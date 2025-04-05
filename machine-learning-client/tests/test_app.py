import os

import requests
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app, analyze_mood_from_image


def test_file_not_found():
    result = analyze_mood_from_image("nonexistent.jpg")
    assert result == {"emotion": "error", "explanation": "Image file not found."}


# TODO -- add more tests for analyze_mood_from_image function
