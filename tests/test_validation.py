from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

mock_inference = MagicMock()
mock_inference.model_path = "gpt2"
mock_inference.generate.return_value = {"text": "test response", "tokens_used": 10}

with patch("app.inference.inference_service", mock_inference):
    with patch("app.inference.ModelInference.load_model"):
        from app.main import app

client = TestClient(app, raise_server_exceptions=False)


# --- Тесты, которых нет в test_api.py ---

def test_prompt_too_long_returns_422():
    """Prompt длиннее 2000 символов → 422"""
    long_prompt = "а" * 2001
    response = client.post("/generate", json={"prompt": long_prompt})
    assert response.status_code == 422


def test_temperature_too_high_returns_422():
    """temperature > 2.0 → 422"""
    response = client.post("/generate", json={"prompt": "Тест", "temperature": 3.0})
    assert response.status_code == 422


def test_temperature_negative_returns_422():
    """temperature < 0.0 → 422"""
    response = client.post("/generate", json={"prompt": "Тест", "temperature": -0.1})
    assert response.status_code == 422


def test_max_tokens_zero_returns_422():
    """max_tokens = 0 → 422"""
    response = client.post("/generate", json={"prompt": "Тест", "max_tokens": 0})
    assert response.status_code == 422