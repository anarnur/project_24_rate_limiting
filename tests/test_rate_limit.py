from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

mock_inference = MagicMock()
mock_inference.model_path = "gpt2"
mock_inference.generate.return_value = {"text": "test response", "tokens_used": 10}

with patch("app.inference.inference_service", mock_inference):
    with patch("app.inference.ModelInference.load_model"):
        from app.main import app

client = TestClient(app, raise_server_exceptions=False)


def test_rate_limit_exceeded():
    """После 10 запросов в минуту → 429"""
    headers = {"X-Forwarded-For": "10.0.0.1"}
    payload = {"prompt": "Тест rate limit"}

    responses = []
    for _ in range(11):
        r = client.post("/generate", json=payload, headers=headers)
        responses.append(r.status_code)

    assert responses[-1] == 429


def test_rate_limit_response_body():
    """Тело ответа 429 содержит error и detail"""
    headers = {"X-Forwarded-For": "10.0.0.2"}
    payload = {"prompt": "Тест"}

    for _ in range(10):
        client.post("/generate", json=payload, headers=headers)

    r = client.post("/generate", json=payload, headers=headers)
    assert r.status_code == 429
    data = r.json()
    assert data["error"] == "rate_limit_exceeded"
    assert "detail" in data