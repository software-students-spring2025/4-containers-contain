"""
Module tests for the machine learning client.
This module tests the analyze_mood_from_image function.
"""

import os
from unittest.mock import patch
import pytest
import requests
from app import app, analyze_mood_from_image


def test_file_not_found():
    """Test that analyzing a nonexistent image file returns an error response."""
    result = analyze_mood_from_image("nonexistent.jpg")
    expected = {
        "emotion": "error",
        "explanation": "Image file not found.",
        "recommendation": "",
    }
    assert result == expected


@pytest.fixture
def test_image_path():
    """Fixture to get the path of the test image. Will be used by other tests."""
    return os.path.join(os.path.dirname(__file__), "happy-guy.jpg")


@patch("app.requests.post")
def test_valid_image(mock_post, test_image_path):
    """Test that a valid image returns correct analysis."""
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": '{"emotion": "happy", "explanation": "The person is smiling", '
                    '"recommendation": "Listen to uplifting music"}'
                }
            }
        ]
    }
    mock_post.return_value.json.return_value = mock_response
    result = analyze_mood_from_image(test_image_path)

    assert "emotion" in result
    assert "explanation" in result
    assert "recommendation" in result
    assert "happy" in result["emotion"]
    assert "smiling" in result["explanation"] or "smile" in result["explanation"]
    assert isinstance(result["recommendation"], str)
    assert len(result["recommendation"]) > 0


@patch("app.requests.post")
def test_no_face(mock_post, test_image_path):
    """Test when an image contains no faces."""
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": '{"emotion": "none", '
                    '"explanation": "No clear face detected, ambiguous analysis", '
                    '"recommendation": "No recommendation."}'
                }
            }
        ]
    }
    mock_post.return_value.json.return_value = mock_response
    result = analyze_mood_from_image(test_image_path)

    assert "emotion" in result
    assert "explanation" in result
    assert "recommendation" in result
    assert result["emotion"] == "none"
    assert "ambiguous" in result["explanation"].lower()
    assert "no recommendation." in result["recommendation"].lower()


@patch("app.requests.post")
def test_many_faces(mock_post, test_image_path):
    """Test when an image contains multiple faces."""
    mock_response = {
        "choices": [
            {
                "message": {
                    "content": '{"emotion": "none", '
                    '"explanation": "Multiple faces detected, ambiguous analysis", '
                    '"recommendation": "No recommendation."}'
                }
            }
        ]
    }
    mock_post.return_value.json.return_value = mock_response
    result = analyze_mood_from_image(test_image_path)

    assert "emotion" in result
    assert "explanation" in result
    assert "recommendation" in result
    assert result["emotion"] == "none"
    assert "ambiguous" in result["explanation"].lower()
    assert "no recommendation." in result["recommendation"].lower()


@patch("app.requests.post")
def test_api_exception(mock_post, test_image_path):
    """Test if there is an error with the API."""
    mock_post.side_effect = requests.RequestException("API call failed")
    result = analyze_mood_from_image(test_image_path)

    assert result["emotion"] == "error"
    assert "api error" in result["explanation"].lower()
    assert result["recommendation"] == ""


@pytest.fixture
def client():
    """Fixture to provide a test client for the Flask app."""
    with app.test_client() as client:
        yield client


def test_analyze_endpoint_valid_file(client, test_image_path):
    """Test the analyze endpoint with a valid image file."""
    with open(test_image_path, "rb"):
        response = client.post("/analyze", json={"filename": "happy-guy.jpg"})
        assert response.status_code == 200
        json_data = response.get_json()

        assert "emotion" in json_data
        assert "explanation" in json_data
        assert "recommendation" in json_data


def test_analyze_endpoint_invalid_file(client):
    """Test the analyze endpoint with invalid/missing filename."""
    response = client.post("/analyze", json={})
    assert response.status_code == 400
    assert "error" in response.get_json()
