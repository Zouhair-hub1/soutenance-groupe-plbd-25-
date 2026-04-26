import socket
import struct
import cv2
import numpy as np
import os
from ultralytics import YOLO
from datetime import datetime

HOST = '0.0.0.0'
PORT = 9999

SAVE_DIR   = r'C:\Users\Zouhire\Desktop\lbd resultats'
MODEL_PATH = r'C:\Users\Zouhire\Desktop\plbd mauvaise herbe\experience_3\weights\best.pt'

os.makedirs(SAVE_DIR, exist_ok=True)

print("Chargement du modele YOLOv8...")
model = YOLO(MODEL_PATH)
print("Modele charge !")

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen(1)

print("Serveur en attente de connexion...")

conn, addr = server.accept()
print(f"Robot connecte depuis : {addr}")

compteur = 1

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

        results = model(frame, conf=0.6, verbose=False)
        detections = results[0].boxes

        if len(detections) > 0:
            annotated = results[0].plot()
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nom = f"resultat_{compteur:03d}_{timestamp}.jpg"
            cv2.imwrite(os.path.join(SAVE_DIR, nom), annotated)
            print(f"DETECTION : {len(detections)} mauvaise(s) herbe(s) -> {nom}")
            compteur += 1
            conn.sendall(b'1')
        else:
            print("Aucune detection")
            conn.sendall(b'0')

    except Exception as e:
        print(f"Erreur : {e}")
        break

conn.close()
print("Connexion fermee")