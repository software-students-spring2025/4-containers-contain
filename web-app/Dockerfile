FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir flask pymongo werkzeug requests
CMD ["python", "app.py"]
