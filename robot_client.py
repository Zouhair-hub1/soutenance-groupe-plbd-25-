import socket
import struct
import cv2
import time
import threading
import sys

sys.path.append('/home/kit9/.local/share/Trash/files/Adeept_PiCar-Pro-V2.0-20250928/Adeept_PiCar-Pro-V2.0-20250928/Code/Adeept_PiCar-Pro/Server')

from gpiozero import TonalBuzzer

PC_IP = '172.22.3.11'
PORT  = 9999

buzzer = TonalBuzzer(18)

def buzzer_son():
    buzzer.play("C4")
    time.sleep(1)
    buzzer.stop()

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((PC_IP, PORT))
print("Connecte au PC")

camera = cv2.VideoCapture(0)
camera.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)
time.sleep(1)
print("Live en cours...")

try:
    while True:
        ret, frame = camera.read()
        if not ret:
            continue

        _, buffer = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
        data = buffer.tobytes()

        client.sendall(struct.pack('>I', len(data)))
        client.sendall(data)

        reponse = client.recv(1)
        if reponse == b'1':
            threading.Thread(target=buzzer_son).start()

        time.sleep(0.1)

except KeyboardInterrupt:
    print("Arret")

camera.release()
client.close()