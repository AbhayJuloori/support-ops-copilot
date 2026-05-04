import inspect
import sys
import types

import httpx
import pytest

from api.main import app
from api.routers import classify as classify_router


def _async_client():
    if "app" in inspect.signature(httpx.AsyncClient).parameters:
        return httpx.AsyncClient(app=app, base_url="http://test")
    return httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://test",
    )


@pytest.mark.asyncio
async def test_health_endpoint():
    async with _async_client() as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert "status" in response.json()


@pytest.mark.asyncio
async def test_classify_endpoint_503_when_no_model(tmp_path, monkeypatch):
    monkeypatch.setattr(classify_router, "MODELS_DIR", tmp_path)

    async with _async_client() as client:
        response = await client.post(
            "/classify",
            json={"text": "my wifi is broken", "priority": "high"},
        )

    assert response.status_code == 503


@pytest.mark.asyncio
async def test_classify_endpoint_with_mock_model(tmp_path, monkeypatch):
    (tmp_path / "ticket_classifier.pkl").write_bytes(b"fake model marker")
    monkeypatch.setattr(classify_router, "MODELS_DIR", tmp_path)

    fake_module = types.ModuleType("src.models.ticket_classifier")
    fake_module.predict = lambda text, priority="medium": {
        "category": "technical",
        "confidence": 0.91,
        "all_probabilities": {"technical": 0.91, "billing": 0.06, "shipping": 0.03},
    }
    monkeypatch.setitem(sys.modules, "src.models.ticket_classifier", fake_module)

    async with _async_client() as client:
        response = await client.post(
            "/classify",
            json={"text": "my wifi is broken", "priority": "high"},
        )

    assert response.status_code == 200
    body = response.json()
    assert body["category"] == "technical"
    assert 0.0 <= body["confidence"] <= 1.0

