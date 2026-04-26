from flask import Flask, Response, render_template, jsonify
import cv2
import numpy as np
import socket
import struct
import threading
import os
from ultralytics import YOLO
from datetime import datetime
import time

app = Flask(__name__)

LIVE_DIR   = r'C:\Users\Zouhire\Desktop\live robot'
MODEL_PATH = r'C:\Users\Zouhire\Desktop\plbd mauvaise herbe\experience_5\weights\best.pt'
HOST = '0.0.0.0'
PORT = 9999

os.makedirs(LIVE_DIR, exist_ok=True)

FRAME_W = 640
FRAME_H = 480
REAL_W_CM = 23.0
REAL_H_CM = 17.0

def pixels_to_cm(px, py):
    cx_cm = round((px / FRAME_W) * REAL_W_CM, 1)
    cy_cm = round((py / FRAME_H) * REAL_H_CM, 1)
    return cx_cm, cy_cm

current_frame = None
detections_list = []
compteur = 1
derniere_detection = 0
frame_lock = threading.Lock()

print("Chargement du modele YOLOv8...")
model = YOLO(MODEL_PATH)
print("Modele charge !")

def recevoir_frames():
    global current_frame, detections_list, compteur, derniere_detection

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((HOST, PORT))
    server.listen(1)
    print("En attente du robot...")

    conn, addr = server.accept()
    print(f"Robot connecte : {addr}")

    while True:
        try:
            raw_size = conn.recv(4)
            if not raw_size:
                break
            size = struct.unpack('>I', raw_size)[0]

            data = b''
            while len(data) < size:
                packet = conn.recv(4096)
                if not packet:
                    break
                data += packet

            img_array = np.frombuffer(data, dtype=np.uint8)
            frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

            if frame is None:
                conn.sendall(b'0')
                continue

            results = model(frame, conf=0.5, verbose=False)
            boxes = results[0].boxes
            annotated = results[0].plot()

            with frame_lock:
                current_frame = annotated.copy()

            if len(boxes) > 0 and (time.time() - derniere_detection > 3):
                coords = []
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    box_area = (x2-x1) * (y2-y1)
                    if box_area > FRAME_W * FRAME_H * 0.7:
                        continue
                    px = int((x1 + x2) / 2)
                    py = int((y1 + y2) / 2)
                    cx_cm, cy_cm = pixels_to_cm(px, py)
                    conf = float(box.conf[0])
                    coords.append({
                        'x_cm': cx_cm,
                        'y_cm': cy_cm,
                        'conf': round(conf * 100)
                    })

                if not coords:
                    conn.sendall(b'0')
                    continue

                screenshot_frame = frame.copy()
                overlay = screenshot_frame.copy()
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)
                    box_area = (x2-x1)*(y2-y1)
                    if box_area > FRAME_W * FRAME_H * 0.7:
                        continue
                    cv2.rectangle(overlay, (x1,y1), (x2,y2), (0,0,255), -1)
                cv2.addWeighted(overlay, 0.4, screenshot_frame, 0.6, 0, screenshot_frame)
                for box in boxes:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    x1,y1,x2,y2 = int(x1),int(y1),int(x2),int(y2)
                    box_area = (x2-x1)*(y2-y1)
                    if box_area > FRAME_W * FRAME_H * 0.7:
                        continue
                    conf = float(box.conf[0])
                    cv2.rectangle(screenshot_frame, (x1,y1), (x2,y2), (0,0,255), 3)
                    cv2.putText(screenshot_frame,
                                f"Mauvaise herbe {conf:.0%}",
                                (x1, y1-10),
                                cv2.FONT_HERSHEY_SIMPLEX,
                                0.6, (0,0,255), 2)

                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nom = f"live_{compteur:03d}_{timestamp}.jpg"
                cv2.imwrite(os.path.join(LIVE_DIR, nom), screenshot_frame)

                detection = {
                    'id': compteur,
                    'image': nom,
                    'timestamp': datetime.now().strftime("%H:%M:%S"),
                    'coords': coords,
                    'conseil': f"Le robot va vers X={coords[0]['x_cm']}cm, Y={coords[0]['y_cm']}cm pour arracher la mauvaise herbe"
                }
                detections_list.insert(0, detection)
                if len(detections_list) > 20:
                    detections_list.pop()

                compteur += 1
                derniere_detection = time.time()
                conn.sendall(b'1')
            else:
                conn.sendall(b'0')

        except Exception as e:
            print(f"Erreur : {e}")
            break

def generate_stream():
    global current_frame
    while True:
        with frame_lock:
            frame = current_frame
        if frame is None:
            time.sleep(0.1)
            continue
        _, buffer = cv2.imencode('.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' +
               buffer.tobytes() + b'\r\n')
        time.sleep(0.05)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_stream(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/detections')
def get_detections():
    return jsonify(detections_list)

@app.route('/screenshot/<nom>')
def screenshot(nom):
    chemin = os.path.join(LIVE_DIR, nom)
    with open(chemin, 'rb') as f:
        return Response(f.read(), mimetype='image/jpeg')

if __name__ == '__main__':
    t = threading.Thread(target=recevoir_frames)
    t.daemon = True
    t.start()
    app.run(host='0.0.0.0', port=5000, debug=False)