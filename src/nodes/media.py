"""
Nós de processamento de mídia - Áudio, Imagem e Texto.

Este módulo contém os nós responsáveis por processar diferentes tipos de mídia
recebidos via WhatsApp, incluindo transcrição de áudio, análise de imagem e
processamento de texto.
"""

from __future__ import annotations

import base64
import logging
import tempfile
import os
from typing import Dict, Any

from src.models.state import AgentState, AcaoFluxo
from src.clients.whatsapp_client import criar_whatsapp_client
from src.config.settings import get_settings

logger = logging.getLogger(__name__)


def rotear_tipo_mensagem(state: AgentState) -> str:
    """
    Rota para o nó correto baseado no tipo de mensagem.
    
    Analisa o tipo de mensagem no estado e determina qual função
    de processamento deve ser chamada.
    
    Args:
        state: Estado atual do agente contendo mensagem_tipo
        
    Returns:
        str: Nome da função para processar ("processar_audio", "processar_imagem", "processar_texto")
        
    Example:
        >>> state = {"mensagem_tipo": "audioMessage"}
        >>> rotear_tipo_mensagem(state)
        "processar_audio"
    """
    try:
        logger.info("=" * 60)
        logger.info("Roteando tipo de mensagem")
        logger.info("=" * 60)
        
        mensagem_tipo = state.get("mensagem_tipo", "")
        logger.info(f"Tipo de mensagem detectado: {mensagem_tipo}")
        
        if mensagem_tipo == "audioMessage":
            logger.info("Direcionando para processamento de áudio")
            return "processar_audio"
        elif mensagem_tipo == "imageMessage":
            logger.info("Direcionando para processamento de imagem")
            return "processar_imagem"
        elif mensagem_tipo == "conversation":
            logger.info("Direcionando para processamento de texto")
            return "processar_texto"
        else:
            logger.info(f"Tipo '{mensagem_tipo}' não reconhecido, direcionando para texto")
            return "processar_texto"
            
    except Exception as e:
        logger.error(f"Erro ao rotear tipo de mensagem: {e}", exc_info=True)
        return "processar_texto"


async def processar_audio(state: AgentState) -> AgentState:
    """
    Processa mensagens de áudio usando OpenAI Whisper.
    
    Baixa o áudio do WhatsApp, salva temporariamente e usa o Whisper
    para fazer a transcrição do áudio para texto.
    
    Args:
        state: Estado atual do agente contendo raw_webhook_data
        
    Returns:
        AgentState: Estado atualizado com mensagem_transcrita e mensagem_conteudo
        
    Example:
        >>> state = {
        ...     "raw_webhook_data": webhook_data,
        ...     "mensagem_tipo": "audioMessage"
        ... }
        >>> state = await processar_audio(state)
        >>> print(state["mensagem_conteudo"])
        "Olá, gostaria de agendar uma consulta"
    """
    temp_file = None
    
    try:
        logger.info("=" * 60)
        logger.info("Processando áudio com Whisper")
        logger.info("=" * 60)
        
        # Carregar configurações
        settings = get_settings()
        
        # Instanciar WhatsAppClient
        whatsapp = criar_whatsapp_client(
            base_url=settings.whatsapp_api_url,
            api_key=settings.whatsapp_api_key,
            instance=settings.whatsapp_instance
        )
        
        # Extrair message_id do webhook
        webhook_data = state.get("raw_webhook_data", {})
        body = webhook_data.get("body", {})
        data = body.get("data", {})
        key = data.get("key", {})
        message_id = key.get("id", "")
        
        if not message_id:
            logger.error("Message ID não encontrado no webhook")
            raise ValueError("Message ID não encontrado")
            
        logger.info(f"Obtendo áudio para message_id: {message_id}")
        
        # Obter áudio em base64
        media = await whatsapp.obter_media_base64(message_id)
        
        if not media or "base64" not in media:
            logger.error("Falha ao obter mídia em base64")
            raise ValueError("Mídia não encontrada")
            
        # Converter base64 para bytes
        audio_bytes = base64.b64decode(media["base64"])
        logger.info(f"Áudio decodificado: {len(audio_bytes)} bytes")
        
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp:
            temp_file = temp.name
            temp.write(audio_bytes)
            
        logger.info(f"Arquivo temporário criado: {temp_file}")
        
        # Usar OpenAI Whisper para transcrever
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        logger.info("Iniciando transcrição com Whisper...")
        
        with open(temp_file, "rb") as audio_file:
            transcript = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="pt"  # Português
            )
            
        texto_transcrito = transcript.text
        logger.info(f"Transcrição concluída: {texto_transcrito[:100]}...")

        # Atualizar estado
        state["mensagem_transcrita"] = texto_transcrito
        state["mensagem_conteudo"] = texto_transcrito
        state["texto_processado"] = texto_transcrito  # IMPORTANTE: Salvar para o agente

        logger.info("Áudio processado com sucesso")
        logger.info("Direcionando para agente...")
        
        return state
        
    except Exception as e:
        logger.error(f"Erro ao processar áudio: {e}", exc_info=True)

        # Em caso de erro, usar texto padrão
        erro_msg = "Erro ao processar mídia de áudio"
        state["mensagem_transcrita"] = erro_msg
        state["mensagem_conteudo"] = erro_msg
        state["texto_processado"] = erro_msg
        state["erro"] = f"Erro ao processar áudio: {str(e)}"

        return state
        
    finally:
        # Limpar arquivo temporário
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
                logger.info(f"Arquivo temporário removido: {temp_file}")
            except Exception as e:
                logger.warning(f"Falha ao remover arquivo temporário: {e}")


async def processar_imagem(state: AgentState) -> AgentState:
    """
    Processa mensagens de imagem usando GPT-4 Vision.
    
    Baixa a imagem do WhatsApp e usa o GPT-4o para analisar e descrever
    o conteúdo da imagem como se fosse o cliente descrevendo.
    
    Args:
        state: Estado atual do agente contendo raw_webhook_data
        
    Returns:
        AgentState: Estado atualizado com mensagem_transcrita e mensagem_conteudo
        
    Example:
        >>> state = {
        ...     "raw_webhook_data": webhook_data,
        ...     "mensagem_tipo": "imageMessage"
        ... }
        >>> state = await processar_imagem(state)
        >>> print(state["mensagem_conteudo"])
        "te enviei uma imagem que mostra um problema no encanamento..."
    """
    try:
        logger.info("=" * 60)
        logger.info("Processando imagem com GPT-4 Vision")
        logger.info("=" * 60)
        
        # Carregar configurações
        settings = get_settings()
        
        # Instanciar WhatsAppClient
        whatsapp = criar_whatsapp_client(
            base_url=settings.whatsapp_api_url,
            api_key=settings.whatsapp_api_key,
            instance=settings.whatsapp_instance
        )
        
        # Extrair message_id do webhook
        webhook_data = state.get("raw_webhook_data", {})
        body = webhook_data.get("body", {})
        data = body.get("data", {})
        key = data.get("key", {})
        message_id = key.get("id", "")
        
        if not message_id:
            logger.error("Message ID não encontrado no webhook")
            raise ValueError("Message ID não encontrado")
            
        logger.info(f"Obtendo imagem para message_id: {message_id}")
        
        # Obter imagem em base64
        media = await whatsapp.obter_media_base64(message_id)
        
        if not media or "base64" not in media:
            logger.error("Falha ao obter mídia em base64")
            raise ValueError("Mídia não encontrada")
            
        base64_data = media["base64"]
        logger.info(f"Imagem obtida: {len(base64_data)} caracteres base64")
        
        # Usar GPT-4 Vision para descrever
        from langchain_openai import ChatOpenAI
        
        llm = ChatOpenAI(
            model="gpt-4o-2024-11-20",
            api_key=settings.openai_api_key,
            temperature=0.7
        )
        
        prompt = """O que há nessa imagem? Me dê a resposta como se fosse um cliente 
        descrevendo a imagem. Comece dizendo: "te enviei uma imagem que..." 
        Sempre em primeira pessoa, como se você fosse o cliente. 
        Ao invés de dizer 'você me enviou', diga 'eu te enviei'.
        
        Seja detalhado e útil na descrição, mas mantenha o tom natural de um cliente 
        conversando via WhatsApp."""
        
        logger.info("Iniciando análise da imagem com GPT-4 Vision...")
        
        messages = [
            {
                "type": "text", 
                "text": prompt
            },
            {
                "type": "image_url", 
                "image_url": {
                    "url": f"data:image/jpeg;base64,{base64_data}"
                }
            }
        ]
        
        response = await llm.ainvoke(messages)
        descricao_imagem = response.content
        
        logger.info(f"Análise da imagem concluída: {descricao_imagem[:100]}...")

        # Atualizar estado
        state["mensagem_transcrita"] = descricao_imagem
        state["mensagem_conteudo"] = descricao_imagem
        state["texto_processado"] = descricao_imagem  # IMPORTANTE: Salvar para o agente

        logger.info("Imagem processada com sucesso")
        logger.info("Direcionando para agente...")
        
        return state
        
    except Exception as e:
        logger.error(f"Erro ao processar imagem: {e}", exc_info=True)

        # Em caso de erro, usar texto padrão
        erro_msg = "Erro ao processar mídia de imagem"
        state["mensagem_transcrita"] = erro_msg
        state["mensagem_conteudo"] = erro_msg
        state["texto_processado"] = erro_msg
        state["erro"] = f"Erro ao processar imagem: {str(e)}"

        return state


async def processar_texto(state: AgentState) -> AgentState:
    """
    Processa mensagens de texto simples.
    
    Para mensagens de texto, simplesmente copia o conteúdo da mensagem
    para os campos apropriados no estado.
    
    Args:
        state: Estado atual do agente contendo mensagem_base64
        
    Returns:
        AgentState: Estado atualizado com mensagem_transcrita e mensagem_conteudo
        
    Example:
        >>> state = {
        ...     "mensagem_base64": "Olá, preciso de ajuda",
        ...     "mensagem_tipo": "conversation"
        ... }
        >>> state = await processar_texto(state)
        >>> print(state["mensagem_conteudo"])
        "Olá, preciso de ajuda"
    """
    try:
        logger.info("=" * 60)
        logger.info("Processando mensagem de texto")
        logger.info("=" * 60)
        
        mensagem_base64 = state.get("mensagem_base64", "")
        
        # Para mensagem de texto, o conteúdo já está disponível
        if isinstance(mensagem_base64, str):
            conteudo = mensagem_base64
        else:
            # Se for um objeto (outras mídias), converter para string
            conteudo = str(mensagem_base64)
            
        logger.info(f"Texto processado: {conteudo[:100]}...")

        # Atualizar estado
        state["mensagem_conteudo"] = conteudo
        state["mensagem_transcrita"] = conteudo
        state["texto_processado"] = conteudo  # IMPORTANTE: Salvar para o agente
        # next_action não precisa ser definido - o workflow já tem edge direto para agente

        logger.info("Texto processado com sucesso")
        logger.info("Direcionando para agente...")
        
        return state
        
    except Exception as e:
        logger.error(f"Erro ao processar texto: {e}", exc_info=True)

        # Em caso de erro, usar texto padrão
        erro_msg = "Erro ao processar mensagem de texto"
        state["mensagem_transcrita"] = erro_msg
        state["mensagem_conteudo"] = erro_msg
        state["texto_processado"] = erro_msg
        state["erro"] = f"Erro ao processar texto: {str(e)}"

        return state


# ========== EXPORTAÇÕES ==========

__all__ = [
    "rotear_tipo_mensagem",
    "processar_audio",
    "processar_imagem", 
    "processar_texto",
]