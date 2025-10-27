"""
Configuração de fixtures do pytest.

Este módulo contém fixtures compartilhadas entre todos os testes.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch
from typing import Dict, Any

# Adicionar src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from models.state import AgentState, criar_estado_inicial


# ==============================================
# FIXTURES DE DADOS
# ==============================================

@pytest.fixture
def webhook_data_texto() -> Dict[str, Any]:
    """Fixture com webhook de mensagem de texto."""
    return {
        "body": {
            "event": "messages.upsert",
            "instance": "test-instance",
            "data": {
                "key": {
                    "remoteJid": "5562999999999@s.whatsapp.net",
                    "id": "MSG123456",
                    "fromMe": False
                },
                "pushName": "Cliente Teste",
                "message": {
                    "conversation": "Olá, preciso de informações sobre instalação de drywall"
                },
                "messageType": "conversation",
                "messageTimestamp": 1672531200
            }
        }
    }


@pytest.fixture
def webhook_data_audio() -> Dict[str, Any]:
    """Fixture com webhook de mensagem de áudio."""
    return {
        "body": {
            "event": "messages.upsert",
            "instance": "test-instance",
            "data": {
                "key": {
                    "remoteJid": "5562888888888@s.whatsapp.net",
                    "id": "MSG_AUDIO_123",
                    "fromMe": False
                },
                "pushName": "Cliente Audio",
                "message": {
                    "audioMessage": {
                        "url": "https://example.com/audio.ogg",
                        "mimetype": "audio/ogg; codecs=opus"
                    }
                },
                "messageType": "audioMessage",
                "messageTimestamp": 1672531300
            }
        }
    }


@pytest.fixture
def webhook_data_imagem() -> Dict[str, Any]:
    """Fixture com webhook de mensagem de imagem."""
    return {
        "body": {
            "event": "messages.upsert",
            "instance": "test-instance",
            "data": {
                "key": {
                    "remoteJid": "5562777777777@s.whatsapp.net",
                    "id": "MSG_IMG_123",
                    "fromMe": False
                },
                "pushName": "Cliente Imagem",
                "message": {
                    "imageMessage": {
                        "url": "https://example.com/image.jpg",
                        "mimetype": "image/jpeg",
                        "caption": "Foto do ambiente"
                    }
                },
                "messageType": "imageMessage",
                "messageTimestamp": 1672531400
            }
        }
    }


@pytest.fixture
def state_inicial(webhook_data_texto) -> AgentState:
    """Fixture com estado inicial do AgentState."""
    return {
        "raw_webhook_data": webhook_data_texto,
        "next_action": ""
    }


@pytest.fixture
def cliente_existente() -> Dict[str, Any]:
    """Fixture com dados de cliente existente no banco."""
    return {
        "id": "cliente-123",
        "nome_lead": "Cliente Teste",
        "phone_numero": "5562999999999",
        "message": "Mensagem anterior",
        "tipo_mensagem": "conversation",
        "created_at": "2025-01-01T00:00:00"
    }


# ==============================================
# FIXTURES DE MOCKS - CLIENTES EXTERNOS
# ==============================================

@pytest.fixture
def mock_supabase_client():
    """Mock do cliente Supabase."""
    mock = AsyncMock()

    # Configurar comportamento padrão
    mock.buscar_cliente.return_value = {
        "id": "cliente-123",
        "nome_lead": "Cliente Teste",
        "phone_numero": "5562999999999"
    }

    mock.cadastrar_cliente.return_value = {
        "id": "cliente-novo-456",
        "nome_lead": "Cliente Novo",
        "phone_numero": "5562111111111"
    }

    mock.buscar_documentos_rag.return_value = [
        {
            "content": "Instalação de drywall custa R$ 80 a R$ 120 por m²",
            "similarity": 0.85
        }
    ]

    return mock


@pytest.fixture
def mock_whatsapp_client():
    """Mock do cliente WhatsApp."""
    mock = AsyncMock()

    # Configurar comportamento padrão
    mock.enviar_mensagem.return_value = {
        "success": True,
        "id": "MSG_SENT_123"
    }

    mock.enviar_status_typing.return_value = None
    mock.obter_media_base64.return_value = {
        "base64": "base64_fake_data",
        "mimetype": "audio/ogg"
    }

    return mock


@pytest.fixture
def mock_redis_client():
    """Mock do cliente Redis."""
    mock = AsyncMock()

    mock.adicionar_mensagem.return_value = True
    mock.obter_mensagens.return_value = [
        {"role": "user", "content": "Mensagem 1"},
        {"role": "assistant", "content": "Resposta 1"}
    ]
    mock.limpar_fila.return_value = True

    return mock


@pytest.fixture
def mock_openai_client():
    """Mock do cliente OpenAI."""
    mock = MagicMock()

    # Mock da resposta do chat
    mock.chat.completions.create.return_value = MagicMock(
        choices=[
            MagicMock(
                message=MagicMock(
                    content="Olá! Para instalação de drywall, trabalhamos com preços entre R$ 80 e R$ 120 por m². Gostaria de agendar uma visita técnica?",
                    tool_calls=None
                )
            )
        ]
    )

    return mock


# ==============================================
# FIXTURES DE CONFIGURAÇÃO
# ==============================================

@pytest.fixture
def mock_settings():
    """Mock das configurações da aplicação."""
    from unittest.mock import MagicMock

    settings = MagicMock()
    settings.whatsapp_api_url = "https://fake-api.com"
    settings.whatsapp_api_key = "fake-key"
    settings.whatsapp_instance = "test-instance"
    settings.bot_phone_number = "555195877046"
    settings.supabase_url = "https://fake-supabase.co"
    settings.supabase_key = "fake-supabase-key"
    settings.max_fragment_size = 300
    settings.agent_timeout = 60
    settings.max_retries = 3
    settings.enable_memory_persistence = False

    return settings


# ==============================================
# FIXTURES DE GRAFO
# ==============================================

@pytest.fixture
def grafo_teste():
    """Fixture que cria um grafo de teste."""
    from graph.workflow import criar_grafo_atendimento
    return criar_grafo_atendimento()


# ==============================================
# CONFIGURAÇÃO DO PYTEST
# ==============================================

def pytest_configure(config):
    """Configuração do pytest."""
    config.addinivalue_line(
        "markers", "integration: marca testes de integração (lentos)"
    )
    config.addinivalue_line(
        "markers", "unit: marca testes unitários (rápidos)"
    )
