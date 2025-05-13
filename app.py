# app.py
from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for
import os
import json
from detector import HumanMovementDetector, runtime_logs

app = Flask(__name__)
SAVE_DIR = "static/saves"
VIDEO_DIR = "static/videos"
FRAME_PATH = "static/current_frame.jpg"

os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

# No default instance yet
detector = None

@app.route("/")
def home():
    video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith((".mp4", ".avi"))]
    running = detector.running if detector else False
    return render_template("index.html", running=running, video_files=video_files)

@app.route("/start", methods=["POST"])
def start_detection():
    global detector

    data = request.form
    email_alert_enabled = data.get("enable_email") == "on"
    email = data.get("email") if email_alert_enabled else None
    filename = data.get("filename")

    video_path = os.path.join(VIDEO_DIR, filename)
    if not os.path.isfile(video_path):
        runtime_logs.append(f"[ERROR] File not found: {video_path}")
        return redirect(url_for("home"))

    if detector and detector.running:
        detector.stop()
    detector = HumanMovementDetector(video_source=video_path)
    detector.start(email=email)

    return redirect(url_for("home"))

@app.route("/stop", methods=["POST"])
def stop_detection():
    global detector
    if detector:
        detector.stop()
    return redirect(url_for("home"))

@app.route("/status", methods=["GET"])
def status():
    running = detector.running if detector else False
    return jsonify({"running": running})

@app.route("/logs")
def list_logs():
    logs = []
    for filename in os.listdir(SAVE_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(SAVE_DIR, filename), "r") as f:
                data = json.load(f)
                logs.append(data)
    return jsonify(sorted(logs, key=lambda x: x["timestamp"], reverse=True))

@app.route("/logs/action-required")
def logs_action_required():
    flagged = []
    for filename in os.listdir(SAVE_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(SAVE_DIR, filename), "r") as f:
                data = json.load(f)
                if data.get("analysis", {}).get("action_required"):
                    flagged.append(data)
    return jsonify(sorted(flagged, key=lambda x: x["timestamp"], reverse=True))

@app.route("/logs/live")
def live_logs():
    return jsonify(runtime_logs[-100:])

@app.route("/images/<filename>")
def get_image(filename):
    return send_from_directory(SAVE_DIR, filename)

@app.route("/reset", methods=["POST"])
def reset_logs():
    for f in os.listdir(SAVE_DIR):
        os.remove(os.path.join(SAVE_DIR, f))
    if os.path.exists(FRAME_PATH):
        os.remove(FRAME_PATH)
    runtime_logs.append("[RESET] Logs and screenshots cleared.")
    return redirect(url_for("home"))

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)