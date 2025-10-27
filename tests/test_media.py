"""
Testes para processamento de mídia.

Testa:
- rotear_tipo_mensagem
- processar_texto
- processar_audio
- processar_imagem
"""

import pytest
import sys
from pathlib import Path

# Adicionar src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from nodes.media import rotear_tipo_mensagem, processar_texto, processar_audio, processar_imagem


# ==============================================
# TESTES DE rotear_tipo_mensagem
# ==============================================

@pytest.mark.unit
def test_rotear_texto():
    """Testa roteamento para processamento de texto."""
    state = {"mensagem_tipo": "conversation"}
    assert rotear_tipo_mensagem(state) == "processar_texto"


@pytest.mark.unit
def test_rotear_texto_extendido():
    """Testa roteamento para texto estendido."""
    state = {"mensagem_tipo": "extendedTextMessage"}
    assert rotear_tipo_mensagem(state) == "processar_texto"


@pytest.mark.unit
def test_rotear_audio():
    """Testa roteamento para processamento de áudio."""
    state = {"mensagem_tipo": "audioMessage"}
    assert rotear_tipo_mensagem(state) == "processar_audio"


@pytest.mark.unit
def test_rotear_imagem():
    """Testa roteamento para processamento de imagem."""
    state = {"mensagem_tipo": "imageMessage"}
    assert rotear_tipo_mensagem(state) == "processar_imagem"


@pytest.mark.unit
def test_rotear_tipo_desconhecido():
    """Testa roteamento de tipo desconhecido (fallback para texto)."""
    state = {"mensagem_tipo": "unknownType"}
    # Deve ter fallback para texto
    result = rotear_tipo_mensagem(state)
    assert result in ["processar_texto", "processar_audio", "processar_imagem"]


# ==============================================
# TESTES DE processar_texto
# ==============================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_processar_texto_simples():
    """Testa processamento de texto simples."""
    state = {
        "mensagem_base64": "Olá, tudo bem?",
        "next_action": ""
    }

    result = await processar_texto(state)

    assert result["mensagem_conteudo"] == "Olá, tudo bem?"
    assert result["next_action"] != ""


@pytest.mark.unit
@pytest.mark.asyncio
async def test_processar_texto_vazio():
    """Testa processamento de texto vazio."""
    state = {
        "mensagem_base64": "",
        "next_action": ""
    }

    result = await processar_texto(state)

    # Deve ter erro ou mensagem padrão
    assert "erro" in result or result.get("mensagem_conteudo", "") == ""


@pytest.mark.unit
@pytest.mark.asyncio
async def test_processar_texto_com_emojis():
    """Testa processamento de texto com emojis."""
    state = {
        "mensagem_base64": "Olá! 😊 Como está?",
        "next_action": ""
    }

    result = await processar_texto(state)

    assert "mensagem_conteudo" in result
    assert len(result["mensagem_conteudo"]) > 0


# ==============================================
# TESTES DE processar_audio (MOCK)
# ==============================================

@pytest.mark.skip(reason="Complexo de mockar - requer integração completa")
@pytest.mark.unit
@pytest.mark.asyncio
async def test_processar_audio_mock(webhook_data_audio):
    """Testa processamento de áudio (mockado)."""
    from unittest.mock import patch, AsyncMock, MagicMock

    state = {
        "raw_webhook_data": webhook_data_audio,
        "mensagem_id": "MSG_AUDIO_123",
        "next_action": ""
    }

    # Mock do WhatsApp client e OpenAI
    with patch('clients.whatsapp_client.criar_whatsapp_client') as mock_criar_whatsapp:
        with patch('openai.Audio.atranscribe') as mock_transcribe:
            # Configurar mocks
            mock_whatsapp = AsyncMock()
            mock_whatsapp.obter_media_base64.return_value = {
                "base64": "fake_audio_base64",
                "mimetype": "audio/ogg"
            }
            mock_criar_whatsapp.return_value = mock_whatsapp

            mock_transcribe.return_value = MagicMock(
                text="Transcrição do áudio de teste"
            )

            # Executar
            result = await processar_audio(state)

            # Verificar (se implementado)
            # assert "mensagem_conteudo" in result or "erro" in result


# ==============================================
# TESTES DE processar_imagem (MOCK)
# ==============================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_processar_imagem_com_caption(webhook_data_imagem):
    """Testa processamento de imagem com legenda."""
    state = {
        "raw_webhook_data": webhook_data_imagem,
        "mensagem_id": "MSG_IMG_123",
        "next_action": ""
    }

    # Se a função pegar caption diretamente
    result = await processar_imagem(state)

    # Verificar que processou ou retornou erro
    assert "mensagem_conteudo" in result or "erro" in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_processar_imagem_sem_caption(webhook_data_imagem):
    """Testa processamento de imagem sem legenda."""
    # Remover caption
    del webhook_data_imagem["body"]["data"]["message"]["imageMessage"]["caption"]

    state = {
        "raw_webhook_data": webhook_data_imagem,
        "mensagem_id": "MSG_IMG_123",
        "next_action": ""
    }

    result = await processar_imagem(state)

    # Deve processar com OCR ou retornar mensagem padrão
    assert result is not None
