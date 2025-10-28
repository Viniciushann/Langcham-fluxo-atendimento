"""
Nós de processamento de mídia - Áudio, Imagem e Texto.

Este módulo contém os nós responsáveis por processar diferentes tipos de mídia
recebidos via WhatsApp, incluindo transcrição de áudio, análise de imagem e
processamento de texto.

CORREÇÕES APLICADAS:
1. Melhor extração de base64 do webhook da Evolution API
2. Tratamento de diferentes formatos de webhook
3. Remoção de emojis para evitar erros de encoding
4. Fallback melhorado quando API não disponibiliza mídia
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
            logger.info("Direcionando para processamento de audio")
            return "processar_audio"
        elif mensagem_tipo == "imageMessage":
            logger.info("Direcionando para processamento de imagem")
            return "processar_imagem"
        elif mensagem_tipo == "conversation":
            logger.info("Direcionando para processamento de texto")
            return "processar_texto"
        else:
            logger.info(f"Tipo '{mensagem_tipo}' nao reconhecido, direcionando para texto")
            return "processar_texto"
            
    except Exception as e:
        logger.error(f"Erro ao rotear tipo de mensagem: {e}", exc_info=True)
        return "processar_texto"


def _extrair_base64_do_webhook(webhook_data: Dict[str, Any], tipo_mensagem: str) -> tuple[str | None, str | None]:
    """
    Função auxiliar para extrair base64 do webhook da Evolution API.
    
    Tenta múltiplas localizações possíveis onde o base64 pode estar.
    
    Args:
        webhook_data: Dados completos do webhook
        tipo_mensagem: Tipo da mensagem (audioMessage, imageMessage, etc)
        
    Returns:
        Tupla (base64_data, mimetype) ou (None, None) se não encontrado
    """
    try:
        body = webhook_data.get("body", {})
        data = body.get("data", {})
        message_obj = data.get("message", {})
        
        # Nome da chave do tipo de mensagem (ex: "audioMessage", "imageMessage")
        tipo_key = tipo_mensagem
        media_msg = message_obj.get(tipo_key, {})
        
        logger.info(f"=== EXTRAINDO BASE64 DO WEBHOOK ===")
        logger.info(f"Tipo mensagem: {tipo_mensagem}")
        logger.info(f"Keys no {tipo_key}: {list(media_msg.keys())}")
        logger.info(f"Keys no message: {list(message_obj.keys())}")
        logger.info(f"Keys no data: {list(data.keys())}")
        
        base64_data = None
        mimetype = None
        
        # PRIORIDADE 1: Dentro do objeto específico da mídia (mais comum)
        # Ex: data.message.audioMessage.media ou .base64
        if tipo_key in message_obj:
            media_obj = message_obj[tipo_key]
            
            # Tentar "media"
            if isinstance(media_obj, dict) and "media" in media_obj:
                base64_data = media_obj["media"]
                mimetype = media_obj.get("mimetype")
                logger.info(f"[OK] Base64 encontrado em message.{tipo_key}.media")
                
            # Tentar "base64"
            elif isinstance(media_obj, dict) and "base64" in media_obj:
                base64_data = media_obj["base64"]
                mimetype = media_obj.get("mimetype")
                logger.info(f"[OK] Base64 encontrado em message.{tipo_key}.base64")
        
        # PRIORIDADE 2: Diretamente no message
        if not base64_data:
            if "media" in message_obj:
                base64_data = message_obj["media"]
                mimetype = message_obj.get("mimetype")
                logger.info("[OK] Base64 encontrado em message.media")
                
            elif "base64" in message_obj:
                base64_data = message_obj["base64"]
                mimetype = message_obj.get("mimetype")
                logger.info("[OK] Base64 encontrado em message.base64")
        
        # PRIORIDADE 3: No data
        if not base64_data:
            if "media" in data:
                base64_data = data["media"]
                mimetype = data.get("mimetype")
                logger.info("[OK] Base64 encontrado em data.media")
                
            elif "base64" in data:
                base64_data = data["base64"]
                mimetype = data.get("mimetype")
                logger.info("[OK] Base64 encontrado em data.base64")
        
        # PRIORIDADE 4: Verificar se está em "mediaData" (algumas versões da Evolution)
        if not base64_data and "mediaData" in data:
            base64_data = data["mediaData"]
            mimetype = data.get("mimetype")
            logger.info("[OK] Base64 encontrado em data.mediaData")
        
        if base64_data:
            logger.info(f"Base64 extraido com sucesso (tamanho: {len(base64_data) if base64_data else 0} chars)")
            logger.info(f"Mimetype: {mimetype}")
        else:
            logger.warning("[AVISO] Base64 NAO encontrado no webhook")
            logger.info("Estrutura completa do webhook para debug:")
            logger.info(f"Body keys: {list(body.keys())}")
            logger.info(f"Data keys: {list(data.keys())}")
            logger.info(f"Message keys: {list(message_obj.keys())}")
            if tipo_key in message_obj:
                logger.info(f"{tipo_key} keys: {list(message_obj[tipo_key].keys())}")
        
        return base64_data, mimetype
        
    except Exception as e:
        logger.error(f"Erro ao extrair base64 do webhook: {e}", exc_info=True)
        return None, None


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
        logger.info("Processando audio com Whisper")
        logger.info("=" * 60)
        
        # Carregar configurações
        settings = get_settings()
        
        # Extrair dados do webhook
        webhook_data = state.get("raw_webhook_data", {})
        
        # PASSO 1: Tentar extrair base64 do webhook
        base64_audio, mimetype = _extrair_base64_do_webhook(webhook_data, "audioMessage")
        
        media = None
        
        if base64_audio:
            # Base64 encontrado no webhook
            media = {
                "base64": base64_audio,
                "mimetype": mimetype or "audio/ogg"
            }
            logger.info("Usando base64 do webhook")
            
        else:
            # PASSO 2: Tentar buscar via API (fallback)
            logger.warning("Base64 nao encontrado no webhook, tentando API...")
            
            # Extrair message_id
            body = webhook_data.get("body", {})
            data = body.get("data", {})
            key = data.get("key", {})
            message_id = key.get("id", "")
            
            if not message_id:
                logger.error("Message ID nao encontrado")
                raise ValueError("Message ID nao encontrado e base64 nao esta no webhook")
            
            # Instanciar WhatsAppClient
            whatsapp = criar_whatsapp_client(
                base_url=settings.whatsapp_api_url,
                api_key=settings.whatsapp_api_key,
                instance=settings.whatsapp_instance
            )
            
            logger.info(f"Tentando buscar midia via API: {message_id}")
            
            try:
                media = await whatsapp.obter_media_base64(message_id)
            except ValueError as api_error:
                # Mídia expirada ou não encontrada
                logger.warning(f"Midia expirada ou nao encontrada: {api_error}")

                erro_msg = "Oi! Parece que voce enviou um audio, mas ele expirou antes de eu conseguir processar. Por favor, envie novamente ou escreva sua mensagem em texto. Obrigado!"
                state["mensagem_transcrita"] = erro_msg
                state["mensagem_conteudo"] = erro_msg
                state["texto_processado"] = erro_msg
                state["erro"] = f"Erro ao processar audio: {str(api_error)}"

                logger.warning("Midia expirada - solicitando reenvio")
                return state
            except Exception as api_error:
                logger.error(f"Erro inesperado ao buscar midia via API: {api_error}")

                # Se a API falhar por outro motivo
                erro_msg = "Desculpe, nao consegui processar o audio no momento. Pode tentar enviar novamente ou escrever em texto?"
                state["mensagem_transcrita"] = erro_msg
                state["mensagem_conteudo"] = erro_msg
                state["texto_processado"] = erro_msg
                state["erro"] = f"Erro ao processar audio: {str(api_error)}"

                logger.error("Falha ao obter audio - usando mensagem de fallback")
                return state
        
        if not media or "base64" not in media:
            logger.error("Falha ao obter midia em base64")
            raise ValueError("Midia nao encontrada no webhook nem via API")
            
        # Converter base64 para bytes
        audio_bytes = base64.b64decode(media["base64"])
        logger.info(f"Audio decodificado: {len(audio_bytes)} bytes")
        
        # Criar arquivo temporário
        with tempfile.NamedTemporaryFile(suffix=".ogg", delete=False) as temp:
            temp_file = temp.name
            temp.write(audio_bytes)
            
        logger.info(f"Arquivo temporario criado: {temp_file}")
        
        # Usar OpenAI Whisper para transcrever
        from openai import AsyncOpenAI
        client = AsyncOpenAI(api_key=settings.openai_api_key)
        
        logger.info("Iniciando transcricao com Whisper...")
        
        with open(temp_file, "rb") as audio_file:
            transcript = await client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="pt"  # Português
            )
            
        texto_transcrito = transcript.text
        logger.info(f"Transcricao concluida: {texto_transcrito[:100]}...")

        # Atualizar estado
        state["mensagem_transcrita"] = texto_transcrito
        state["mensagem_conteudo"] = texto_transcrito
        state["texto_processado"] = texto_transcrito  # IMPORTANTE: Salvar para o agente

        logger.info("Audio processado com sucesso")
        logger.info("Direcionando para agente...")
        
        return state
        
    except Exception as e:
        logger.error(f"Erro ao processar audio: {e}", exc_info=True)

        # Em caso de erro, usar texto padrão amigável
        erro_msg = "Oi! Parece que teve um problema ao enviar ou processar o audio. Se for algo importante, voce pode tentar enviar novamente ou escrever como texto?"
        state["mensagem_transcrita"] = erro_msg
        state["mensagem_conteudo"] = erro_msg
        state["texto_processado"] = erro_msg
        state["erro"] = f"Erro ao processar audio: {str(e)}"

        logger.info("Usando mensagem de erro amigavel para o cliente")
        
        return state
        
    finally:
        # Limpar arquivo temporário
        if temp_file and os.path.exists(temp_file):
            try:
                os.unlink(temp_file)
                logger.info("Arquivo temporario removido")
            except Exception as e:
                logger.warning(f"Erro ao remover arquivo temporario: {e}")


async def processar_imagem(state: AgentState) -> AgentState:
    """
    Processa mensagens de imagem usando GPT-4 Vision.
    
    Baixa a imagem do WhatsApp e usa GPT-4 Vision para descrever
    o conteúdo da imagem.
    
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
        "te enviei uma imagem que mostra..."
    """
    try:
        logger.info("=" * 60)
        logger.info("Processando imagem com GPT-4 Vision")
        logger.info("=" * 60)
        
        # Carregar configurações
        settings = get_settings()
        
        # Extrair dados do webhook
        webhook_data = state.get("raw_webhook_data", {})
        
        # PASSO 1: Tentar extrair base64 do webhook
        base64_image, mimetype = _extrair_base64_do_webhook(webhook_data, "imageMessage")
        
        media = None
        
        if base64_image:
            # Base64 encontrado no webhook
            media = {
                "base64": base64_image,
                "mimetype": mimetype or "image/jpeg"
            }
            logger.info("Usando base64 do webhook")
            
        else:
            # PASSO 2: Tentar buscar via API (fallback)
            logger.warning("Base64 nao encontrado no webhook, tentando API...")
            
            # Extrair message_id
            body = webhook_data.get("body", {})
            data = body.get("data", {})
            key = data.get("key", {})
            message_id = key.get("id", "")
            
            if not message_id:
                logger.error("Message ID nao encontrado")
                raise ValueError("Message ID nao encontrado e base64 nao esta no webhook")
            
            # Instanciar WhatsAppClient
            whatsapp = criar_whatsapp_client(
                base_url=settings.whatsapp_api_url,
                api_key=settings.whatsapp_api_key,
                instance=settings.whatsapp_instance
            )
            
            logger.info(f"Tentando buscar midia via API: {message_id}")
            
            try:
                media = await whatsapp.obter_media_base64(message_id)
            except Exception as api_error:
                logger.error(f"Erro ao buscar midia via API: {api_error}")
                
                # Se a API falhar, informar que não conseguimos processar
                erro_msg = "Desculpe, nao consegui processar a imagem. Pode descrever o que precisa?"
                state["mensagem_transcrita"] = erro_msg
                state["mensagem_conteudo"] = erro_msg
                state["texto_processado"] = erro_msg
                state["erro"] = f"Erro ao processar imagem: {str(api_error)}"
                
                logger.error("Falha ao obter imagem - usando mensagem de fallback")
                return state
        
        if not media or "base64" not in media:
            logger.error("Falha ao obter midia em base64")
            raise ValueError("Midia nao encontrada no webhook nem via API")

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
        
        logger.info("Iniciando analise da imagem com GPT-4 Vision...")
        
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
        
        logger.info(f"Analise da imagem concluida: {descricao_imagem[:100]}...")

        # Atualizar estado
        state["mensagem_transcrita"] = descricao_imagem
        state["mensagem_conteudo"] = descricao_imagem
        state["texto_processado"] = descricao_imagem  # IMPORTANTE: Salvar para o agente

        logger.info("Imagem processada com sucesso")
        logger.info("Direcionando para agente...")
        
        return state
        
    except Exception as e:
        logger.error(f"Erro ao processar imagem: {e}", exc_info=True)

        # Em caso de erro, usar texto padrão amigável
        erro_msg = "Oi! Parece que teve um problema ao processar a imagem. Pode descrever o que precisa ou tentar enviar novamente?"
        state["mensagem_transcrita"] = erro_msg
        state["mensagem_conteudo"] = erro_msg
        state["texto_processado"] = erro_msg
        state["erro"] = f"Erro ao processar imagem: {str(e)}"

        logger.info("Usando mensagem de erro amigavel para o cliente")

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
