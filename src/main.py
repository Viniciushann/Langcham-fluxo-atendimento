"""
API FastAPI para WhatsApp Bot com LangGraph.

Este módulo contém a aplicação principal FastAPI que recebe webhooks
da Evolution API e processa mensagens através do sistema de bot.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import asyncio
from datetime import datetime
from typing import Dict, Any
import json

# Imports do projeto
from src.config.settings import get_settings
from src.models.state import AgentState
from src.graph.workflow import criar_grafo_atendimento

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar configurações
settings = get_settings()

# ========== CRIAR GRAFO (SINGLETON) ==========
logger.info("Criando grafo de atendimento...")
grafo_atendimento = criar_grafo_atendimento()
logger.info("Grafo criado e pronto!")

# Criar aplicação FastAPI
app = FastAPI(
    title="WhatsApp Bot LangGraph",
    description="Bot inteligente de WhatsApp com processamento de múltiplas mídias",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Endpoint raiz - Health check básico."""
    return {
        "message": "WhatsApp Bot LangGraph API",
        "status": "running",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }


@app.get("/health")
async def health_check():
    """Endpoint de health check detalhado."""
    try:
        return {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "environment": settings.environment,
            "whatsapp_instance": settings.whatsapp_instance,
            "bot_number": settings.bot_phone_number,
            "services": {
                "fastapi": "✅ Running",
                "whatsapp_api": "✅ Configured", 
                "openai": "✅ Configured" if settings.openai_api_key else "❌ Missing",
                "supabase": "✅ Configured" if settings.supabase_url else "❌ Missing"
            }
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={"status": "unhealthy", "error": str(e)}
        )


async def processar_mensagem(state: AgentState):
    """
    Processa a mensagem através do grafo LangGraph.
    Executado em background.
    """
    try:
        logger.info("=" * 60)
        logger.info("Iniciando processamento da mensagem via GRAFO")
        logger.info("=" * 60)

        # Executar grafo
        final_state = await grafo_atendimento.ainvoke(state)

        # Logging do resultado
        if final_state.get("erro"):
            logger.error(f"Erro no processamento: {final_state['erro']}")
        else:
            logger.info(f"Processamento concluído com sucesso")
            logger.info(f"Cliente: {final_state.get('cliente_nome')}")
            logger.info(f"Respostas enviadas: {len(final_state.get('respostas_fragmentadas', []))}")

        logger.info("=" * 60)

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}", exc_info=True)


@app.post("/webhook/whatsapp")
async def webhook_whatsapp(
    request: Request,
    background_tasks: BackgroundTasks,
    webhook_data: Dict[str, Any] = None
):
    """
    Endpoint principal para receber webhooks da Evolution API.
    
    Este endpoint recebe as mensagens enviadas para o bot via WhatsApp
    e processa em background para não bloquear a resposta.
    """
    try:
        # Se não veio no body, pegar do request
        if webhook_data is None:
            webhook_data = await request.json()
            
        logger.info("📨 Webhook recebido!")
        logger.info(f"Event: {webhook_data.get('event', 'unknown')}")
        logger.info(f"Instance: {webhook_data.get('instance', 'unknown')}")

        # DEBUG: Verificar se base64 está presente
        data = webhook_data.get("data", {})
        message = data.get("message", {})
        message_type = data.get("messageType", "")

        if message_type == "audioMessage" and "audioMessage" in message:
            audio = message["audioMessage"]
            has_base64 = "base64" in audio or "media" in audio
            logger.info(f"🎵 AUDIO DETECTADO - Base64 presente: {has_base64}")
            if has_base64:
                base64_key = "base64" if "base64" in audio else "media"
                logger.info(f"✅ Base64 encontrado em audioMessage.{base64_key} (tamanho: {len(audio[base64_key])} chars)")
            else:
                logger.warning("⚠️ Base64 NAO encontrado no audioMessage!")
                logger.info(f"Keys disponiveis em audioMessage: {list(audio.keys())}")

        # Filtrar apenas eventos de mensagem
        event = webhook_data.get("event", "")
        if event != "messages.upsert":
            logger.info(f"⏭️  Evento ignorado: {event}")
            return {"status": "ignored", "reason": f"Event {event} not processed"}
        
        # Verificar se tem dados
        data = webhook_data.get("data", {})
        if not data:
            logger.warning("⚠️  Webhook sem dados")
            return {"status": "ignored", "reason": "No data in webhook"}
        
        # Verificar se não é mensagem do próprio bot
        key = data.get("key", {})
        from_me = key.get("fromMe", False)
        if from_me:
            logger.info("⏭️  Mensagem do próprio bot ignorada")
            return {"status": "ignored", "reason": "Message from bot itself"}
        
        # Preparar estado inicial
        initial_state: AgentState = {
            "raw_webhook_data": {"body": webhook_data},
            "next_action": ""
        }

        # Processar em background (não bloqueia a resposta)
        background_tasks.add_task(processar_mensagem, initial_state)

        logger.info("✅ Mensagem adicionada à fila de processamento - respondendo imediatamente")

        # IMPORTANTE: Retornar imediatamente para evitar timeout do ngrok/túnel
        return JSONResponse(
            status_code=200,
            content={
                "status": "received",
                "message": "Webhook received and queued for processing",
                "timestamp": datetime.now().isoformat()
            }
        )
        
    except json.JSONDecodeError:
        logger.error("❌ JSON inválido no webhook")
        raise HTTPException(status_code=400, detail="Invalid JSON")
        
    except Exception as e:
        logger.error(f"❌ Erro no webhook: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/test/message")
async def test_message(
    telefone: str,
    mensagem: str,
    background_tasks: BackgroundTasks
):
    """
    Endpoint de teste para simular mensagens.
    
    Útil para testar o bot sem precisar enviar mensagem real no WhatsApp.
    """
    try:
        # Criar webhook simulado
        webhook_simulado = {
            "event": "messages.upsert",
            "instance": settings.whatsapp_instance,
            "data": {
                "key": {
                    "remoteJid": f"{telefone}@s.whatsapp.net",
                    "fromMe": False,
                    "id": f"TEST_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                },
                "pushName": "Teste API",
                "messageType": "conversation",
                "messageTimestamp": int(datetime.now().timestamp()),
                "message": {
                    "conversation": mensagem
                }
            }
        }
        
        # Preparar estado inicial
        initial_state: AgentState = {
            "raw_webhook_data": {"body": webhook_simulado},
            "next_action": ""
        }

        # Processar em background
        background_tasks.add_task(processar_mensagem, initial_state)
        
        return {
            "status": "test_sent",
            "telefone": telefone,
            "mensagem": mensagem,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Erro no teste: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    """Endpoint para verificar status do bot."""
    return {
        "bot": {
            "number": settings.bot_phone_number,
            "instance": settings.whatsapp_instance,
            "environment": settings.environment
        },
        "apis": {
            "whatsapp": settings.whatsapp_api_url,
            "supabase": settings.supabase_url
        },
        "timestamp": datetime.now().isoformat()
    }


@app.post("/webhook/debug")
async def webhook_debug(request: Request):
    """
    Endpoint de DEBUG para capturar e salvar webhooks completos.

    Use este endpoint temporariamente para analisar a estrutura
    dos webhooks e verificar se o base64 está presente.
    """
    try:
        webhook_data = await request.json()

        # Salvar webhook em arquivo JSON
        filename = f"webhook_debug_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(webhook_data, f, indent=2, ensure_ascii=False)

        logger.info(f"[DEBUG] Webhook salvo em: {filename}")

        # Análise rápida
        data = webhook_data.get("data", {})
        message = data.get("message", {})
        message_type = data.get("messageType", "")

        analysis = {
            "saved_to": filename,
            "event": webhook_data.get("event", "unknown"),
            "message_type": message_type,
            "message_keys": list(message.keys()),
        }

        # Verificar base64 em áudio
        if message_type == "audioMessage" and "audioMessage" in message:
            audio = message["audioMessage"]
            analysis["audio_keys"] = list(audio.keys())
            analysis["has_base64"] = "base64" in audio or "media" in audio

            if analysis["has_base64"]:
                base64_key = "base64" if "base64" in audio else "media"
                analysis["base64_location"] = f"audioMessage.{base64_key}"
                analysis["base64_size"] = len(audio[base64_key])

        logger.info(f"[DEBUG] Analise: {analysis}")

        return {
            "status": "saved",
            "analysis": analysis,
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"[DEBUG] Erro: {e}", exc_info=True)
        return {"status": "error", "error": str(e)}


if __name__ == "__main__":
    import uvicorn
    
    logger.info("🚀 Iniciando WhatsApp Bot LangGraph...")
    logger.info(f"📱 Bot Number: {settings.bot_phone_number}")
    logger.info(f"🤖 Instance: {settings.whatsapp_instance}")
    logger.info(f"🌍 Environment: {settings.environment}")
    logger.info(f"🔧 Port: {settings.port}")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.is_development,
        log_level=settings.log_level.lower()
    )