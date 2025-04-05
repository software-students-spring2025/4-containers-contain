import os

import requests
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app, analyze_mood_from_image


def fake_post_success(*args, **kwargs):
    class FakeResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {
                "choices": [
                    {
                        "message": {
                            "content": '{"emotion": "happy", "explanation": "Image shows a smile"}'
                        }
                    }
                ]
            }

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
            # Missing required keys
            return {
                "choices": [{"message": {"content": '{"unexpected_key": "value"}'}}]
            }

    return FakeResponse()


def fake_post_exception(*args, **kwargs):
    raise requests.RequestException("API error")


# --- Tests for analyze_mood_from_image function ---


def test_file_not_found():
    result = analyze_mood_from_image("nonexistent.jpg")
    assert result == {"emotion": "error", "explanation": "Image file not found."}


# TODO -- add more tests for analyze_mood_from_image function
