import os
import time
import base64
import json
import re
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv, find_dotenv

# Load environment variables early
load_dotenv(find_dotenv())
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

# Initialize OpenAI client
client = OpenAI(api_key=OPENAI_API_KEY)

def process_screenshot(image_path):
    """
    Analyzes the given image using GPT-4o to detect humans,
    potential weapons, danger level, and whether action is required.
    Always returns a consistent structure.
    """
    timestamp = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    print(f"[PROCESSING] {image_path}")

    try:
        # Prepare the image as base64
        image_base64 = _to_base64(image_path)

        # Run analysis
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a security assistant analyzing images. "
                        "Do not identify or make assumptions about specific individuals. "
                        "Instead, describe visible people’s posture (e.g., sitting, running), visible object types "
                        "(e.g., bags, tools, weapons), and potential threats. Return the following fields:\n"
                        "- profiles: list of descriptions of each human\n"
                        "- weapons: list of any objects resembling weapons\n"
                        "- danger: brief summary of threat level\n"
                        "- action_required: true/false flag\n"
                        "Respond strictly in JSON format only. Avoid vague statements or refusals."
                    )
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Analyze this image and return the structured information as instructed."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ]
                }
            ],
            temperature=0.2,
            max_tokens=1000
        )

        # Extract text and try to parse JSON
        raw_text = response.choices[0].message.content
        structured = _safe_parse_json(raw_text)

        # If the model refused to analyze, flag it
        if "sorry" in raw_text.lower() or not structured:
            raise ValueError("Model refused or failed to respond with structured data.")

        return {
            "status": "success",
            "timestamp": timestamp,
            "image_path": image_path,
            "profiles": structured.get("profiles", []),
            "weapons": structured.get("weapons", []),
            "danger": structured.get("danger", "Not provided."),
            "action_required": structured.get("action_required", False),
            "raw_model_response": raw_text
        }

    except Exception as e:
        print(f"[ERROR] during image analysis: {e}")
        return {
            "status": "error",
            "timestamp": timestamp,
            "image_path": image_path,
            "error": str(e),
            "profiles": [],
            "weapons": [],
            "danger": "Unable to analyze due to error.",
            "action_required": False,
            "raw_model_response": None
        }

# Helper: convert image to base64 string
def _to_base64(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

# Helper: safely parse a JSON block from model output
def _safe_parse_json(text):
    try:
        if text.startswith("```json"):
            text = re.sub(r"```json|```", "", text).strip()
        return json.loads(text)
    except json.JSONDecodeError:
        return {}
