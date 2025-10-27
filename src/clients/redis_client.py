"""
Cliente Redis para gerenciamento de fila de mensagens.

Este módulo fornece uma interface assíncrona para gerenciar filas de mensagens
usando Redis, garantindo processamento sequencial por cliente.
"""

from __future__ import annotations

import json
import logging
from typing import Dict, Any, List, Optional

import redis.asyncio as aioredis
from redis.asyncio import Redis
from redis.exceptions import RedisError, ConnectionError as RedisConnectionError

logger = logging.getLogger(__name__)


class RedisQueue:
    """
    Gerenciador de fila de mensagens usando Redis.

    Utiliza listas do Redis para implementar filas FIFO (First In, First Out)
    garantindo processamento sequencial de mensagens por cliente.

    Attributes:
        redis_client: Cliente Redis assíncrono
    """

    def __init__(self, redis_client: Redis) -> None:
        """
        Inicializa o gerenciador de fila Redis.

        Args:
            redis_client: Cliente Redis assíncrono já configurado

        Example:
            >>> import redis.asyncio as aioredis
            >>> redis_client = await aioredis.from_url("redis://localhost:6379")
            >>> queue = RedisQueue(redis_client)
        """
        if not redis_client:
            raise ValueError("redis_client é obrigatório")

        self.redis_client = redis_client
        logger.info("RedisQueue inicializado")

    async def adicionar_mensagem(
        self,
        telefone: str,
        mensagem: Dict[str, Any]
    ) -> None:
        """
        Adiciona uma mensagem à fila de um cliente.

        A mensagem é serializada em JSON e adicionada ao final da fila
        usando o comando RPUSH do Redis.

        Args:
            telefone: Número do telefone do cliente (chave da fila)
            mensagem: Dicionário com dados da mensagem

        Raises:
            ValueError: Se telefone estiver vazio
            RedisError: Se houver erro ao acessar Redis

        Example:
            >>> await queue.adicionar_mensagem(
            ...     telefone="5562999999999",
            ...     mensagem={
            ...         "conteudo": "Olá",
            ...         "timestamp": "2025-10-21T10:00:00",
            ...         "tipo": "conversation"
            ...     }
            ... )
        """
        if not telefone or not telefone.strip():
            raise ValueError("Telefone não pode estar vazio")

        try:
            key = f"fila:{telefone}"
            mensagem_json = json.dumps(mensagem, ensure_ascii=False)

            # Adicionar ao final da fila (RPUSH)
            await self.redis_client.rpush(key, mensagem_json)

            logger.info(f"Mensagem adicionada à fila: {telefone}")
            logger.debug(f"Conteúdo: {mensagem_json[:100]}...")

        except json.JSONEncodeError as e:
            logger.error(f"Erro ao serializar mensagem: {e}")
            raise ValueError(f"Mensagem inválida para serialização JSON: {e}")

        except RedisError as e:
            logger.error(f"Erro ao adicionar mensagem ao Redis: {e}", exc_info=True)
            raise

    async def buscar_mensagens(self, telefone: str) -> List[Dict[str, Any]]:
        """
        Busca todas as mensagens da fila de um cliente.

        Retorna todas as mensagens sem removê-las da fila.

        Args:
            telefone: Número do telefone do cliente

        Returns:
            Lista de mensagens (dicionários) na ordem de chegada

        Raises:
            RedisError: Se houver erro ao acessar Redis

        Example:
            >>> mensagens = await queue.buscar_mensagens("5562999999999")
            >>> for msg in mensagens:
            ...     print(msg["conteudo"])
        """
        if not telefone or not telefone.strip():
            raise ValueError("Telefone não pode estar vazio")

        try:
            key = f"fila:{telefone}"

            # Buscar todas as mensagens (índice 0 até -1)
            mensagens_json = await self.redis_client.lrange(key, 0, -1)

            if not mensagens_json:
                logger.info(f"Nenhuma mensagem na fila: {telefone}")
                return []

            # Deserializar mensagens
            mensagens = []
            for msg_json in mensagens_json:
                try:
                    # msg_json pode ser bytes, converter para string
                    if isinstance(msg_json, bytes):
                        msg_json = msg_json.decode('utf-8')

                    mensagem = json.loads(msg_json)
                    mensagens.append(mensagem)

                except json.JSONDecodeError as e:
                    logger.error(f"Erro ao deserializar mensagem: {e}")
                    logger.debug(f"Mensagem inválida: {msg_json}")
                    # Continuar com as outras mensagens
                    continue

            logger.info(f"Encontradas {len(mensagens)} mensagens na fila: {telefone}")
            return mensagens

        except RedisError as e:
            logger.error(f"Erro ao buscar mensagens do Redis: {e}", exc_info=True)
            raise

    async def limpar_fila(self, telefone: str) -> None:
        """
        Remove todas as mensagens da fila de um cliente.

        Deleta a chave completamente do Redis.

        Args:
            telefone: Número do telefone do cliente

        Raises:
            RedisError: Se houver erro ao acessar Redis

        Example:
            >>> await queue.limpar_fila("5562999999999")
        """
        if not telefone or not telefone.strip():
            raise ValueError("Telefone não pode estar vazio")

        try:
            key = f"fila:{telefone}"

            # Deletar a chave
            deleted = await self.redis_client.delete(key)

            if deleted:
                logger.info(f"Fila limpa: {telefone}")
            else:
                logger.info(f"Fila já estava vazia: {telefone}")

        except RedisError as e:
            logger.error(f"Erro ao limpar fila do Redis: {e}", exc_info=True)
            raise

    async def contar_mensagens(self, telefone: str) -> int:
        """
        Conta o número de mensagens na fila de um cliente.

        Args:
            telefone: Número do telefone do cliente

        Returns:
            Número de mensagens na fila (0 se vazia)

        Raises:
            RedisError: Se houver erro ao acessar Redis

        Example:
            >>> count = await queue.contar_mensagens("5562999999999")
            >>> print(f"Mensagens na fila: {count}")
        """
        if not telefone or not telefone.strip():
            raise ValueError("Telefone não pode estar vazio")

        try:
            key = f"fila:{telefone}"

            # Contar elementos na lista
            count = await self.redis_client.llen(key)

            logger.debug(f"Fila {telefone}: {count} mensagens")
            return count

        except RedisError as e:
            logger.error(f"Erro ao contar mensagens no Redis: {e}", exc_info=True)
            raise

    async def obter_primeira_mensagem(self, telefone: str) -> Optional[Dict[str, Any]]:
        """
        Obtém a primeira mensagem da fila sem removê-la.

        Args:
            telefone: Número do telefone do cliente

        Returns:
            Primeira mensagem da fila ou None se vazia

        Example:
            >>> primeira = await queue.obter_primeira_mensagem("5562999999999")
            >>> if primeira:
            ...     print(primeira["conteudo"])
        """
        try:
            key = f"fila:{telefone}"

            # Buscar primeiro elemento (índice 0)
            msg_json = await self.redis_client.lindex(key, 0)

            if not msg_json:
                return None

            # Deserializar
            if isinstance(msg_json, bytes):
                msg_json = msg_json.decode('utf-8')

            return json.loads(msg_json)

        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Erro ao obter primeira mensagem: {e}")
            return None

    async def remover_primeira_mensagem(self, telefone: str) -> Optional[Dict[str, Any]]:
        """
        Remove e retorna a primeira mensagem da fila (LPOP).

        Args:
            telefone: Número do telefone do cliente

        Returns:
            Primeira mensagem removida ou None se fila vazia

        Example:
            >>> mensagem = await queue.remover_primeira_mensagem("5562999999999")
        """
        try:
            key = f"fila:{telefone}"

            # Remover primeiro elemento
            msg_json = await self.redis_client.lpop(key)

            if not msg_json:
                return None

            # Deserializar
            if isinstance(msg_json, bytes):
                msg_json = msg_json.decode('utf-8')

            mensagem = json.loads(msg_json)
            logger.info(f"Mensagem removida da fila: {telefone}")

            return mensagem

        except (RedisError, json.JSONDecodeError) as e:
            logger.error(f"Erro ao remover primeira mensagem: {e}", exc_info=True)
            return None

    async def fila_existe(self, telefone: str) -> bool:
        """
        Verifica se existe uma fila para o cliente.

        Args:
            telefone: Número do telefone do cliente

        Returns:
            True se a fila existe, False caso contrário
        """
        try:
            key = f"fila:{telefone}"
            existe = await self.redis_client.exists(key)
            return bool(existe)

        except RedisError as e:
            logger.error(f"Erro ao verificar existência da fila: {e}")
            return False

    async def definir_ttl(self, telefone: str, segundos: int) -> None:
        """
        Define tempo de expiração para a fila.

        Útil para limpar filas antigas automaticamente.

        Args:
            telefone: Número do telefone do cliente
            segundos: Tempo em segundos até expiração

        Example:
            >>> # Fila expira em 1 hora
            >>> await queue.definir_ttl("5562999999999", 3600)
        """
        try:
            key = f"fila:{telefone}"
            await self.redis_client.expire(key, segundos)
            logger.debug(f"TTL definido para fila {telefone}: {segundos}s")

        except RedisError as e:
            logger.error(f"Erro ao definir TTL: {e}")

    async def close(self) -> None:
        """
        Fecha a conexão com Redis.

        Example:
            >>> await queue.close()
        """
        try:
            await self.redis_client.close()
            logger.info("Conexão Redis fechada")
        except Exception as e:
            logger.error(f"Erro ao fechar conexão Redis: {e}")


# ========== FACTORY FUNCTIONS ==========

async def criar_redis_queue(
    host: str = "localhost",
    port: int = 6379,
    password: Optional[str] = None,
    db: int = 0
) -> RedisQueue:
    """
    Factory function para criar RedisQueue.

    Args:
        host: Host do Redis
        port: Porta do Redis
        password: Senha do Redis (opcional)
        db: Índice do database Redis

    Returns:
        RedisQueue: Gerenciador de fila inicializado

    Example:
        >>> from src.config import get_settings
        >>> settings = get_settings()
        >>> queue = await criar_redis_queue(
        ...     host=settings.redis_host,
        ...     port=settings.redis_port,
        ...     password=settings.redis_password,
        ...     db=settings.redis_db
        ... )
    """
    try:
        # Criar cliente Redis assíncrono
        redis_client = await aioredis.from_url(
            f"redis://{host}:{port}/{db}",
            password=password,
            encoding="utf-8",
            decode_responses=False  # Vamos decodificar manualmente
        )

        # Testar conexão
        await redis_client.ping()
        logger.info(f"Conectado ao Redis: {host}:{port}/{db}")

        return RedisQueue(redis_client)

    except RedisConnectionError as e:
        logger.error(f"Erro ao conectar ao Redis: {e}")
        raise
    except Exception as e:
        logger.error(f"Erro ao criar RedisQueue: {e}")
        raise


async def criar_redis_queue_from_url(url: str) -> RedisQueue:
    """
    Factory function para criar RedisQueue a partir de URL.

    Args:
        url: URL do Redis (ex: redis://localhost:6379/0)

    Returns:
        RedisQueue: Gerenciador de fila inicializado

    Example:
        >>> queue = await criar_redis_queue_from_url("redis://localhost:6379/0")
    """
    try:
        redis_client = await aioredis.from_url(
            url,
            encoding="utf-8",
            decode_responses=False
        )

        await redis_client.ping()
        logger.info(f"Conectado ao Redis: {url}")

        return RedisQueue(redis_client)

    except Exception as e:
        logger.error(f"Erro ao criar RedisQueue from URL: {e}")
        raise


# ========== EXPORTAÇÕES ==========

__all__ = [
    "RedisQueue",
    "criar_redis_queue",
    "criar_redis_queue_from_url",
]
