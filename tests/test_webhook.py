"""
Testes para os nós de webhook (validação e cadastro).

Testa:
- validar_webhook
- verificar_cliente
- cadastrar_cliente
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, AsyncMock

# Adicionar src ao path
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from nodes.webhook import validar_webhook, verificar_cliente, cadastrar_cliente
from models.state import AcaoFluxo


# ==============================================
# TESTES DE validar_webhook
# ==============================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_validar_webhook_sucesso(state_inicial):
    """Testa validação bem-sucedida do webhook."""
    result = await validar_webhook(state_inicial)

    # Verificar extração de dados
    assert result["cliente_numero"] == "5562999999999"
    assert result["cliente_nome"] == "Cliente Teste"
    assert result["mensagem_tipo"] == "conversation"
    assert result["mensagem_id"] == "MSG123456"

    # Verificar next_action
    assert result["next_action"] == AcaoFluxo.VERIFICAR_CLIENTE.value


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validar_webhook_proprio_numero(webhook_data_texto):
    """Testa filtro de mensagens do próprio bot."""
    # Alterar para número do bot (pegar de settings)
    from config.settings import get_settings
    settings = get_settings()
    webhook_data_texto["body"]["data"]["key"]["remoteJid"] = f"{settings.bot_phone_number}@s.whatsapp.net"

    state = {
        "raw_webhook_data": webhook_data_texto,
        "next_action": ""
    }

    result = await validar_webhook(state)

    # Deve ser ignorado quando remoteJid = bot
    assert result["next_action"] == AcaoFluxo.END.value
    assert "erro" not in result


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validar_webhook_mensagem_propria(webhook_data_texto):
    """Testa que mensagens fromMe=True são capturadas no estado."""
    webhook_data_texto["body"]["data"]["key"]["fromMe"] = True

    state = {
        "raw_webhook_data": webhook_data_texto,
        "next_action": ""
    }

    result = await validar_webhook(state)

    # A função não filtra baseado em fromMe, apenas armazena no estado
    assert result["mensagem_from_me"] is True
    assert result["next_action"] == AcaoFluxo.VERIFICAR_CLIENTE.value


@pytest.mark.unit
@pytest.mark.asyncio
async def test_validar_webhook_dados_invalidos():
    """Testa validação com dados inválidos/faltantes."""
    state = {
        "raw_webhook_data": {"body": {}},
        "next_action": ""
    }

    result = await validar_webhook(state)

    # Deve ter erro
    assert "erro" in result or result["next_action"] == AcaoFluxo.ERRO.value


# ==============================================
# TESTES DE verificar_cliente
# ==============================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_verificar_cliente_existente(state_inicial, cliente_existente):
    """Testa verificação de cliente que já existe no banco."""
    # Mock do Supabase
    with patch('nodes.webhook.criar_supabase_client') as mock_criar:
        mock_client = AsyncMock()
        mock_client.buscar_cliente.return_value = cliente_existente
        mock_criar.return_value = mock_client

        # Preparar estado
        state_inicial["cliente_numero"] = "5562999999999"

        # Executar
        result = await verificar_cliente(state_inicial)

        # Verificar
        assert result["cliente_id"] == "cliente-123"
        assert result["cliente_existe"] is True
        assert result["next_action"] == AcaoFluxo.PROCESSAR_MIDIA.value


@pytest.mark.unit
@pytest.mark.asyncio
async def test_verificar_cliente_nao_existente(state_inicial):
    """Testa verificação de cliente novo (não existe no banco)."""
    # Mock do Supabase retornando None
    with patch('nodes.webhook.criar_supabase_client') as mock_criar:
        mock_client = AsyncMock()
        mock_client.buscar_cliente.return_value = None
        mock_criar.return_value = mock_client

        # Preparar estado
        state_inicial["cliente_numero"] = "5562111111111"
        state_inicial["cliente_nome"] = "Cliente Novo"

        # Executar
        result = await verificar_cliente(state_inicial)

        # Verificar
        assert result["cliente_existe"] is False
        assert result["next_action"] == AcaoFluxo.CADASTRAR_CLIENTE.value


# ==============================================
# TESTES DE cadastrar_cliente
# ==============================================

@pytest.mark.unit
@pytest.mark.asyncio
async def test_cadastrar_cliente_sucesso(state_inicial):
    """Testa cadastro bem-sucedido de novo cliente."""
    # Mock do Supabase
    with patch('nodes.webhook.criar_supabase_client') as mock_criar:
        mock_client = AsyncMock()
        mock_client.cadastrar_cliente.return_value = {
            "id": "cliente-novo-789",
            "nome_lead": "Cliente Teste",
            "phone_numero": "5562999999999"
        }
        mock_criar.return_value = mock_client

        # Preparar estado
        state_inicial["cliente_numero"] = "5562999999999"
        state_inicial["cliente_nome"] = "Cliente Teste"
        state_inicial["mensagem_conteudo"] = "Olá, preciso de informações"
        state_inicial["mensagem_tipo"] = "conversation"

        # Executar
        result = await cadastrar_cliente(state_inicial)

        # Verificar
        assert result["cliente_id"] == "cliente-novo-789"
        assert result["cliente_existe"] is True
        assert result["next_action"] == AcaoFluxo.PROCESSAR_MIDIA.value

        # Verificar que chamou cadastrar_cliente
        mock_client.cadastrar_cliente.assert_called_once()


@pytest.mark.unit
@pytest.mark.asyncio
async def test_cadastrar_cliente_erro(state_inicial):
    """Testa tratamento de erro no cadastro."""
    # Mock do Supabase com erro
    with patch('nodes.webhook.criar_supabase_client') as mock_criar:
        mock_client = AsyncMock()
        mock_client.cadastrar_cliente.side_effect = Exception("Erro no banco de dados")
        mock_criar.return_value = mock_client

        # Preparar estado
        state_inicial["cliente_numero"] = "5562999999999"
        state_inicial["cliente_nome"] = "Cliente Teste"
        state_inicial["mensagem_conteudo"] = "Teste"
        state_inicial["mensagem_tipo"] = "conversation"

        # Executar
        result = await cadastrar_cliente(state_inicial)

        # Verificar que teve erro mas não quebrou
        assert "erro" in result or result["next_action"] == AcaoFluxo.ERRO.value
