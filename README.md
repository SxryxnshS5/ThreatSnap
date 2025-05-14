# 🔐 ThreatSnap

**ThreatSnap** is a real-time threat monitoring system that detects dangerous human activity from CCTV footage. Built with Flask, YOLOv8, and OpenAI's GPT-4o, it automatically analyzes human movement in video files and sends email alerts when suspicious behavior is detected.

> 🏆 Built for AmpliCode Hackathon 2025 under the **Security & Online Safety** track.  
> 🚀 Deployed on [Railway](https://railway.app)

---

## 📌 About the Project

ThreatSnap focuses primarily on **backend technology** — combining real-time object detection, contextual AI analysis, and intelligent alerting — to build a meaningful safety solution. While a basic frontend dashboard is included for demonstration purposes, the **core innovation lies in the detection and analysis pipeline**.

The backend system:
- Uses **YOLOv8** to detect humans and movements in CCTV-like footage
- Applies **OpenAI GPT-4o** to interpret human posture, weapon presence, and threat level
- Sends **email alerts** with visual + textual logs when necessary
- Organizes all detections for review

---

## 💡 Key Features

- 📂 Monitors **existing video files** for human movement
- 🤖 Uses **GPT-4o** to analyze screenshots for dangerous behavior
- ✉️ Sends detailed email alerts with image and threat log
- 📁 Stores logs and analysis reports in a structured format
- ⚙️ Backend-driven — minimal dependencies and frontend bloat

---

## 📽 Intended Use

ThreatSnap is designed to run **offline on local systems**, including:

- Schools
- Retail environments
- Residential security systems

The web interface exists **only for demonstration**. In the future, ThreatSnap will be:

- 🔐 Integrated directly into **CCTV hardware** or video surveillance pipelines
- 💻 Available as a **desktop monitoring tool**
- 📱 Possibly offered as a **mobile app** with local + cloud options
- 👥 Equipped with **user accounts** and role-based access control

---

## 🧪 How It Works

1. Upload a sample video to `/static/videos/`
2. Select the file from the dropdown in the UI
3. (Optionally) enter an email address for alert notifications
4. Click **Start Monitoring**
5. The backend:
   - Detects human movement
   - Captures frames
   - Analyzes them using OpenAI
   - Sends email if action is required
6. All logs are viewable from `/logs` and `/logs/action-required`

---

## 🧱 Project Structure

```
ThreatSnap/
├── app.py              # Flask routes and control logic
├── detector.py         # Movement + frame capture + alert trigger
├── processor.py        # OpenAI GPT-4o analysis
├── emailer.py          # Email alert system
├── templates/
│   └── index.html      # Demo UI for hackathon
├── static/
│   ├── saves/          # Captured screenshots + logs
│   └── videos/         # Uploaded video files
├── .env                # Environment variables
```

---

## 🌐 API Endpoints

| Endpoint                  | Method | Description                                       |
|---------------------------|--------|---------------------------------------------------|
| `/`                       | GET    | Main dashboard with UI                            |
| `/start`                  | POST   | Start monitoring (JSON: `{ email, filename }`)    |
| `/stop`                   | POST   | Stop monitoring                                   |
| `/reset`                  | POST   | Delete all logs and screenshots                   |
| `/status`                 | GET    | Return current monitoring state                   |
| `/logs`                   | GET    | Return all saved logs (JSON)                      |
| `/logs/action-required`   | GET    | Return logs where `action_required = true`        |
| `/logs/live`              | GET    | Return in-memory runtime logs (terminal-style)    |
| `/images/<filename>`      | GET    | Serve saved images or log files                   |

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

## 📋 Future Roadmap

- 🎥 Support for **live CCTV camera feeds**
- 👥 **User accounts** and role-based access
- ☁️ Hybrid/local **cloud data sync**
- 📱 Desktop + mobile app versions for deployment

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
