from ultralytics import YOLO
import cv2
import os
import time
import shutil

MODEL_PATH = r'C:\Users\Zouhire\Desktop\plbd mauvaise herbe\experience_3\weights\best.pt'
WATCH_DIR  = r'C:\Users\Zouhire\Desktop\tst lbd'
SAVE_DIR   = r'C:\Users\Zouhire\Desktop\lbd resultats'

os.makedirs(SAVE_DIR, exist_ok=True)

print("⏳ Chargement du modèle...")
model = YOLO(MODEL_PATH)
print("✅ Modèle chargé ! Surveillance du dossier...")

images_traitees = set()

while True:
    fichiers = [f for f in os.listdir(WATCH_DIR) 
                if f.endswith(('.jpg', '.jpeg', '.png'))]

    for fichier in fichiers:
        if fichier in images_traitees:
            continue

        chemin = os.path.join(WATCH_DIR, fichier)
        print(f"\n🔍 Nouvelle image détectée : {fichier}")

        results = model(chemin, verbose=False)
        detections = results[0].boxes

        annotated = results[0].plot()
        save_path = os.path.join(SAVE_DIR, f"resultat_{fichier}")
        cv2.imwrite(save_path, annotated)

        print(f"🌿 {len(detections)} détection(s) → sauvegardé dans lbd resultats")
        images_traitees.add(fichier)

    time.sleep(1)  # vérifie chaque seconde