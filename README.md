# 🌿 Robot de Détection de Mauvaises Herbes — PLBD S6

> Détection automatique de mauvaises herbes par robot mobile via vision artificielle (YOLOv8) et communication WiFi temps réel.

---

## 📸 Résultats de Détection

| Détection dans le site web | Détections multiples |
|:---:|:---:|
| ![Detection site](detection_site.jpg) | ![Detection multiple](detection_multiple.jpg) |

---

## 📱 QR Code — Accès au Site Web

<p align="center">
  <img src="qrcode_site.png" width="200"/>
  <br/>
  <b>Scanner pour accéder au site : http://172.22.3.11:5000</b>
</p>

---

## 🏗️ Architecture du Système
┌──────────────────────────┐     WiFi TCP:9999      ┌──────────────────────────┐
│   Raspberry Pi — Robot   │ ──────────────────────► │    PC Windows — Serveur  │
│                          │                         │                          │
│  📷 Caméra USB 640x480   │   Envoi frames JPEG     │  🤖 YOLOv8 50 epochs     │
│  🔊 Buzzer GPIO 18       │ ◄────────────────────── │  🌐 Flask port 5000      │
│                          │   Signal 0/1            │  💾 Screenshots rouges   │
└──────────────────────────┘                         └──────────────────────────┘
---

## 📁 Structure du Projet
soutenance-groupe-plbd-25-/
├── robot_client.py     # Raspberry Pi — capture + envoi + buzzer
├── web_app.py          # PC — Flask + YOLOv8 + site web
├── train.py            # Entraînement YOLOv8
├── live_pc.py          # Test live sans site web
├── pc_serveur.py       # Test connexion Robot-PC
├── yolov8n.pt          # Poids YOLOv8 nano
└── templates/
└── index.html      # Interface web
---

## 🔧 Matériel Utilisé

| Composant | Détails |
|-----------|---------|
| **Robot** | Adeept PiCar Pro V2 |
| **Ordinateur embarqué** | Raspberry Pi |
| **Caméra** | USB 640×480 |
| **Buzzer** | TonalBuzzer GPIO 18 |
| **PC** | Windows Flask + YOLOv8 |
| **Communication** | WiFi TCP Port 9999 |

---

## 🧠 Modèle YOLOv8

| Paramètre | Valeur |
|-----------|--------|
| **Architecture** | YOLOv8 Nano |
| **Dataset** | Mauvaises herbes Roboflow |
| **Epochs** | 50 |
| **Image size** | 640×640 |
| **Confiance** | 0.5 |
| **Classe** | Weeds |

---

## 🌐 Site Web Flask
http://localhost:5000         → PC
http://172.22.3.11:5000       → Téléphone / Tablette
Fonctionnalités :
- 📺 Live stream avec boxes YOLOv8
- 📸 Screenshots zones rouges
- 📊 Graphe X,Y en cm
- 💡 Conseils position mauvaise herbe

---

## 🚀 Lancement

**PC :**
```bash
pip install ultralytics flask opencv-python numpy
python web_app.py
```

**Raspberry Pi :**
```bash
pip install opencv-python gpiozero
sudo python3 robot_client.py
```

---

## ⚙️ Fonctionnement
Robot capture une frame toutes les 0.1s
Frame envoyée au PC via WiFi
YOLOv8 analyse (conf > 50%)
Si mauvaise herbe :
→ Screenshot zones rouges sauvegardé
→ Coordonnées X,Y en cm calculées
→ Signal 1 envoyé au robot
→ Buzzer sonne (C4, 1 seconde)
Site web mis à jour toutes les 2 secondes
---

## 📐 Coordonnées en cm
Caméra à 20 cm du sol
X_cm = (pixel_x / 640) × 23.0
Y_cm = (pixel_y / 480) × 17.0
---

## 👥 Équipe — PLBD 25 

---

