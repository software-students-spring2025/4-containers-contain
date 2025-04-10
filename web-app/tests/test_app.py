"""
Module tests for the web app.
"""

import os
import io
import requests
import tempfile
from datetime import datetime
from unittest.mock import patch, MagicMock
import pytest

os.environ["UPLOAD_FOLDER"] = tempfile.mkdtemp()
from app import app, allowed_file  # pylint: disable=wrong-import-position


@pytest.fixture
def client_instance():
    """Fixture for testing the Flask app."""
    # Enable testing mode.
    app.config["TESTING"] = True
    # Use a temporary directory for file uploads.
    with tempfile.TemporaryDirectory() as tmp_upload_dir:
        app.config["UPLOAD_FOLDER"] = tmp_upload_dir
        # Ensure the directory exists.
        os.makedirs(tmp_upload_dir, exist_ok=True)
        with app.test_client() as client_instance:
            yield client_instance


def test_allowed_file():
    """test the allowed_file function."""
    # Valid file extensions (case-insensitive)
    assert allowed_file("image.png")
    assert allowed_file("photo.JPG")
    # Invalid file extensions
    assert not allowed_file("document.pdf")
    assert not allowed_file("no_extension")


@patch("app.requests.post")
@patch("app.collection.insert_one")
def test_index_post_success(mock_insert_one, mock_requests_post, client_instance):
    """
    Test a successful POST to the index endpoint.
    This simulates sending a valid image file and a successful response from the ML client.
    """
    # Create a fake response object for the ML client.
    fake_ml_response = MagicMock()
    fake_ml_response.json.return_value = {
        "emotion": "happy",
        "explanation": "smile detected",
    }
    fake_ml_response.raise_for_status.return_value = None
    mock_requests_post.return_value = fake_ml_response

    # Simulate an image file upload.
    data = {"image": (io.BytesIO(b"fake image data"), "test.jpg")}
    response = client_instance.post(
        "/", data=data, content_type="multipart/form-data", follow_redirects=False
    )
    # Expect a redirect after processing.
    assert response.status_code == 302

    # Verify that MongoDB insert was called with the expected data.
    args, _ = mock_insert_one.call_args
    inserted_data = args[0]
    assert inserted_data["filename"] == "test.jpg"
    assert inserted_data["emotion"] == "happy"
    assert inserted_data["explanation"] == "smile detected"
    # Check that a timestamp is included.
    assert "timestamp" in inserted_data
    assert isinstance(inserted_data["timestamp"], datetime)

@patch("app.requests.post")
def test_get_activities_fail(mock_requests_post, client_instance):
    """
    Test when get activities fails to offer suggestions.
    """
    mock_requests_post.side_effect = requests.RequestException("ML client timeout")

    response = client_instance.post(
        "/get-activities", json={"emotion": "happy"}, follow_redirects=False
    )
    # assert if status is 500 and message includes specified text
    assert response.status_code == 500
    assert b"Failed to retrieve activities" in response.data


def test_activities_page(client_instance):
    """
    Test if the activities page loads with the correct emotion.
    """
    response = client_instance.get("/activities?emotion=happy")

    # assert that the correct emotion is in the response data
    assert response.status_code == 200
    assert b"happy" in response.data 