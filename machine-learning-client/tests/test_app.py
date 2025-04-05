"""
Module tests for the machine learning client.
This module tests the analyze_mood_from_image function.
"""

from app import analyze_mood_from_image


def test_file_not_found():
    """
    Test that analyzing a nonexistent image file returns an error response.
    """
    result = analyze_mood_from_image("nonexistent.jpg")
    expected = {"emotion": "error", "explanation": "Image file not found."}
    assert result == expected


# TODO: Add more tests for the analyze_mood_from_image function.
