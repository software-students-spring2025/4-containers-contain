"""
Machine Learning Client for Mood Detector.
This module exposes an API endpoint to analyze images and detect emotion using the OpenAI API.
"""

import os
import base64
import json
import logging
import re

from flask import Flask, request, jsonify
from dotenv import load_dotenv
import requests

app = Flask(__name__)
UPLOAD_FOLDER = "/shared/uploads"

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
HEADERS = {
    "Authorization": f"Bearer {OPENAI_API_KEY}",
    "Content-Type": "application/json",
}


def analyze_mood_from_image(image_path):
    """Analyze mood from an image using the OpenAI API.

    Args:
        image_path (str): The path to the image file.

    Returns:
        dict: Analysis result with keys 'emotion', 'explanation', and 'recommendation'.
    """
    try:
        with open(image_path, "rb") as f:
            b64_image = base64.b64encode(f.read()).decode("utf-8")
    except FileNotFoundError:
        logging.error("Image file not found: %s", image_path)
        return {"emotion": "error", "explanation": "Image file not found.", "recommendation": ""}

    prompt_text = (
        "Analyze the facial expression in the provided image. "
        "Return your result as a JSON object with three keys: 'emotion', 'explanation', and 'recommendation'. "
        "'emotion' should be a single word (e.g., 'happy', 'sad', 'angry') representing the dominant emotion. "
        "'explanation' should be a one-sentence explanation of how you arrived at that conclusion. "
        "'recommendation' should be a one-sentence suggestion based on the mood detected. "
        "If the image does not contain a clear single face—either because no face is present or multiple faces are present—"
        "return 'none' as the emotion, include an explanation stating that the analysis was ambiguous, "
        "and set the recommendation to 'no recommendation'."
    )

    data = {
        "model": "gpt-4o",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt_text},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{b64_image}"},
                    },
                ],
            }
        ],
        "max_tokens": 150,
    }

    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=HEADERS,
            json=data,
            timeout=150,
        )
        response.raise_for_status()
        result = response.json()
        raw_output = result["choices"][0]["message"]["content"].strip()
        logging.info("GPT raw response: %s", raw_output)
        if raw_output.startswith("```"):
            raw_output = re.sub(r"^```(?:json)?\s*", "", raw_output)
            raw_output = re.sub(r"\s*```$", "", raw_output)
        try:
            analysis = json.loads(raw_output)
            if "emotion" in analysis and "explanation" in analysis and "recommendation" in analysis:
                return analysis
            logging.error("Response JSON missing required keys: %s", analysis)
            return {"emotion": "error", "explanation": "Incomplete response from analysis.", "recommendation": ""}
        except json.JSONDecodeError:
            logging.error("Failed to parse JSON from GPT response.")
            return {"emotion": "error", "explanation": "Response could not be parsed as JSON.", "recommendation": ""}
    except requests.RequestException as e:
        logging.error("Failed to analyze image %s: %s", image_path, e)
        return {"emotion": "error", "explanation": "Unable to analyze mood due to an API error.", "recommendation": ""}


@app.route("/analyze", methods=["POST"])
def analyze_endpoint():
    """API endpoint to analyze the image for mood detection."""
    data = request.get_json()
    filename = data.get("filename")
    if not filename:
        return jsonify({"error": "Filename not provided"}), 400
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    result = analyze_mood_from_image(image_path)
    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
