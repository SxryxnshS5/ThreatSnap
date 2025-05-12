from flask import Flask, request, jsonify, send_from_directory
import os
import json
from detector import HumanMovementDetector

app = Flask(__name__)
detector = HumanMovementDetector()

SAVE_DIR = "static/saves"

@app.route("/start", methods=["POST"])
def start_detection():
    data = request.get_json()
    email = data.get("email") if data else None
    detector.start(email=email)
    return jsonify({"status": "started", "email": email})

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
    for filename in os.listdir(SAVE_DIR):
        if filename.endswith(".json"):
            with open(os.path.join(SAVE_DIR, filename), "r") as f:
                data = json.load(f)
                logs.append(data)
    return jsonify(sorted(logs, key=lambda x: x["timestamp"], reverse=True))

@app.route("/images/<filename>")
def get_image(filename):
    return send_from_directory(SAVE_DIR, filename)

if __name__ == "__main__":
    app.run(debug=True)
