import os
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from pymongo import MongoClient
from werkzeug.utils import secure_filename
import requests

UPLOAD_FOLDER = os.environ.get("UPLOAD_FOLDER", "/shared/uploads")
ALLOWED_EXTENSIONS = {"jpeg", "jpg", "png"}

app = Flask(__name__)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER

client = MongoClient("mongodb://mongo:27017/")
db = client["mood_db"]
collection = db["moods"]


def allowed_file(filename):
    """Check if the filename has an allowed extension (only jpeg, jpg, and png)."""
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/uploads/<filename>")
def uploaded_file(filename):
    """Serve an uploaded file from the uploads folder."""
    return send_from_directory(app.config["UPLOAD_FOLDER"], filename)


@app.route("/", methods=["GET", "POST"])
def index():
    """Handle image upload, process it, and display recent uploads."""
    if request.method == "POST":
        file = request.files.get("image")
        # Return error if no file or file extension not allowed.
        if not file or not allowed_file(file.filename):
            return "File type not allowed", 400

        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(filepath)
        # Call the machine learning client for image analysis.
        try:
            response = requests.post(
                "http://ml-client:5001/analyze",
                json={"filename": filename},
                timeout=150,
            )
            response.raise_for_status()
            result = response.json()
        except requests.RequestException as e:
            result = {
                "emotion": "error",
                "explanation": f"ML analysis failed: {e}",
                "recommendation": "",
            }
        # Insert the analysis record into MongoDB.
        collection.insert_one(
            {
                "filename": filename,
                "emotion": result.get("emotion", "unknown"),
                "explanation": result.get("explanation", ""),
                "recommendation": result.get("recommendation", ""),
                "timestamp": datetime.utcnow(),
            }
        )
        return redirect(url_for("index"))

    results = list(collection.find().sort("timestamp", -1).limit(10))
    return render_template("index.html", moods=results)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
