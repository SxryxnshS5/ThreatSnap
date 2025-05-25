from flask import Flask, request, jsonify, send_from_directory, render_template
import os
import json
import time
import threading
from datetime import datetime, timedelta
from detector import HumanMovementDetector, SecuritySystem, runtime_logs

app = Flask(__name__)
SAVE_DIR = "static/saves"
VIDEO_DIR = "static/videos"
FRAME_PATH = "static/current_frame.jpg"

os.makedirs(SAVE_DIR, exist_ok=True)
os.makedirs(VIDEO_DIR, exist_ok=True)

detector = None
security_system = SecuritySystem()

def cleanup_old_data():
    """Remove data older than the retention period"""
    retention_days = int(os.getenv("DATA_RETENTION_DAYS", 30))
    cutoff_time = datetime.now() - timedelta(days=retention_days)
    
    cleanup_count = 0
    for filename in os.listdir(SAVE_DIR):
        try:
            # Extract timestamp from filename (assuming YYYYMMDD_HHMMSS format)
            if not filename.endswith((".jpg", ".json")):
                continue
                
            file_time_str = filename.split('.')[0]
            file_time = datetime.strptime(file_time_str, "%Y%m%d_%H%M%S")
            
            if file_time < cutoff_time:
                os.remove(os.path.join(SAVE_DIR, filename))
                cleanup_count += 1
        except Exception as e:
            print(f"Error processing file {filename}: {e}")
    
    if cleanup_count > 0:
        runtime_logs.append(f"[CLEANUP] Removed {cleanup_count} expired files")

def start_cleanup_task():
    """Start background task for periodic cleanup"""
    def cleanup_task():
        while True:
            cleanup_old_data()
            time.sleep(86400)  # Run once per day
            
    thread = threading.Thread(target=cleanup_task)
    thread.daemon = True
    thread.start()
    runtime_logs.append("[SYSTEM] Started cleanup background task")

@app.route("/")
def home():
    video_files = [f for f in os.listdir(VIDEO_DIR) if f.endswith((".mp4", ".avi"))]
    running = detector.running if detector else False
    return render_template("index.html", running=running, video_files=video_files)

@app.route("/current_frame")
def current_frame():
    """Return the current frame being processed"""
    if os.path.exists(FRAME_PATH):
        return send_from_directory("static", "current_frame.jpg")
    return jsonify({"error": "No current frame available"}), 404

@app.route("/start", methods=["POST"])
def start_detection():
    global detector
    data = request.get_json()
    email = data.get("email")
    filename = data.get("filename")
    privacy_blur = data.get("privacy_blur", False)
    zones = data.get("zones", [])

    video_path = os.path.join(VIDEO_DIR, filename)
    if not os.path.isfile(video_path):
        runtime_logs.append(f"[ERROR] File not found: {video_path}")
        return jsonify({"status": "error", "message": "Video file not found."}), 400

    if detector and detector.running:
        detector.stop()

    detector = HumanMovementDetector(video_source=video_path)
    
    # Set monitoring zones if provided
    if zones:
        detector.set_monitoring_zones(zones)
        
    detector.start(email=email, privacy_blur=privacy_blur)
    return jsonify({"status": "started", "email": email})

@app.route("/stop", methods=["POST"])
def stop_detection():
    global detector
    if detector:
        detector.stop()
    return jsonify({"status": "stopped"})

@app.route("/reset", methods=["POST"])
def reset_logs():
    for f in os.listdir(SAVE_DIR):
        os.remove(os.path.join(SAVE_DIR, f))
    if os.path.exists(FRAME_PATH):
        os.remove(FRAME_PATH)
    runtime_logs.append("[RESET] Logs and screenshots cleared.")
    return jsonify({"status": "reset"})

@app.route("/save-zones", methods=["POST"])
def save_zones():
    global detector
    data = request.get_json()
    zones = data.get("zones", [])
    
    if detector:
        detector.set_monitoring_zones(zones)
    
    return jsonify({"status": "success", "zones": zones})

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

@app.route("/analytics")
def analytics():
    logs = []
    try:
        # Look for logs in the saves directory
        for filename in os.listdir("static/saves"):
            if filename.endswith(".json"):
                with open(os.path.join("static/saves", filename), "r") as f:
                    log_data = json.load(f)
                    logs.append(log_data)
    except Exception as e:
        print(f"Error loading logs: {e}")

    # Sort logs by timestamp (newest first)
    logs = sorted(logs, key=lambda x: x["timestamp"], reverse=True)
    
    total_alerts = len(logs)
    danger_levels = {"LOW": 0, "MEDIUM": 0, "HIGH": 0, "CRITICAL": 0}
    hourly_breakdown = {}
    weapons_detected = {}
    response_actions = {}
    objects_detected = {}
    
    # Process the logs to extract data for analytics
    for log in logs:
        analysis = log.get("analysis", {})
        
        # Count by danger level
        danger = analysis.get("danger", "LOW")
        danger_levels[danger] = danger_levels.get(danger, 0) + 1
        
        # Group by hour for time analysis (format: YYYYMMDD_HH)
        hour = log["timestamp"][:9]
        hourly_breakdown[hour] = hourly_breakdown.get(hour, 0) + 1
        
        # Count weapons detected
        for weapon in analysis.get("weapons", []):
            weapons_detected[weapon] = weapons_detected.get(weapon, 0) + 1
        
        # Extract profile descriptions for objects detected
        for profile in analysis.get("profiles", []):
            desc = profile.get("description", "Unknown person")
            # Take first part of description to categorize
            parts = desc.split(',')
            if parts:
                key = parts[0].strip()
                objects_detected[key] = objects_detected.get(key, 0) + 1
                
        # Count recommended actions
        if analysis.get("recommended_response"):
            # Extract first sentence for categorization
            response = analysis["recommended_response"].split(".")[0] + "."
            response_actions[response] = response_actions.get(response, 0) + 1
    
    # Include the detailed incidents for the timeline
    detailed_incidents = logs[:20]  # Show only the 20 most recent logs
    
    return render_template(
        "analytics.html",
        total_alerts=total_alerts,
        danger_levels=danger_levels,
        hourly_breakdown=hourly_breakdown,
        weapons_detected=weapons_detected,
        objects_detected=objects_detected,
        action_summary=response_actions,
        detailed_incidents=detailed_incidents
    )

@app.route("/images/<filename>")
def get_image(filename):
    return send_from_directory(SAVE_DIR, filename)

@app.route("/system/add-camera", methods=["POST"])
def add_camera():
    data = request.get_json()
    camera_id = data.get("camera_id")
    source = data.get("source")
    
    if not camera_id or not source:
        return jsonify({"status": "error", "message": "Missing camera ID or source"}), 400
        
    security_system.add_camera(camera_id, source)
    return jsonify({"status": "success", "camera_id": camera_id})

@app.route("/system/start-all", methods=["POST"])
def start_all_cameras():
    data = request.get_json()
    email = data.get("email")
    security_system.start_monitoring(email=email)
    return jsonify({"status": "success"})

@app.route("/system/stop-all", methods=["POST"])
def stop_all_cameras():
    security_system.stop_monitoring()
    return jsonify({"status": "success"})

# Alternative to @app.before_first_request for newer Flask versions
@app.before_request
def before_request_func():
    global cleanup_task_started
    if not getattr(app, 'cleanup_task_started', False):
        app.cleanup_task_started = True
        start_cleanup_task()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=True)