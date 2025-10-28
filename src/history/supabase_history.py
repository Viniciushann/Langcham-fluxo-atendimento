"""
Histórico de mensagens usando Supabase REST API.

Este módulo implementa um histórico de chat compatível com LangChain
usando a API REST do Supabase em vez de conexão PostgreSQL direta.
"""

from typing import List
import json
from datetime import datetime

from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from supabase import create_client, Client

import logging

logger = logging.getLogger(__name__)


class SupabaseChatMessageHistory:
    """
    Histórico de mensagens usando Supabase REST API.

    Compatível com a interface do LangChain ChatMessageHistory.
    """

    def __init__(
        self,
        supabase_url: str,
        supabase_key: str,
        session_id: str,
        table_name: str = "message_history"
    ):
        """
        Inicializa o histórico de mensagens.

        Args:
            supabase_url: URL do projeto Supabase
            supabase_key: Chave de API do Supabase
            session_id: ID da sessão (número do telefone)
            table_name: Nome da tabela (padrão: message_history)
        """
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.session_id = session_id
        self.table_name = table_name

        logger.info(f"SupabaseChatMessageHistory inicializado para sessão: {session_id}")

    @property
    def messages(self) -> List[BaseMessage]:
        """
        Retorna todas as mensagens do histórico.

        Returns:
            Lista de mensagens (HumanMessage e AIMessage)
        """
        try:
            # Buscar mensagens ordenadas por data
            response = self.supabase.table(self.table_name)\
                .select("*")\
                .eq("session_id", self.session_id)\
                .order("created_at", desc=False)\
                .execute()

            messages = []
            for row in response.data:
                message_data = row["message"]

                # Converter de JSON para BaseMessage
                if message_data.get("type") == "human":
                    messages.append(HumanMessage(content=message_data.get("data", {}).get("content", "")))
                elif message_data.get("type") == "ai":
                    messages.append(AIMessage(content=message_data.get("data", {}).get("content", "")))

            logger.debug(f"Carregadas {len(messages)} mensagens do histórico")
            return messages

        except Exception as e:
            logger.error(f"Erro ao carregar mensagens: {e}")
            return []

    def add_user_message(self, message: str) -> None:
        """
        Adiciona mensagem do usuário ao histórico.

        Args:
            message: Texto da mensagem do usuário
        """
        try:
            message_json = {
                "type": "human",
                "data": {
                    "content": message,
                    "additional_kwargs": {},
                    "type": "human"
                }
            }

            self.supabase.table(self.table_name).insert({
                "session_id": self.session_id,
                "message": message_json,
                "created_at": datetime.now().isoformat()
            }).execute()

            logger.debug(f"Mensagem do usuário adicionada: {message[:50]}...")

        except Exception as e:
            logger.error(f"Erro ao adicionar mensagem do usuário: {e}")
            raise

    def add_ai_message(self, message: str) -> None:
        """
        Adiciona mensagem da IA ao histórico.

        Args:
            message: Texto da resposta da IA
        """
        try:
            message_json = {
                "type": "ai",
                "data": {
                    "content": message,
                    "additional_kwargs": {},
                    "type": "ai"
                }
            }

            self.supabase.table(self.table_name).insert({
                "session_id": self.session_id,
                "message": message_json,
                "created_at": datetime.now().isoformat()
            }).execute()

            logger.debug(f"Mensagem da IA adicionada: {message[:50]}...")

        except Exception as e:
            logger.error(f"Erro ao adicionar mensagem da IA: {e}")
            raise

    def clear(self) -> None:
        """
        Limpa todo o histórico da sessão.
        """
        try:
            self.supabase.table(self.table_name)\
                .delete()\
                .eq("session_id", self.session_id)\
                .execute()

            logger.info(f"Histórico limpo para sessão: {self.session_id}")

        except Exception as e:
            logger.error(f"Erro ao limpar histórico: {e}")
            raise
