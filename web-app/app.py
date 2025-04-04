from flask import Flask, render_template, request, redirect, url_for, send_from_directory
from pymongo import MongoClient
from datetime import datetime
from werkzeug.utils import secure_filename
import os

UPLOAD_FOLDER = '/shared/uploads'
ALLOWED_EXTENSIONS = { 'png', 'jpg', 'jpeg' }

app = Flask(__name__)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

client = MongoClient("mongodb://mongo:27017/")
db = client["mood_db"]
collection = db["moods"]

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["image"]
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)

            # Insert only if not already in DB
            if not collection.find_one({"filename": filename}):
                collection.insert_one({
                    "filename": filename,
                    "analysis": "processing",
                    "timestamp": datetime.utcnow()
                })

        return redirect(url_for("index"))

    results = list(collection.find().sort("timestamp", -1).limit(10))
    return render_template("index.html", moods=results)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
