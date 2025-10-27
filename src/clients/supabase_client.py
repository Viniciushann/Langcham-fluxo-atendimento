"""
Cliente Supabase para gerenciamento de clientes e RAG.

Este módulo fornece uma interface assíncrona para interagir com o Supabase,
incluindo operações de CRUD de clientes e busca vetorial para RAG.
"""

from __future__ import annotations

import logging
from typing import Optional, Dict, Any, List

from supabase import create_client, Client
from supabase.lib.client_options import ClientOptions

logger = logging.getLogger(__name__)


class SupabaseClient:
    """
    Cliente para interação com Supabase.

    Gerencia operações de banco de dados e vector store para RAG.

    Attributes:
        client: Cliente Supabase inicializado
        url: URL do projeto Supabase
        key: Chave de API do Supabase
    """

    def __init__(self, url: str, key: str) -> None:
        """
        Inicializa o cliente Supabase.

        Args:
            url: URL do projeto Supabase (ex: https://xxx.supabase.co)
            key: Chave de API do Supabase (anon/service key)

        Raises:
            ValueError: Se URL ou key estiverem vazios
            Exception: Se houver erro ao conectar ao Supabase

        Example:
            >>> client = SupabaseClient(
            ...     url="https://xxx.supabase.co",
            ...     key="eyJhbGc..."
            ... )
        """
        if not url or not key:
            raise ValueError("URL e key do Supabase são obrigatórios")

        self.url = url
        self.key = key

        try:
            self.client: Client = create_client(url, key)
            logger.info(f"Cliente Supabase inicializado: {url}")
        except Exception as e:
            logger.error(f"Erro ao inicializar cliente Supabase: {e}")
            raise

    async def buscar_cliente(self, telefone: str) -> Optional[Dict[str, Any]]:
        """
        Busca um cliente pelo número de telefone.

        Args:
            telefone: Número do telefone do cliente (formato: 5562999999999)

        Returns:
            Dict com dados do cliente se encontrado, None caso contrário

        Raises:
            Exception: Se houver erro na consulta ao banco

        Example:
            >>> cliente = await client.buscar_cliente("5562999999999")
            >>> if cliente:
            ...     print(f"Cliente encontrado: {cliente['nome_lead']}")
        """
        try:
            logger.info(f"Buscando cliente com telefone: {telefone}")

            response = (
                self.client
                .table("leads")
                .select("*")
                .eq("phone_numero", telefone)
                .execute()
            )

            if response.data and len(response.data) > 0:
                cliente = response.data[0]
                logger.info(f"Cliente encontrado: {cliente.get('id')}")
                return cliente
            else:
                logger.info(f"Cliente não encontrado: {telefone}")
                return None

        except Exception as e:
            logger.error(f"Erro ao buscar cliente {telefone}: {e}", exc_info=True)
            raise

    async def cadastrar_cliente(self, dados: Dict[str, Any]) -> Dict[str, Any]:
        """
        Cadastra um novo cliente no banco de dados.

        Args:
            dados: Dicionário com dados do cliente
                - nome_lead (str): Nome do cliente
                - phone_numero (str): Número de telefone
                - message (str): Primeira mensagem recebida
                - tipo_mensagem (str): Tipo da mensagem (ex: "conversation")

        Returns:
            Dict com dados do cliente cadastrado, incluindo ID

        Raises:
            ValueError: Se campos obrigatórios estiverem faltando
            Exception: Se houver erro ao inserir no banco

        Example:
            >>> cliente = await client.cadastrar_cliente({
            ...     "nome_lead": "João Silva",
            ...     "phone_numero": "5562999999999",
            ...     "message": "Olá, preciso de ajuda",
            ...     "tipo_mensagem": "conversation"
            ... })
            >>> print(f"Cliente cadastrado com ID: {cliente['id']}")
        """
        # Validar campos obrigatórios
        campos_obrigatorios = ["nome_lead", "phone_numero", "message", "tipo_mensagem"]
        for campo in campos_obrigatorios:
            if campo not in dados:
                raise ValueError(f"Campo obrigatório ausente: {campo}")

        try:
            logger.info(f"Cadastrando cliente: {dados.get('nome_lead')} - {dados.get('phone_numero')}")

            # Mapear campos para a estrutura da tabela leads
            dados_leads = {
                "nome_Leed": dados.get("nome_lead"),
                "phone_numero": dados.get("phone_numero"),
                "message": dados.get("message"),
                "wpp.TipoDeMensagem": dados.get("tipo_mensagem")
            }

            response = (
                self.client
                .table("leads")
                .insert(dados_leads)
                .execute()
            )

            if response.data and len(response.data) > 0:
                cliente_criado = response.data[0]
                logger.info(f"Cliente cadastrado com sucesso: ID {cliente_criado.get('id')}")
                return cliente_criado
            else:
                raise Exception("Falha ao cadastrar cliente: resposta vazia")

        except Exception as e:
            logger.error(f"Erro ao cadastrar cliente: {e}", exc_info=True)
            raise

    async def buscar_documentos_rag(
        self,
        query: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Busca documentos similares usando vector store para RAG.

        Utiliza a função match_documents do Supabase que faz busca por
        similaridade usando embeddings vetoriais.

        Args:
            query: Texto da consulta para buscar documentos similares
            limit: Número máximo de documentos a retornar (default: 5)

        Returns:
            Lista de documentos similares com metadados e scores

        Raises:
            ValueError: Se query estiver vazia
            Exception: Se houver erro na busca vetorial

        Example:
            >>> docs = await client.buscar_documentos_rag(
            ...     query="preços de instalação de drywall",
            ...     limit=3
            ... )
            >>> for doc in docs:
            ...     print(f"Documento: {doc['content']}")
            ...     print(f"Similaridade: {doc['similarity']}")
        """
        if not query or not query.strip():
            raise ValueError("Query não pode estar vazia")

        try:
            logger.info(f"Buscando documentos RAG para: '{query[:50]}...' (limit={limit})")

            # Chamar função RPC do Supabase para busca vetorial
            response = self.client.rpc(
                "match_documents",
                {
                    "query_embedding": query,
                    "match_count": limit
                }
            ).execute()

            documentos = response.data if response.data else []

            logger.info(f"Encontrados {len(documentos)} documentos similares")

            return documentos

        except Exception as e:
            logger.error(f"Erro ao buscar documentos RAG: {e}", exc_info=True)
            # Retornar lista vazia ao invés de propagar erro
            # para não quebrar o fluxo do agente
            logger.warning("Retornando lista vazia de documentos")
            return []

    async def atualizar_cliente(
        self,
        cliente_id: str,
        dados: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Atualiza dados de um cliente existente.

        Args:
            cliente_id: ID do cliente no Supabase
            dados: Dicionário com campos a serem atualizados

        Returns:
            Dict com dados atualizados do cliente

        Raises:
            Exception: Se houver erro na atualização

        Example:
            >>> cliente = await client.atualizar_cliente(
            ...     cliente_id="123",
            ...     dados={"message": "Nova mensagem"}
            ... )
        """
        try:
            logger.info(f"Atualizando cliente ID: {cliente_id}")

            response = (
                self.client
                .table("leads")
                .update(dados)
                .eq("id", cliente_id)
                .execute()
            )

            if response.data and len(response.data) > 0:
                cliente_atualizado = response.data[0]
                logger.info(f"Cliente atualizado: ID {cliente_id}")
                return cliente_atualizado
            else:
                raise Exception(f"Cliente não encontrado: ID {cliente_id}")

        except Exception as e:
            logger.error(f"Erro ao atualizar cliente {cliente_id}: {e}", exc_info=True)
            raise

    async def listar_clientes(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Lista clientes cadastrados.

        Args:
            limit: Número máximo de clientes a retornar
            offset: Número de registros a pular (para paginação)

        Returns:
            Lista de clientes

        Example:
            >>> clientes = await client.listar_clientes(limit=10)
        """
        try:
            logger.info(f"Listando clientes (limit={limit}, offset={offset})")

            response = (
                self.client
                .table("leads")
                .select("*")
                .range(offset, offset + limit - 1)
                .execute()
            )

            clientes = response.data if response.data else []
            logger.info(f"Encontrados {len(clientes)} clientes")

            return clientes

        except Exception as e:
            logger.error(f"Erro ao listar clientes: {e}", exc_info=True)
            raise

    def close(self) -> None:
        """
        Fecha conexão com Supabase.

        Nota: O cliente Supabase Python gerencia conexões automaticamente,
        mas este método está disponível para consistência de API.
        """
        logger.info("Fechando cliente Supabase")
        # Cliente Supabase não requer fechamento explícito
        pass


# ========== FACTORY FUNCTION ==========

def criar_supabase_client(url: str, key: str) -> SupabaseClient:
    """
    Factory function para criar SupabaseClient.

    Args:
        url: URL do projeto Supabase
        key: Chave de API do Supabase

    Returns:
        SupabaseClient: Cliente inicializado

    Example:
        >>> from src.config import get_settings
        >>> settings = get_settings()
        >>> client = criar_supabase_client(
        ...     settings.supabase_url,
        ...     settings.supabase_key
        ... )
    """
    return SupabaseClient(url, key)


# ========== SINGLETON ==========

_supabase_client: Optional[Client] = None


def get_supabase_client() -> Client:
    """
    Retorna instância singleton do cliente Supabase.

    Carrega configurações automaticamente e reutiliza a mesma instância.

    Returns:
        Client: Cliente Supabase nativo (para compatibilidade com LangChain)

    Raises:
        ValueError: Se configurações estiverem inválidas

    Example:
        >>> client = get_supabase_client()
        >>> response = client.table("leads").select("*").execute()
    """
    global _supabase_client

    if _supabase_client is None:
        from config.settings import get_settings

        settings = get_settings()

        if not settings.supabase_url or not settings.supabase_key:
            raise ValueError("SUPABASE_URL e SUPABASE_KEY devem estar configurados")

        _supabase_client = create_client(
            settings.supabase_url,
            settings.supabase_key
        )

        logger.info(f"Cliente Supabase singleton inicializado: {settings.supabase_url}")

    return _supabase_client


# ========== EXPORTAÇÕES ==========

__all__ = [
    "SupabaseClient",
    "criar_supabase_client",
    "get_supabase_client",
]
