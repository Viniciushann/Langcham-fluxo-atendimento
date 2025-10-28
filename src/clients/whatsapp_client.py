"""
Cliente WhatsApp para integração com Evolution API.

Este módulo fornece uma interface assíncrona para interagir com a Evolution API,
incluindo envio de mensagens, obtenção de mídia e gerenciamento de presença.
"""

from __future__ import annotations

import asyncio
import logging
from typing import Dict, Any, Optional
from urllib.parse import quote_plus

import httpx
from httpx import AsyncClient, HTTPError, TimeoutException

logger = logging.getLogger(__name__)


class WhatsAppClient:
    """
    Cliente para interação com Evolution API (WhatsApp Business).

    Fornece métodos para enviar mensagens, obter mídia e gerenciar status
    de digitação, com retry automático para resiliência.

    Attributes:
        base_url: URL base da Evolution API
        api_key: Chave de autenticação da API
        instance: Nome da instância do WhatsApp
        client: Cliente HTTP assíncrono
        max_retries: Número máximo de tentativas
        retry_delay: Delay inicial entre tentativas (segundos)
    """

    def __init__(
        self,
        base_url: str,
        api_key: str,
        instance: str,
        max_retries: int = 3,
        timeout: float = 30.0
    ) -> None:
        """
        Inicializa o cliente WhatsApp.

        Args:
            base_url: URL base da Evolution API (sem trailing slash)
            api_key: Chave de autenticação da Evolution API
            instance: Nome da instância do WhatsApp
            max_retries: Número máximo de tentativas em caso de falha (default: 3)
            timeout: Timeout em segundos para requisições (default: 30.0)

        Raises:
            ValueError: Se parâmetros obrigatórios estiverem vazios

        Example:
            >>> client = WhatsAppClient(
            ...     base_url="https://api.evolution.com",
            ...     api_key="sua-chave",
            ...     instance="minha-instancia"
            ... )
        """
        if not base_url or not api_key or not instance:
            raise ValueError("base_url, api_key e instance são obrigatórios")

        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.instance = instance
        self.max_retries = max_retries
        self.retry_delay = 1.0  # Delay inicial em segundos

        # Criar cliente HTTP assíncrono
        self.client = AsyncClient(
            timeout=httpx.Timeout(timeout),
            headers={
                "apikey": api_key,
                "Content-Type": "application/json"
            }
        )

        logger.info(f"WhatsAppClient inicializado: {base_url} - Instância: {instance}")

    async def _request_with_retry(
        self,
        method: str,
        url: str,
        **kwargs
    ) -> httpx.Response:
        """
        Executa requisição HTTP com retry exponential backoff.

        Args:
            method: Método HTTP (GET, POST, etc)
            url: URL completa da requisição
            **kwargs: Argumentos adicionais para a requisição

        Returns:
            httpx.Response: Resposta da requisição

        Raises:
            HTTPError: Se todas as tentativas falharem
        """
        last_exception = None

        for attempt in range(self.max_retries):
            try:
                response = await self.client.request(method, url, **kwargs)
                response.raise_for_status()
                return response

            except (HTTPError, TimeoutException) as e:
                last_exception = e
                attempt_num = attempt + 1

                # Tentar logar o corpo da resposta de erro
                try:
                    if hasattr(e, 'response') and e.response is not None:
                        error_body = e.response.text
                        logger.error(f"Resposta de erro da API: {error_body}")
                except:
                    pass

                if attempt_num < self.max_retries:
                    # Exponential backoff: 1s, 2s, 4s
                    delay = self.retry_delay * (2 ** attempt)
                    logger.warning(
                        f"Tentativa {attempt_num}/{self.max_retries} falhou: {e}. "
                        f"Tentando novamente em {delay}s..."
                    )
                    await asyncio.sleep(delay)
                else:
                    logger.error(
                        f"Todas as {self.max_retries} tentativas falharam: {e}",
                        exc_info=True
                    )

        # Se chegou aqui, todas as tentativas falharam
        raise last_exception

    async def obter_media_base64(self, message_id: str) -> Dict[str, Any]:
        """
        Obtém mídia (áudio, imagem, vídeo) em formato base64.

        Args:
            message_id: ID da mensagem contendo a mídia

        Returns:
            Dict contendo:
                - base64 (str): Dados da mídia em base64
                - mimetype (str): Tipo MIME da mídia

        Raises:
            ValueError: Se message_id estiver vazio
            HTTPError: Se houver erro na requisição

        Example:
            >>> media = await client.obter_media_base64("MSG123456")
            >>> print(f"Tipo: {media['mimetype']}")
            >>> print(f"Base64: {media['base64'][:50]}...")
        """
        if not message_id or not message_id.strip():
            raise ValueError("message_id não pode estar vazio")

        try:
            # URL encode do message_id também (pode conter caracteres especiais)
            url = f"{self.base_url}/message/media-base64/{quote_plus(self.instance)}/{quote_plus(message_id)}"

            logger.info(f"Obtendo mídia: {message_id}")
            logger.debug(f"URL de mídia: {url}")

            response = await self._request_with_retry("GET", url)
            data = response.json()

            logger.info(f"Mídia obtida: {message_id} - Tipo: {data.get('mimetype', 'unknown')}")

            return data

        except HTTPError as e:
            # Verificar se é 404 (mídia não encontrada ou expirada)
            if e.response and e.response.status_code == 404:
                logger.error(f"Mídia não encontrada (404) para message_id: {message_id}. A mídia pode ter expirado.")
                raise ValueError(f"Mídia não encontrada ou expirada para message_id: {message_id}")
            else:
                logger.error(f"Erro HTTP ao obter mídia {message_id}: {e}", exc_info=True)
                raise
        except Exception as e:
            logger.error(f"Erro ao obter mídia {message_id}: {e}", exc_info=True)
            raise

    async def enviar_mensagem(self, telefone: str, texto: str) -> Dict[str, Any]:
        """
        Envia mensagem de texto para um número.

        Args:
            telefone: Número do destinatário (formato: 5562999999999)
            texto: Texto da mensagem a enviar

        Returns:
            Dict com resposta da API contendo status e ID da mensagem

        Raises:
            ValueError: Se telefone ou texto estiverem vazios
            HTTPError: Se houver erro na requisição

        Example:
            >>> response = await client.enviar_mensagem(
            ...     telefone="5562999999999",
            ...     texto="Olá! Como posso ajudar?"
            ... )
            >>> print(f"Mensagem enviada: {response['id']}")
        """
        if not telefone or not telefone.strip():
            raise ValueError("telefone não pode estar vazio")

        if not texto or not texto.strip():
            raise ValueError("texto não pode estar vazio")

        try:
            url = f"{self.base_url}/message/sendText/{self.instance}"

            payload = {
                "number": telefone,
                "text": texto
            }

            logger.info(f"Enviando mensagem para: {telefone}")
            logger.debug(f"Texto: {texto[:100]}...")

            response = await self._request_with_retry("POST", url, json=payload)
            data = response.json()

            logger.info(f"Mensagem enviada com sucesso para: {telefone}")

            return data

        except Exception as e:
            logger.error(f"Erro ao enviar mensagem para {telefone}: {e}", exc_info=True)
            raise

    async def enviar_status_typing(self, telefone: str) -> None:
        """
        Envia status de "digitando" para um contato.

        Simula que o bot está digitando, melhorando a experiência do usuário.

        Args:
            telefone: Número do destinatário

        Raises:
            ValueError: Se telefone estiver vazio
            HTTPError: Se houver erro na requisição

        Example:
            >>> await client.enviar_status_typing("5562999999999")
            >>> # Aguardar um pouco
            >>> await asyncio.sleep(2)
            >>> # Enviar mensagem
            >>> await client.enviar_mensagem("5562999999999", "Olá!")
        """
        if not telefone or not telefone.strip():
            raise ValueError("telefone não pode estar vazio")

        try:
            url = f"{self.base_url}/chat/sendPresence/{self.instance}"

            payload = {
                "number": telefone,
                "options": {
                    "delay": 1200,
                    "presence": "composing"
                }
            }

            logger.debug(f"Enviando status 'digitando' para: {telefone}")

            await self._request_with_retry("POST", url, json=payload)

            logger.debug(f"Status 'digitando' enviado para: {telefone}")

        except Exception as e:
            # Não propagar erro de status typing para não quebrar o fluxo
            logger.warning(f"Erro ao enviar status typing (não crítico): {e}")

    async def enviar_status_available(self, telefone: str) -> None:
        """
        Remove status de "digitando" (marca como disponível).

        Args:
            telefone: Número do destinatário

        Example:
            >>> await client.enviar_status_available("5562999999999")
        """
        try:
            url = f"{self.base_url}/chat/sendPresence/{self.instance}"

            payload = {
                "number": telefone,
                "options": {
                    "delay": 1200,
                    "presence": "available"
                }
            }

            await self._request_with_retry("POST", url, json=payload)
            logger.debug(f"Status 'disponível' enviado para: {telefone}")

        except Exception as e:
            logger.warning(f"Erro ao enviar status available: {e}")

    async def enviar_audio(
        self,
        telefone: str,
        audio_base64: str,
        mimetype: str = "audio/ogg"
    ) -> Dict[str, Any]:
        """
        Envia áudio em formato base64.

        Args:
            telefone: Número do destinatário
            audio_base64: Áudio em base64
            mimetype: Tipo MIME do áudio (default: audio/ogg)

        Returns:
            Dict com resposta da API
        """
        try:
            url = f"{self.base_url}/message/sendMedia/{self.instance}"

            payload = {
                "number": telefone,
                "mediatype": "audio",
                "media": audio_base64,
                "mimetype": mimetype
            }

            logger.info(f"Enviando áudio para: {telefone}")

            response = await self._request_with_retry("POST", url, json=payload)
            data = response.json()

            logger.info(f"Áudio enviado para: {telefone}")
            return data

        except Exception as e:
            logger.error(f"Erro ao enviar áudio: {e}", exc_info=True)
            raise

    async def verificar_numero(self, telefone: str) -> Dict[str, Any]:
        """
        Verifica se um número está registrado no WhatsApp.

        Args:
            telefone: Número a verificar

        Returns:
            Dict com informações do número

        Example:
            >>> info = await client.verificar_numero("5562999999999")
            >>> if info.get("exists"):
            ...     print("Número existe no WhatsApp")
        """
        try:
            url = f"{self.base_url}/chat/checkNumber/{self.instance}"

            payload = {"number": telefone}

            response = await self._request_with_retry("POST", url, json=payload)
            data = response.json()

            logger.info(f"Número verificado: {telefone}")
            return data

        except Exception as e:
            logger.error(f"Erro ao verificar número: {e}")
            raise

    async def obter_perfil(self, telefone: str) -> Optional[Dict[str, Any]]:
        """
        Obtém informações do perfil de um contato.

        Args:
            telefone: Número do contato

        Returns:
            Dict com dados do perfil ou None se não encontrado
        """
        try:
            url = f"{self.base_url}/chat/fetchProfile/{self.instance}"

            payload = {"number": telefone}

            response = await self._request_with_retry("POST", url, json=payload)
            data = response.json()

            logger.info(f"Perfil obtido: {telefone}")
            return data

        except Exception as e:
            logger.warning(f"Erro ao obter perfil (não crítico): {e}")
            return None

    async def marcar_como_lido(self, message_id: str, telefone: str) -> None:
        """
        Marca mensagem como lida.

        Args:
            message_id: ID da mensagem
            telefone: Número do remetente
        """
        try:
            url = f"{self.base_url}/chat/markMessageAsRead/{self.instance}"

            payload = {
                "id": message_id,
                "number": telefone
            }

            await self._request_with_retry("POST", url, json=payload)
            logger.debug(f"Mensagem marcada como lida: {message_id}")

        except Exception as e:
            logger.warning(f"Erro ao marcar como lido (não crítico): {e}")

    async def close(self) -> None:
        """
        Fecha a conexão HTTP.

        Example:
            >>> await client.close()
        """
        try:
            await self.client.aclose()
            logger.info("Cliente WhatsApp fechado")
        except Exception as e:
            logger.error(f"Erro ao fechar cliente WhatsApp: {e}")


# ========== FACTORY FUNCTION ==========

def criar_whatsapp_client(
    base_url: str,
    api_key: str,
    instance: str,
    max_retries: int = 3
) -> WhatsAppClient:
    """
    Factory function para criar WhatsAppClient.

    Args:
        base_url: URL base da Evolution API
        api_key: Chave de autenticação
        instance: Nome da instância
        max_retries: Número máximo de tentativas (default: 3)

    Returns:
        WhatsAppClient: Cliente inicializado

    Example:
        >>> from src.config import get_settings
        >>> settings = get_settings()
        >>> client = criar_whatsapp_client(
        ...     base_url=settings.whatsapp_api_url,
        ...     api_key=settings.whatsapp_api_key,
        ...     instance=settings.whatsapp_instance
        ... )
    """
    return WhatsAppClient(
        base_url=base_url,
        api_key=api_key,
        instance=instance,
        max_retries=max_retries
    )


# ========== EXPORTAÇÕES ==========

__all__ = [
    "WhatsAppClient",
    "criar_whatsapp_client",
]
