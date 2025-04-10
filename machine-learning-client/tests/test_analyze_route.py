"""Tests for the /analyze route in app.py."""

import pytest
import app


@pytest.fixture
def client():
    """Fixture to create a test client for the Flask app."""
    app.app.config["TESTING"] = True
    with app.app.test_client() as client:
        yield client


def test_analyze_route_file_not_found(client):
    """Test that /analyze returns an error for missing image file."""
    response = client.post("/analyze", json={"filename": "nonexistent.jpg"})
    data = response.get_json()
    assert response.status_code == 200
    assert data["emotion"] == "error"
    assert "not found" in data["explanation"].lower()


def test_analyze_route_mocked_success(monkeypatch, client):
    """Test /analyze with mocked happy emotion response."""

    def mock_analyze_mood_from_image(_):
        return {
            "emotion": "happy",
            "explanation": "Detected a smiling face.",
            "recommendation": "Call a friend and share your good vibes!",
        }

    monkeypatch.setattr(app, "analyze_mood_from_image", mock_analyze_mood_from_image)
    response = client.post("/analyze", json={"filename": "valid.jpg"})
    data = response.get_json()

    assert response.status_code == 200
    assert data["emotion"] == "happy"
    assert "smiling" in data["explanation"].lower()
