# app.py
from flask import Flask, jsonify, send_from_directory
import os
import json
from detector import HumanMovementDetector

app = Flask(__name__)
detector = HumanMovementDetector()

SCREENSHOT_DIR = "static/screenshots"

@app.route("/start", methods=["POST"])
def start_detection():
    detector.start()
    return jsonify({"status": "started"})

@app.route("/stop", methods=["POST"])
def stop_detection():
    detector.stop()
    return jsonify({"status": "stopped"})

@app.route("/status", methods=["GET"])
def status():
    return jsonify({"running": detector.running})

@app.route("/logs", methods=["GET"])
def list_logs():
    logs = []
    for filename in os.listdir(SCREENSHOT_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(SCREENSHOT_DIR, filename), "r") as f:
                data = json.load(f)
                logs.append(data)
    return jsonify(sorted(logs, key=lambda x: x["timestamp"], reverse=True))

@app.route("/images/<filename>")
def get_image(filename):
    return send_from_directory(SCREENSHOT_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True)
