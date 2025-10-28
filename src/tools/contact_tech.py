"""
Módulo para contato direto com o técnico.

Permite que o bot encaminhe solicitações urgentes ou específicas
diretamente para o técnico via WhatsApp.

Autor: Sistema WhatsApp Bot
Data: 2025-10-28
"""

import logging
from typing import Dict, Any

from langchain.tools import tool

from src.clients.whatsapp_client import WhatsAppClient
from src.config.settings import get_settings

# Configuração de logging
logger = logging.getLogger(__name__)

# Configuração do técnico
TELEFONE_TECNICO = "556298540075"  # +55 62 98540-0075


@tool
async def contatar_tecnico_tool(
    nome_cliente: str,
    telefone_cliente: str,
    assunto: str,
    mensagem_cliente: str = ""
) -> Dict[str, Any]:
    """
    Envia uma mensagem direta para o técnico sobre uma solicitação do cliente.

    Use esta ferramenta quando:
    - Cliente quer falar diretamente com o técnico
    - Situação urgente que requer atenção imediata
    - Problema técnico complexo que você não consegue resolver
    - Cliente solicita orçamento muito específico ou personalizado

    Args:
        nome_cliente: Nome completo do cliente
        telefone_cliente: Telefone do cliente com DDD
        assunto: Motivo do contato (ex: "orçamento urgente", "dúvida técnica", "falar com técnico")
        mensagem_cliente: Mensagem ou contexto adicional do cliente (opcional)

    Returns:
        Dict: {
            "sucesso": bool,
            "mensagem": str - Mensagem de confirmação para o cliente
        }

    Example:
        >>> resultado = await contatar_tecnico_tool(
        ...     nome_cliente="João Silva",
        ...     telefone_cliente="5511987654321",
        ...     assunto="orçamento urgente",
        ...     mensagem_cliente="Cliente precisa instalar drywall em 3 dias"
        ... )
    """
    try:
        logger.info(f"Solicitação de contato com técnico - Cliente: {nome_cliente}")

        settings = get_settings()
        whatsapp = WhatsAppClient(
            base_url=settings.whatsapp_api_url,
            api_key=settings.whatsapp_api_key,
            instance=settings.whatsapp_instance
        )

        # Montar mensagem para o técnico
        mensagem_tecnico = f"""📞 SOLICITAÇÃO DE CONTATO

👤 Cliente: {nome_cliente}
📱 Telefone: {telefone_cliente}
📋 Assunto: {assunto}"""

        if mensagem_cliente:
            mensagem_tecnico += f"""

💬 Mensagem do cliente:
{mensagem_cliente}"""

        mensagem_tecnico += """

⚠️ Cliente solicitou falar com você. Entre em contato o mais breve possível!"""

        # Enviar mensagem para o técnico
        resultado = await whatsapp.enviar_mensagem(
            telefone=TELEFONE_TECNICO,
            texto=mensagem_tecnico
        )

        if resultado:
            logger.info(f"Solicitação de contato enviada ao técnico para cliente {nome_cliente}")
            return {
                "sucesso": True,
                "mensagem": f"Perfeito! Já encaminhei sua solicitação para nosso técnico. Ele entrará em contato com você no telefone {telefone_cliente} o mais breve possível. Geralmente respondemos em até 1 hora durante horário comercial."
            }
        else:
            logger.warning(f"Falha ao enviar solicitação de contato para {nome_cliente}")
            return {
                "sucesso": False,
                "mensagem": "Desculpe, tive um problema ao encaminhar sua solicitação. Por favor, você pode ligar diretamente para (62) 98540-0075 e falar com nosso técnico?"
            }

    except Exception as e:
        logger.error(f"Erro ao contatar técnico: {e}", exc_info=True)
        return {
            "sucesso": False,
            "mensagem": "Desculpe, tive um problema ao encaminhar sua solicitação. Por favor, você pode ligar diretamente para (62) 98540-0075 e falar com nosso técnico?"
        }
