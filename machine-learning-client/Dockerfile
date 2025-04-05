FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir pymongo requests python-dotenv flask werkzeug
CMD ["python", "app.py"]
