"""
Script para testar o sistema RAG do Supabase.

Testa a busca vetorial usando a função match_documents.
"""

import asyncio
import logging
from openai import OpenAI
from src.clients.supabase_client import criar_supabase_client
from src.config.settings import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def testar_rag():
    """Testa o sistema RAG com diferentes queries."""

    # Inicializar clientes
    settings = get_settings()
    supabase = criar_supabase_client(settings.supabase_url, settings.supabase_key)
    openai_client = OpenAI(api_key=settings.openai_api_key)

    print("\n" + "="*60)
    print("TESTANDO SISTEMA RAG")
    print("="*60 + "\n")

    # Queries de teste
    queries = [
        "Quanto custa instalação de drywall?",
        "Quais serviços vocês oferecem?",
        "Qual o horário de atendimento?",
        "O que é drywall?"
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n[TESTE {i}/{len(queries)}] Query: '{query}'")
        print("-" * 60)

        try:
            # 1. Gerar embedding da query
            print("  [1/3] Gerando embedding da query...")
            response = openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=query
            )
            query_embedding = response.data[0].embedding
            print(f"       OK - Embedding gerado ({len(query_embedding)} dims)")

            # 2. Buscar documentos similares
            print("  [2/3] Buscando documentos similares...")
            resultado = supabase.client.rpc(
                "match_documents",
                {
                    "query_embedding": query_embedding,
                    "match_count": 3
                }
            ).execute()

            documentos = resultado.data
            print(f"       OK - {len(documentos)} documentos encontrados")

            # 3. Mostrar resultados
            print("  [3/3] Resultados:")
            if documentos:
                for j, doc in enumerate(documentos, 1):
                    similarity = doc.get('similarity', 0)
                    content = doc.get('content', '')
                    metadata = doc.get('metadata', {})

                    print(f"\n       Documento {j}:")
                    print(f"         Similaridade: {similarity:.4f} ({similarity*100:.1f}%)")
                    print(f"         Categoria: {metadata.get('categoria', 'N/A')}")
                    print(f"         Conteudo: {content[:100]}...")
            else:
                print("       Nenhum documento encontrado!")

        except Exception as e:
            print(f"       ERRO: {str(e)[:200]}")
            logger.error(f"Erro ao testar RAG: {e}", exc_info=True)

    print("\n" + "="*60)
    print("TESTES CONCLUÍDOS!")
    print("="*60 + "\n")


async def verificar_funcao():
    """Verifica se a função match_documents existe."""

    settings = get_settings()
    supabase = criar_supabase_client(settings.supabase_url, settings.supabase_key)

    print("\n[INFO] Verificando função match_documents...")

    try:
        # Tentar chamar a função com parâmetros vazios
        resultado = supabase.client.rpc(
            "match_documents",
            {
                "query_embedding": [0.0] * 1536,
                "match_count": 1
            }
        ).execute()

        print("[OK] Função match_documents existe e está acessível!\n")
        return True

    except Exception as e:
        error_msg = str(e)
        if "PGRST202" in error_msg or "Could not find" in error_msg:
            print("[ERRO] Função match_documents NÃO encontrada!")
            print("[AÇÃO] Execute o script setup_rag_supabase.sql no Supabase\n")
            return False
        else:
            print(f"[ERRO] {error_msg[:200]}\n")
            return False


if __name__ == "__main__":
    try:
        print("\n" + "="*60)
        print("INICIANDO TESTES DO SISTEMA RAG")
        print("="*60)

        # Verificar se a função existe
        funcao_existe = asyncio.run(verificar_funcao())

        if funcao_existe:
            # Executar testes
            asyncio.run(testar_rag())
        else:
            print("⚠️  Configure o Supabase primeiro:")
            print("   1. Acesse: https://znyypdwnqdlvqwwvffzk.supabase.co/project/_/sql/new")
            print("   2. Execute: setup_rag_supabase.sql")
            print("   3. Execute: python gerar_embeddings.py")
            print("   4. Execute: python testar_rag.py novamente\n")

    except KeyboardInterrupt:
        print("\n\nTestes interrompidos pelo usuário.")
    except Exception as e:
        print(f"\n\nERRO CRÍTICO: {e}")
        logger.error(f"Erro ao testar RAG: {e}", exc_info=True)
