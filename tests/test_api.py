"""
Testes da API FastAPI.

Testa:
- Health check endpoints
- Webhook endpoint
- Test message endpoint
"""

import pytest
import sys
from pathlib import Path
from fastapi.testclient import TestClient

# Adicionar src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

# Cliente de teste será criado em cada função para evitar erro de import


# ==============================================
# TESTES DE HEALTH CHECK
# ==============================================

@pytest.mark.unit
def test_root_endpoint():
    """Testa endpoint raiz /."""
    from main import app
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "running"


@pytest.mark.unit
def test_health_endpoint():
    """Testa endpoint /health."""
    from main import app
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"


@pytest.mark.unit
def test_status_endpoint():
    """Testa endpoint /status."""
    from main import app
    client = TestClient(app)
    response = client.get("/status")

    assert response.status_code == 200
    data = response.json()
    assert "bot" in data
    assert "instance" in data["bot"]


# ==============================================
# TESTES DE WEBHOOK
# ==============================================

@pytest.mark.unit
def test_webhook_mensagem_valida(webhook_data_texto):
    """Testa recebimento de webhook com mensagem válida."""
    from main import app
    client = TestClient(app)
    payload = {
        "event": "messages.upsert",
        "instance": "test-instance",
        "data": webhook_data_texto["body"]["data"]
    }

    response = client.post("/webhook/whatsapp", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "received"


@pytest.mark.unit
def test_webhook_evento_ignorado():
    """Testa que eventos não-mensagem são ignorados."""
    from main import app
    client = TestClient(app)
    payload = {
        "event": "connection.update",
        "instance": "test-instance",
        "data": {}
    }

    response = client.post("/webhook/whatsapp", json=payload)

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ignored"


@pytest.mark.unit
def test_webhook_mensagem_propria(webhook_data_texto):
    """Testa que mensagens do próprio bot são ignoradas."""
    from main import app
    client = TestClient(app)
    webhook_data_texto["body"]["data"]["key"]["fromMe"] = True

    payload = {
        "event": "messages.upsert",
        "instance": "test-instance",
        "data": webhook_data_texto["body"]["data"]
    }

    response = client.post("/webhook/whatsapp", json=payload)

    assert response.status_code == 200
    # Deve ser ignorado
    data = response.json()
    assert data["status"] in ["ignored", "accepted"]


# ==============================================
# TESTES DE TEST MESSAGE
# ==============================================

@pytest.mark.unit
def test_test_message_endpoint():
    """Testa endpoint de teste de mensagem."""
    from main import app
    client = TestClient(app)
    response = client.post(
        "/test/message",
        params={
            "telefone": "5562999999999",
            "mensagem": "Mensagem de teste"
        }
    )

    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "test_sent"
    assert data["telefone"] == "5562999999999"
    assert data["mensagem"] == "Mensagem de teste"
