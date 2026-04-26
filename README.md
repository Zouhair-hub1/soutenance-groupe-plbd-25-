# 🌿 Robot de Détection de Mauvaises Herbes — PLBD S6

> Projet de fin d'études — Détection automatique de mauvaises herbes par robot mobile via vision artificielle (YOLOv8) et communication WiFi temps réel.

---

## 📸 Résultats de Détection

| Détection simple (59%) | Détections multiples (77% — 94%) |
|:---:|:---:|
| ![Detection 1](detection_1.jpg) | ![Detection 2](detection_2.jpg) |

---

## 🏗️ Architecture du Système

```
┌─────────────────────────────────┐        WiFi (TCP:9999)       ┌──────────────────────────────────┐
│     Raspberry Pi — Robot        │ ──────────────────────────►  │        PC Windows — Serveur       │
│                                 │                               │                                   │
│  📷 Caméra USB (640x480)        │   Envoi frames JPEG           │  🤖 YOLOv8 (50 epochs)            │
│  🔊 Buzzer GPIO 18              │ ◄──────────────────────────── │  🌐 Site Web Flask (port 5000)    │
│  🦾 Servo bras (ID 4)           │   Signal 0/1 détection        │  💾 Sauvegarde screenshots        │
│                                 │                               │  📊 Graphe coordonnées X,Y (cm)   │
└─────────────────────────────────┘                               └──────────────────────────────────┘
```

---

## 📁 Structure du Projet

```
soutenance-groupe-plbd-25-/
│
├── 🤖 robot_client.py        # Code Raspberry Pi — capture + envoi images + buzzer
├── 🌐 web_app.py             # Serveur Flask — réception + analyse YOLOv8 + site web
├── 🏋️ train.py               # Entraînement modèle YOLOv8 sur dataset mauvaises herbes
├── 📺 live_pc.py             # Version live sans site web (test initial)
├── 🔌 pc_serveur.py          # Code test connexion Robot↔PC (première version)
├── 🧠 yolov8n.pt             # Poids pré-entraînés YOLOv8 nano
│
└── templates/
    └── 🖥️ index.html         # Interface web — live stream + détections + graphe
```

---

## 🔧 Matériel Utilisé

| Composant | Détails |
|-----------|---------|
| **Robot** | Adeept PiCar Pro V2 — 4 roues |
| **Ordinateur embarqué** | Raspberry Pi (kit9) |
| **Caméra** | USB 640×480 |
| **Buzzer** | TonalBuzzer — GPIO 18 |
| **Bras robot** | Servo moteur — ID 4 — PCA9685 (0x5f) |
| **PC** | Windows — Flask + YOLOv8 |
| **Communication** | WiFi TCP Socket — Port 9999 |

---

## 🧠 Modèle YOLOv8

| Paramètre | Valeur |
|-----------|--------|
| **Architecture** | YOLOv8 Nano |
| **Dataset** | Mauvaises herbes (Roboflow) |
| **Epochs** | 50 |
| **Image size** | 640×640 |
| **Device** | CPU |
| **Confiance** | 0.5 |
| **Classe** | `Weeds` |

### 📊 Résultats d'entraînement
```
Class    Images  Instances  Box(P    R    mAP50  mAP50-95)
all      50      148        0.615    0.07   0.0306
```

---

## 🌐 Site Web Flask

Le site web est accessible depuis **n'importe quel appareil** sur le réseau WiFi :

```
http://localhost:5000          → sur le PC
http://172.22.3.11:5000        → sur téléphone/tablette
```

### Fonctionnalités du site :
- 📺 **Live stream** — vidéo en temps réel avec boxes YOLOv8
- 📸 **Screenshots** — images avec zones rouges quand mauvaise herbe détectée
- 📊 **Graphe 2D** — coordonnées X,Y en cm de chaque détection
- 💡 **Conseils** — "Le robot va vers X=Xcm, Y=Ycm pour arracher la mauvaise herbe"

---

## 🚀 Installation & Lancement

### Prérequis PC
```bash
pip install ultralytics flask opencv-python numpy
```

### Prérequis Raspberry Pi
```bash
pip install opencv-python gpiozero
```

### Lancement

**1. Entraîner le modèle (une seule fois) :**
```bash
python train.py
```

**2. Lancer le serveur PC :**
```bash
python web_app.py
```

**3. Lancer le robot (Raspberry Pi) :**
```bash
sudo python3 robot_client.py
```

**4. Ouvrir le site web :**
```
http://localhost:5000
```

---

## ⚙️ Fonctionnement

```
1. Robot démarre → caméra s'ouvre
2. Toutes les 0.1s → frame capturée et envoyée au PC via WiFi
3. PC analyse la frame avec YOLOv8
4. Si mauvaise herbe détectée (conf > 50%) :
   ├── Screenshot sauvegardé avec zones ROUGES
   ├── Coordonnées X,Y calculées en cm
   ├── Signal "1" envoyé au robot
   └── Robot → Buzzer sonne (note C4, 1 seconde)
5. Site web mis à jour automatiquement toutes les 2 secondes
```

---

## 📐 Conversion Pixels → Centimètres

La caméra est à **20 cm du sol**. La conversion est calculée selon le champ de vision :

```
Largeur réelle visible  = 23.0 cm
Hauteur réelle visible  = 17.0 cm

X_cm = (pixel_x / 640) × 23.0
Y_cm = (pixel_y / 480) × 17.0
```

---

## 📂 Dossiers de Sauvegarde

| Dossier | Contenu |
|---------|---------|
| `C:\Users\Zouhire\Desktop\live robot` | Screenshots avec zones rouges |
| `C:\Users\Zouhire\Desktop\lbd resultats` | Résultats d'analyse |
| `C:\Users\Zouhire\Desktop\plbd mauvaise herbe` | Dataset + modèles entraînés |

---

## 👥 Équipe

Projet réalisé dans le cadre de la **soutenance PLBD S6**

---

## 📄 Licence

MIT License — Libre d'utilisation pour des fins éducatives.
