from flask import Flask, request, jsonify, send_from_directory, render_template, redirect, url_for
import os
import json
import shutil
from detector import HumanMovementDetector, runtime_logs

app = Flask(__name__)
SAVE_DIR = "static/saves"
VIDEO_DIR = "static/videos"
FRAME_PATH = "static/current_frame.jpg"

os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

# Default detector instance
detector = HumanMovementDetector()

@app.route("/")
def home():
    video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith((".mp4", ".avi"))]
    return render_template("index.html", running=detector.running, video_files=video_files)

@app.route("/start", methods=["POST"])
def start_detection():
    data = request.form
    email = data.get("email")
    source = data.get("source")
    filename = data.get("filename")

    # Determine video source
    if source == "video":
        video_path = os.path.join(VIDEO_DIR, filename)
        if not os.path.isfile(video_path):
            runtime_logs.append(f"[ERROR] File not found: {video_path}")
            return redirect(url_for("home"))
        video_source = video_path
    else:
        video_source = 0

    global detector
    if detector.running:
        detector.stop()
    detector = HumanMovementDetector(video_source=video_source)
    detector.start(email=email)

    return redirect(url_for("home"))

@app.route("/stop", methods=["POST"])
def stop_detection():
    detector.stop()
    return redirect(url_for("home"))

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"running": detector.running})

@app.route("/logs")
def list_logs():
    logs = []
    for filename in os.listdir(SAVE_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(SAVE_DIR, filename), "r") as f:
                data = json.load(f)
                logs.append(data)
    return jsonify(sorted(logs, key=lambda x: x["timestamp"], reverse=True))

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
    app.run(debug=True)