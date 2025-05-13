# detector.py
import cv2
import time
import threading
import math
import os
import json
from datetime import datetime
from ultralytics import YOLO
from processor import process_screenshot
from emailer import send_alert_email

runtime_logs = []

def log(msg):
    print(msg)
    runtime_logs.append(msg)

class HumanMovementDetector:
    def __init__(self, video_source):
        self.video_source = video_source
        self.model = YOLO("yolov8n.pt")
        self.running = False
        self.thread = None
        self.prev_boxes = []
        self.cooldown = 5  # seconds
        self.last_trigger_video_time = -float('inf')
        self.user_email = None
        self.output_dir = "static/saves"
        os.makedirs(self.output_dir, exist_ok=True)

    def euclidean_distance(self, a, b):
        return math.sqrt((a[0] - b[0])**2 + (a[1] - b[1])**2)

    def extract_person_boxes(self, results):
        boxes = []
        for r in results:
            for box in r.boxes:
                if int(box.cls[0]) == 0:
                    x1, y1, x2, y2 = box.xyxy[0].tolist()
                    cx = (x1 + x2) / 2
                    cy = (y1 + y2) / 2
                    boxes.append((cx, cy))
        return boxes

    def has_movement(self, prev_boxes, curr_boxes, threshold=40):
        if not prev_boxes or not curr_boxes:
            return False
        for cb in curr_boxes:
            closest = min((self.euclidean_distance(cb, pb) for pb in prev_boxes), default=1e9)
            if closest > threshold:
                return True
        return False

    def _detect_loop(self):
        cap = cv2.VideoCapture(self.video_source)
        log(f"[STARTED] Monitoring source: {self.video_source}")
        while self.running and cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                log("[VIDEO END] Stopping monitoring as video has ended.")
                self.running = False
                break

            current_video_time = cap.get(cv2.CAP_PROP_POS_MSEC) / 1000
            if current_video_time - self.last_trigger_video_time < self.cooldown:
                continue  # Skip frame due to cooldown

            results = self.model(frame)
            curr_boxes = self.extract_person_boxes(results)

            if self.has_movement(self.prev_boxes, curr_boxes):
                timestamp_str = datetime.fromtimestamp(time.time()).strftime("%Y%m%d_%H%M%S")
                image_filename = f"{timestamp_str}.jpg"
                image_path = os.path.join(self.output_dir, image_filename)
                cv2.imwrite(image_path, frame)

                analysis = process_screenshot(image_path)
                log_filename = f"{timestamp_str}.json"
                log_path = os.path.join(self.output_dir, log_filename)
                with open(log_path, 'w') as log_file:
                    json.dump({
                        "timestamp": timestamp_str,
                        "image": image_filename,
                        "analysis": analysis
                    }, log_file, indent=2)

                log(f"[LOGGED] {image_filename} | Action: {analysis.get('action_required')} | Danger: {analysis.get('danger')}")

                if analysis.get("action_required"):
                    self.last_trigger_video_time = current_video_time

                    if self.user_email:
                        subject = "🔴 ThreatSnap Alert – Action Required"
                        body = (
                            f"Timestamp: {analysis['timestamp']}\n\n"
                            f"Danger: {analysis.get('danger', 'N/A')}\n\n"
                            f"Recommended Action: Investigate immediately.\n\n"
                            "See attached image and log file for more information."
                        )
                        send_alert_email(
                            recipient=self.user_email,
                            subject=subject,
                            body=body,
                            attachments=[image_path, log_path]
                        )

            self.prev_boxes = curr_boxes
            time.sleep(0.05)

        cap.release()
        log("[STOPPED] Monitoring session ended.")

    def start(self, email=None):
        if not self.running:
            self.running = True
            self.user_email = email
            self.thread = threading.Thread(target=self._detect_loop)
            self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()
            self.thread = None