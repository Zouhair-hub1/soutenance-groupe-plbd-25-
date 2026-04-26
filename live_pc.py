import socket
import struct
import cv2
import numpy as np
import os
from ultralytics import YOLO
from datetime import datetime

HOST = '0.0.0.0'
PORT = 9999

LIVE_DIR = r'C:\Users\Zouhire\Desktop\live robot'
MODEL_PATH = r'C:\Users\Zouhire\Desktop\plbd mauvaise herbe\experience_5\weights\best.pt'

os.makedirs(LIVE_DIR, exist_ok=True)

print("Chargement du modele YOLOv8...")
model = YOLO(MODEL_PATH)
print("Modele charge ! Lancement du live...")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)

print("En attente du robot...")
conn, addr = server.accept()
print(f"Robot connecte : {addr}")

compteur = 1
derniere_detection = 0  # timestamp derniere detection

while True:
    try:
        # Recevoir frame
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

        # Analyser avec YOLOv8
        results = model(frame, conf=0.5, verbose=False)
        detections = results[0].boxes
        annotated = results[0].plot()  # frame avec boxes

        # Afficher le live
        cv2.imshow("Live Robot - Detection Mauvaises Herbes", annotated)
        cv2.waitKey(1)

        now = time.time() if False else __import__('time').time()

        if len(detections) > 0:
            # Screenshot seulement si 3 secondes depuis derniere detection
            if __import__('time').time() - derniere_detection > 3:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                nom = f"live_{compteur:03d}_{timestamp}.jpg"
                cv2.imwrite(os.path.join(LIVE_DIR, nom), annotated)
                print(f"DETECTION : {len(detections)} mauvaise(s) herbe(s) -> screenshot {nom}")
                compteur += 1
                derniere_detection = __import__('time').time()

            conn.sendall(b'1')
        else:
            conn.sendall(b'0')

    except Exception as e:
        print(f"Erreur : {e}")
        break

conn.close()
cv2.destroyAllWindows()
print("Connexion fermee")