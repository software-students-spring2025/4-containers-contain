import os
import io
import sys
import tempfile
import pytest
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app


def fake_post_success(*args, **kwargs):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"emotion": "happy", "explanation": "Image shows a smile"}

    return FakeResponse()


def fake_post_invalid_json(*args, **kwargs):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": "Not a valid JSON string"}}]}

    return FakeResponse()


def fake_post_incomplete(*args, **kwargs):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            # Missing required keys in the returned JSON
            return {"choices": [{"message": {"content": '{"unexpected_key": "value"}'}}]}

    return FakeResponse()


def fake_post_exception(*args, **kwargs):
    raise requests.RequestException("API error")


@pytest.fixture
def client(monkeypatch):
    # Create a temporary directory for file uploads.
    temp_upload_dir = tempfile.mkdtemp()
    app.config["UPLOAD_FOLDER"] = temp_upload_dir
    app.config["TESTING"] = True

    # Monkeypatch requests.post to simulate a successful response from the ML client.
    monkeypatch.setattr(requests, "post", fake_post_success)

    # Monkeypatch the collection's insert_one method so we can capture the inserted document.
    inserted_docs = []

    def fake_insert_one(doc):
        inserted_docs.append(doc)

    # 'collection' was defined in app.py as a global variable.
    # Import and monkeypatch it here.
    from app import collection

    monkeypatch.setattr(collection, "insert_one", fake_insert_one)

    # Provide both the test client and a list to record inserted documents.
    with app.test_client() as client:
        yield client, inserted_docs


# --- Tests for the web-app endpoints ---


def test_index_get(client):
    test_client, _ = client
    response = test_client.get("/")
    assert response.status_code == 200
    assert b"Mood Detector" in response.data


# TODO -- more tests for the index page
