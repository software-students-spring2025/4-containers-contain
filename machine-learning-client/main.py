import os
import time
import base64
import requests
from pymongo import MongoClient
from dotenv import load_dotenv

# Load .env variables
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
print("📦 OPENAI_API_KEY loaded:", bool(OPENAI_API_KEY))

client = MongoClient("mongodb://mongo:27017/")
db = client["mood_db"]
collection = db["moods"]

UPLOAD_FOLDER = "/shared/uploads"

HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json"
}

def analyze_mood_from_image(image_path):
    with open(image_path, "rb") as f:
        b64_image = base64.b64encode(f.read()).decode("utf-8")

    data = {
        "model": "gpt-4-vision-preview",
        "messages": [
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": "Analyze the mood or emotion this person is expressing based on their face. Respond with 1–2 sentences describing how they appear to feel."
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/jpeg;base64,{b64_image}"
                        }
                    }
                ]
            }
        ],
        "max_tokens": 100
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=HEADERS,
            json=data
        )
        response.raise_for_status()
        result = response.json()
        analysis = result["choices"][0]["message"]["content"].strip()
        print("🔍 GPT response:", analysis)
        return analysis
    except Exception as e:
        print("❌ Failed to analyze image:", e)
        return "Unable to analyze mood."


while True:
    try:
        for fname in os.listdir(UPLOAD_FOLDER):
            if not fname.lower().endswith((".jpg", ".jpeg", ".png")):
                continue

            image_path = os.path.join(UPLOAD_FOLDER, fname)

            record = collection.find_one({"filename": fname})
            if not record or record.get("analysis") != "processing":
                continue

            print(f"🧠 Analyzing {fname}...")

            analysis = analyze_mood_from_image(image_path)

            result = collection.update_one(
                {"filename": fname, "analysis": "processing"},
                {"$set": {"analysis": analysis}}
            )

            if result.modified_count == 1:
                print(f"✅ Updated {fname} → {analysis}")
            else:
                print(f"⚠️ Skipped updating {fname} (already done?)")

    except Exception as e:
        print("❌ Error:", e)

    time.sleep(5)
