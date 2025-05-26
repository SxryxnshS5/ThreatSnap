# 🔐 ThreatSnap

**ThreatSnap** is a real-time threat monitoring system that detects dangerous human activity from CCTV footage. Built with Flask, YOLOv8, and OpenAI's GPT-4o, it automatically analyzes human movement in video files and sends email alerts when suspicious behavior is detected.

> 🏆 Built for AmpliCode Hackathon 2025 under the **Security & Online Safety** track.
> 🚀 Deployed on [Railway](https://railway.app)

---

## 📌 About the Project

ThreatSnap focuses primarily on **backend technology** — combining real-time object detection, contextual AI analysis, and intelligent alerting — to build a meaningful safety solution. While a basic frontend dashboard is included for demonstration purposes, the **core innovation lies in the detection and analysis pipeline**.

The backend system:

* Uses **YOLOv8** to detect humans and movements in CCTV-like footage
* Applies **OpenAI GPT-4o** to interpret human posture, weapon presence, and threat level
* Sends **email alerts** with visual + textual logs when necessary
* Organizes all detections for review and displays them in a structured log format
* Categorizes alerts into **threat levels**: Low, Medium, High, and Critical
* Includes **privacy masking** to blur non-relevant areas in the footage
* Tracks individual persons across frames for enhanced analysis
* Provides **advanced analytics** and supports **external alarm system** connectivity for real-time physical response

---

## 💡 Key Features

* 📂 Monitors **existing video files** for human movement
* 🤖 Uses **GPT-4o** to analyze screenshots for dangerous behavior
* ✉️ Sends detailed email alerts with images and structured threat logs
* 🔒 Supports **privacy masking** and **multi-level threat detection**
* 🧍‍♂️ **Tracks people** across multiple frames for consistency
* 📈 Provides **advanced analytics** and visual logs
* 📢 Supports **external alarm system triggers**
* 📁 Stores logs and reports for post-event investigation
* ⚙️ Backend-driven — minimal dependencies and frontend bloat

---

## 📽 Intended Use

ThreatSnap is designed to run locally on systems such as:

* Schools
* Retail environments
* Residential security systems

It currently processes local video files and requires internet for AI-based analysis, but future versions will support **offline AI models** for complete local operation.

---

## 🧪 How It Works

1. Select a video file (placed in `/static/videos/`)
2. Optionally enable email alerts
3. Click **Start Monitoring**
4. The system:

   * Detects human movement and extracts frames
   * Applies AI for scene interpretation and threat assessment
   * Sends email alerts for threats (if enabled)
   * Logs activity with timestamps, labels, and screenshots

Logs are accessible at:

* `/logs`: General activity logs
* `/logs/action-required`: Only critical or high-risk events

---

## 🧰 Technical Overview

* **Backend**: Python (Flask)
* **Frontend**: HTML/CSS/JavaScript (lightweight dashboard)
* **Detection**: Computer vision with YOLOv8
* **AI Analysis**: GPT-4o via OpenAI API
* **Tracking**: Person ID consistency across frames
* **Data Handling**: Structured logs and visual evidence
* **Connectivity**: External alarm integration (planned)

---

## 🚧 Future Improvements

* Optimize detector for more efficient frame sampling
* Reduce false positives with custom ML models
* Integrate **real-time CCTV stream monitoring**
* Build **mobile app** for remote alerts and control
* Implement **user accounts** and **role-based access control**
* Support **fully offline AI models** for private deployments

---


## 🧱 Project Structure

```
ThreatSnap/
├── app.py              # Flask routes and control logic
├── detector.py         # Movement + frame capture + alert trigger
├── processor.py        # OpenAI GPT-4o analysis
├── emailer.py          # Email alert system
├── templates/
│   ├── index.html      # Demo UI for hackathon
│   └── analytics.html  # Threat analytics dashboard
├── static/
│   ├── saves/          # Captured screenshots + logs
│   ├── videos/         # Uploaded video files
│   ├── style.css       # Custom CSS styles
│   └── script.js       # JavaScript for UI interactions
├── .env                # Environment variables
```

---

## 🌐 API Endpoints

| Endpoint                    | Method | Description                                                                 |
|-----------------------------|--------|-----------------------------------------------------------------------------|
| `/`                         | GET    | Main dashboard with UI                                                      |
| `/start`                    | POST   | Start monitoring (JSON: `{ email, filename, privacy_blur?, zones? }`)      |
| `/stop`                     | POST   | Stop current video monitoring                                               |
| `/reset`                    | POST   | Delete all logs and screenshots                                             |
| `/status`                   | GET    | Return current monitoring status                                            |
| `/current_frame`            | GET    | Get the latest processed frame (image)                                     |
| `/save-zones`              | POST   | Set or update monitoring zones (JSON: `{ zones: [...] }`)                  |
| `/logs`                     | GET    | Return all saved detection logs (JSON)                                     |
| `/logs/action-required`     | GET    | Return only logs flagged as `action_required = true`                       |
| `/logs/live`                | GET    | Return recent in-memory runtime logs (for terminal-style viewing)          |
| `/analytics`                | GET    | Show analytical dashboard with stats and recent threats                    |
| `/images/<filename>`        | GET    | Serve saved image or log file from `/static/saves/`                        |
| `/system/add-camera`        | POST   | Add a new camera source (JSON: `{ camera_id, source }`)                    |
| `/system/start-all`         | POST   | Start monitoring across all registered camera sources                      |
| `/system/stop-all`          | POST   | Stop monitoring all active cameras                                         |

---

## 🛠 Setup Instructions

### 1. Clone and set up virtualenv

```bash
git clone https://github.com/SxryxnshS5/ThreatSnap.git
cd ThreatSnap
python -m venv venv
source venv/bin/activate  # Windows: .\venv\Scripts\activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create `.env` file

```env
OPENAI_API_KEY=your-openai-api-key
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

### 4. Run the app

```bash
python app.py
```

Then open:  
`http://localhost:8080`

---

## 📽 Demo Video

> “Soon”

🎬 [Demo Link – coming soon]

---

## 📃 License

MIT License © 2025 [Suryansh]

---

## 👏 Credits

- Built by [@SxryxnshS5](https://github.com/SxryxnshS5)
- YOLOv8 by [Ultralytics](https://github.com/ultralytics/ultralytics)
- GPT-4o API by [OpenAI](https://openai.com/gpt-4o)
