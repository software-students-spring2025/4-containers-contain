FROM python:3.10-slim
WORKDIR /app
COPY . .
RUN pip install flask pymongo werkzeug
CMD ["python", "app.py"]
