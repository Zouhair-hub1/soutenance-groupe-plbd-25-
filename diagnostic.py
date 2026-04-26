from ultralytics import YOLO
import cv2
import os

MODEL_PATH = r'C:\Users\Zouhire\Desktop\plbd mauvaise herbe\experience_2\weights\best.pt'
IMAGE_TEST = r'C:\Users\Zouhire\Desktop\tst lbd'

model = YOLO(MODEL_PATH)

# Afficher les classes du modèle
print(f"📋 Classes du modèle : {model.names}")

fichiers = [f for f in os.listdir(IMAGE_TEST) if f.endswith(('.jpg', '.jpeg', '.png'))]

for fichier in fichiers[:3]:
    chemin = os.path.join(IMAGE_TEST, fichier)
    
    # Baisser le seuil de confiance à 10% pour voir TOUT
    results = model(chemin, conf=0.1, verbose=True)
    detections = results[0].boxes
    
    print(f"\n🖼️ {fichier}")
    print(f"   → {len(detections)} détection(s)")
    
    if len(detections) > 0:
        for box in detections:
            print(f"   → Confiance : {box.conf[0]:.2f} | Classe : {model.names[int(box.cls[0])]}")