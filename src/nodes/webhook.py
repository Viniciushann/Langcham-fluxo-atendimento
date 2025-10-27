"""
Nós de webhook - Recepção e validação de mensagens.

Este módulo contém os nós responsáveis por processar webhooks da Evolution API,
verificar e cadastrar clientes no Supabase.
"""

from __future__ import annotations

import logging
from typing import Dict, Any

from src.models.state import AgentState, AcaoFluxo, extrair_numero_whatsapp
from src.clients.supabase_client import SupabaseClient, criar_supabase_client
from src.config.settings import get_settings

logger = logging.getLogger(__name__)


async def validar_webhook(state: AgentState) -> AgentState:
    """
    Valida e extrai dados do webhook da Evolution API.

    Processa o webhook recebido, extrai informações relevantes e filtra
    mensagens enviadas pelo próprio bot.

    Args:
        state: Estado atual do agente contendo raw_webhook_data

    Returns:
        AgentState: Estado atualizado com dados extraídos

    Raises:
        Nenhuma exceção é propagada. Erros são capturados e salvos no state.

    Example:
        >>> state = {
        ...     "raw_webhook_data": webhook_data,
        ...     "next_action": ""
        ... }
        >>> state = await validar_webhook(state)
        >>> print(state["cliente_numero"])
        "5562999999999"
    """
    try:
        logger.info("=" * 60)
        logger.info("Iniciando validação do webhook")
        logger.info("=" * 60)

        # Extrair dados do webhook
        webhook_data = state.get("raw_webhook_data", {})

        if not webhook_data:
            logger.error("raw_webhook_data está vazio")
            state["erro"] = "Webhook vazio"
            state["next_action"] = AcaoFluxo.END.value
            return state

        # Navegar na estrutura do webhook
        body = webhook_data.get("body", {})
        data = body.get("data", {})

        if not data:
            logger.error("Dados do webhook inválidos")
            state["erro"] = "Estrutura de webhook inválida"
            state["next_action"] = AcaoFluxo.END.value
            return state

        # Extrair informações principais
        key = data.get("key", {})
        remote_jid = key.get("remoteJid", "")
        from_me = key.get("fromMe", False)
        message_id = key.get("id", "")

        push_name = data.get("pushName", "Desconhecido")
        message_type = data.get("messageType", "outros")
        message_timestamp = data.get("messageTimestamp", None)

        logger.info(f"Webhook recebido:")
        logger.info(f"  Remote JID: {remote_jid}")
        logger.info(f"  From Me: {from_me}")
        logger.info(f"  Message Type: {message_type}")
        logger.info(f"  Push Name: {push_name}")

        # Carregar configurações para obter bot_phone_number
        settings = get_settings()
        bot_jid = f"{settings.bot_phone_number}@s.whatsapp.net"

        # Filtrar mensagens do próprio bot
        if remote_jid == bot_jid:
            logger.info(f"Mensagem filtrada: é do próprio bot ({bot_jid})")
            state["next_action"] = AcaoFluxo.END.value
            return state

        # Extrair número do cliente (remover @s.whatsapp.net)
        cliente_numero = extrair_numero_whatsapp(remote_jid)

        # Extrair conteúdo da mensagem
        message_obj = data.get("message", {})
        mensagem_base64 = None

        # Tentar extrair de diferentes campos dependendo do tipo
        if message_type == "conversation":
            mensagem_base64 = message_obj.get("conversation", "")
        elif message_type == "extendedTextMessage":
            mensagem_base64 = message_obj.get("extendedTextMessage", {}).get("text", "")
        elif message_type == "imageMessage":
            mensagem_base64 = message_obj.get("imageMessage", {})
        elif message_type == "audioMessage":
            mensagem_base64 = message_obj.get("audioMessage", {})
        elif message_type == "videoMessage":
            mensagem_base64 = message_obj.get("videoMessage", {})
        else:
            # Para outros tipos, tentar pegar qualquer conteúdo
            mensagem_base64 = message_obj

        # Atualizar estado com dados extraídos
        state["cliente_numero"] = cliente_numero
        state["cliente_nome"] = push_name
        state["mensagem_tipo"] = message_type
        state["mensagem_id"] = message_id
        state["mensagem_from_me"] = from_me
        state["mensagem_timestamp"] = message_timestamp
        state["mensagem_base64"] = mensagem_base64

        # Definir próxima ação
        state["next_action"] = AcaoFluxo.VERIFICAR_CLIENTE.value

        logger.info("Webhook validado com sucesso")
        logger.info(f"  Cliente número: {cliente_numero}")
        logger.info(f"  Cliente nome: {push_name}")
        logger.info(f"  Tipo mensagem: {message_type}")
        logger.info(f"  Próxima ação: {state['next_action']}")

        return state

    except Exception as e:
        logger.error(f"Erro ao validar webhook: {e}", exc_info=True)
        state["erro"] = f"Erro ao validar webhook: {str(e)}"
        state["erro_detalhes"] = {"exception": str(e)}
        state["next_action"] = AcaoFluxo.END.value
        return state


async def verificar_cliente(state: AgentState) -> AgentState:
    """
    Verifica se o cliente já está cadastrado no Supabase.

    Busca o cliente no banco de dados pelo número de telefone.
    Se encontrado, atualiza o estado com os dados do cliente.
    Se não encontrado, marca para cadastro.

    Args:
        state: Estado atual do agente contendo cliente_numero

    Returns:
        AgentState: Estado atualizado com dados do cliente (se encontrado)

    Example:
        >>> state = {
        ...     "cliente_numero": "5562999999999",
        ...     "next_action": ""
        ... }
        >>> state = await verificar_cliente(state)
        >>> if state["cliente_existe"]:
        ...     print(f"Cliente ID: {state['cliente_id']}")
    """
    try:
        logger.info("=" * 60)
        logger.info("Verificando cliente no banco de dados")
        logger.info("=" * 60)

        cliente_numero = state.get("cliente_numero")

        if not cliente_numero:
            logger.error("cliente_numero não encontrado no state")
            state["erro"] = "Número do cliente não encontrado"
            state["next_action"] = AcaoFluxo.END.value
            return state

        # Carregar configurações
        settings = get_settings()

        # Instanciar SupabaseClient
        logger.info("Conectando ao Supabase...")
        supabase = criar_supabase_client(
            url=settings.supabase_url,
            key=settings.supabase_key
        )

        # Buscar cliente
        logger.info(f"Buscando cliente: {cliente_numero}")
        cliente = await supabase.buscar_cliente(cliente_numero)

        if cliente:
            # Cliente encontrado
            logger.info(f"Cliente encontrado no banco de dados")
            logger.info(f"  ID: {cliente.get('id')}")
            logger.info(f"  Nome: {cliente.get('nome_lead')}")

            state["cliente_existe"] = True
            state["cliente_id"] = cliente.get("id")
            state["cliente_ultima_mensagem"] = cliente.get("updated_at")

            # Próxima ação: processar mídia
            state["next_action"] = AcaoFluxo.PROCESSAR_MIDIA.value

            logger.info(f"Próxima ação: {state['next_action']}")

        else:
            # Cliente não encontrado
            logger.info(f"Cliente NÃO encontrado no banco de dados")
            logger.info("Cliente será cadastrado")

            state["cliente_existe"] = False
            state["cliente_id"] = None

            # Próxima ação: cadastrar cliente
            state["next_action"] = AcaoFluxo.CADASTRAR_CLIENTE.value

            logger.info(f"Próxima ação: {state['next_action']}")

        return state

    except Exception as e:
        logger.error(f"Erro ao verificar cliente: {e}", exc_info=True)
        state["erro"] = f"Erro ao verificar cliente: {str(e)}"
        state["erro_detalhes"] = {"exception": str(e)}
        state["next_action"] = AcaoFluxo.END.value
        return state


async def cadastrar_cliente(state: AgentState) -> AgentState:
    """
    Cadastra um novo cliente no Supabase.

    Cria um novo registro de cliente com os dados extraídos do webhook.

    Args:
        state: Estado atual do agente contendo dados do cliente

    Returns:
        AgentState: Estado atualizado com cliente_id do novo cliente

    Example:
        >>> state = {
        ...     "cliente_nome": "João Silva",
        ...     "cliente_numero": "5562999999999",
        ...     "mensagem_base64": "Olá",
        ...     "mensagem_tipo": "conversation"
        ... }
        >>> state = await cadastrar_cliente(state)
        >>> print(f"Cliente cadastrado: ID {state['cliente_id']}")
    """
    try:
        logger.info("=" * 60)
        logger.info("Cadastrando novo cliente")
        logger.info("=" * 60)

        # Validar campos obrigatórios
        campos_necessarios = ["cliente_nome", "cliente_numero", "mensagem_tipo"]
        for campo in campos_necessarios:
            if not state.get(campo):
                logger.error(f"Campo obrigatório ausente: {campo}")
                state["erro"] = f"Campo obrigatório ausente: {campo}"
                state["next_action"] = AcaoFluxo.END.value
                return state

        # Extrair dados do estado
        nome_lead = state["cliente_nome"]
        phone_numero = state["cliente_numero"]
        message = state.get("mensagem_base64", "")
        tipo_mensagem = state["mensagem_tipo"]

        # Converter mensagem para string se for dict
        if isinstance(message, dict):
            # Para mídia, apenas indicar o tipo
            message = f"[{tipo_mensagem}]"
        elif not isinstance(message, str):
            message = str(message)

        logger.info(f"Dados do novo cliente:")
        logger.info(f"  Nome: {nome_lead}")
        logger.info(f"  Telefone: {phone_numero}")
        logger.info(f"  Tipo mensagem: {tipo_mensagem}")

        # Carregar configurações
        settings = get_settings()

        # Instanciar SupabaseClient
        logger.info("Conectando ao Supabase...")
        supabase = criar_supabase_client(
            url=settings.supabase_url,
            key=settings.supabase_key
        )

        # Preparar dados para cadastro
        dados_cliente = {
            "nome_lead": nome_lead,
            "phone_numero": phone_numero,
            "message": message,
            "tipo_mensagem": tipo_mensagem
        }

        # Cadastrar cliente
        logger.info("Cadastrando cliente no banco de dados...")
        resultado = await supabase.cadastrar_cliente(dados_cliente)

        # Atualizar estado
        state["cliente_id"] = resultado.get("id")
        state["cliente_existe"] = True

        logger.info(f"Cliente cadastrado com sucesso!")
        logger.info(f"  ID: {state['cliente_id']}")

        # Próxima ação: voltar para verificar cliente (para confirmar cadastro)
        state["next_action"] = AcaoFluxo.VERIFICAR_CLIENTE.value

        logger.info(f"Próxima ação: {state['next_action']}")
        logger.info("Retornando para verificação do cliente recém-cadastrado...")

        return state

    except Exception as e:
        logger.error(f"Erro ao cadastrar cliente: {e}", exc_info=True)
        state["erro"] = f"Erro ao cadastrar cliente: {str(e)}"
        state["erro_detalhes"] = {"exception": str(e)}
        state["next_action"] = AcaoFluxo.END.value
        return state


# ========== EXPORTAÇÕES ==========

__all__ = [
    "validar_webhook",
    "verificar_cliente",
    "cadastrar_cliente",
]
