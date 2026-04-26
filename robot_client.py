import socket
import struct
import cv2
import time
import threading
import sys

sys.path.append('/home/kit9/.local/share/Trash/files/Adeept_PiCar-Pro-V2.0-20250928/Adeept_PiCar-Pro-V2.0-20250928/Code/Adeept_PiCar-Pro/Server')

from gpiozero import TonalBuzzer
from RPIservo import ServoCtrl

PC_IP = '172.22.3.11'
PORT  = 9999

buzzer = TonalBuzzer(18)
sc = ServoCtrl()

def buzzer_son():
    buzzer.play("C4")
    time.sleep(1)
    buzzer.stop()

def mouvement_dents():
    sc.set_angle(4, 135)  # ouvrir
    time.sleep(0.5)
    sc.set_angle(4, 45)   # fermer
    time.sleep(0.5)
    sc.set_angle(4, 90)   # position normale

def action_detection():
    print("Mauvaise herbe detectee ! Buzzer + dents...")
    t1 = threading.Thread(target=buzzer_son)
    t2 = threading.Thread(target=mouvement_dents)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    print("Action terminee !")

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((PC_IP, PORT))
print("Connecte au PC")

camera = cv2.VideoCapture(0)
time.sleep(1)
print("Envoi toutes les 2 secondes...")

try:
    while True:
        ret, frame = camera.read()
        if not ret:
            print("Erreur camera")
            continue

        _, buffer = cv2.imencode('.jpg', frame)
        data = buffer.tobytes()

        client.sendall(struct.pack('>I', len(data)))
        client.sendall(data)

        reponse = client.recv(1)
        if reponse == b'1':
            action_detection()

        time.sleep(2)

except KeyboardInterrupt:
    print("Arret")

camera.release()
client.close()