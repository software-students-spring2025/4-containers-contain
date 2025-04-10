"""
Module tests for the machine learning client.
This module tests the analyze_mood_from_image function.
"""

from app import analyze_mood_from_image
import app


def test_file_not_found():
    """Test that analyzing a nonexistent image file returns an error response."""
    result = analyze_mood_from_image("nonexistent.jpg")
    expected = {
        "emotion": "error",
        "explanation": "Image file not found.",
        "recommendation": ""
    }
    assert result == expected


def test_empty_file_path():
    """Test analyzing with an empty file path returns an error."""
    result = analyze_mood_from_image("")
    assert result["emotion"] == "error"
    assert "not found" in result["explanation"].lower()


def test_return_structure_keys():
    """Test that a result always includes expected keys: emotion, explanation, recommendation."""
    result = analyze_mood_from_image("nonexistent.jpg")
    assert all(key in result for key in ["emotion", "explanation", "recommendation"])


def test_mock_valid_image(monkeypatch):
    """Test analyze_mood_from_image returns mocked values for a valid image."""

    def mock_analyze(_):
        return {
            "emotion": "happy",
            "explanation": "Detected smiling face",
            "recommendation": "Share your happiness with a friend!"
        }

    monkeypatch.setattr(app, "analyze_mood_from_image", mock_analyze)
    result = analyze_mood_from_image("valid.jpg")

    assert result["emotion"] == "happy"
    assert "smiling" in result["explanation"].lower()
