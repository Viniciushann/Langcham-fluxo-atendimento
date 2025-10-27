"""
Script para gerar embeddings dos documentos no Supabase.

Este script:
1. Busca documentos sem embedding
2. Gera embeddings usando OpenAI
3. Atualiza os documentos no Supabase

Execute após rodar o setup_rag_supabase.sql
"""

import asyncio
import logging
from openai import OpenAI
from src.clients.supabase_client import criar_supabase_client
from src.config.settings import get_settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def gerar_embeddings():
    """Gera embeddings para todos os documentos sem embedding."""

    # Inicializar clientes
    settings = get_settings()
    supabase = criar_supabase_client(settings.supabase_url, settings.supabase_key)
    openai_client = OpenAI(api_key=settings.openai_api_key)

    print("\n" + "="*60)
    print("GERANDO EMBEDDINGS DOS DOCUMENTOS")
    print("="*60 + "\n")

    # 1. Buscar documentos sem embedding
    print("[1/4] Buscando documentos sem embedding...")
    try:
        response = (
            supabase.client
            .table("documents")
            .select("*")
            .is_("embedding", "null")
            .execute()
        )

        documentos = response.data
        total = len(documentos)

        if total == 0:
            print("    Nenhum documento sem embedding encontrado.")
            print("    Todos os documentos ja foram processados!\n")
            return

        print(f"    Encontrados {total} documentos para processar\n")

    except Exception as e:
        print(f"    ERRO ao buscar documentos: {e}")
        return

    # 2. Gerar embeddings
    print(f"[2/4] Gerando embeddings com OpenAI (modelo: text-embedding-ada-002)...")
    embeddings_gerados = 0

    for i, doc in enumerate(documentos, 1):
        try:
            doc_id = doc['id']
            content = doc['content']

            print(f"    [{i}/{total}] Processando documento: {content[:50]}...")

            # Gerar embedding via OpenAI
            response = openai_client.embeddings.create(
                model="text-embedding-ada-002",
                input=content
            )

            embedding = response.data[0].embedding

            # Atualizar documento no Supabase
            supabase.client.table("documents").update({
                "embedding": embedding
            }).eq("id", doc_id).execute()

            embeddings_gerados += 1
            print(f"         OK - Embedding gerado e salvo ({len(embedding)} dimensões)")

        except Exception as e:
            print(f"         ERRO: {str(e)[:100]}")
            continue

    print(f"\n[3/4] Embeddings gerados: {embeddings_gerados}/{total}\n")

    # 3. Verificar resultados
    print("[4/4] Verificando resultados...")
    try:
        response = (
            supabase.client
            .table("documents")
            .select("id, content, embedding")
            .not_.is_("embedding", "null")
            .execute()
        )

        docs_com_embedding = len(response.data)
        print(f"    Total de documentos com embedding: {docs_com_embedding}")

        if docs_com_embedding > 0:
            print("\n    Exemplos:")
            for i, doc in enumerate(response.data[:3], 1):
                preview = doc['content'][:60]
                emb_size = len(doc['embedding']) if doc['embedding'] else 0
                print(f"      {i}. {preview}... [{emb_size} dims]")

    except Exception as e:
        print(f"    ERRO na verificação: {e}")

    print("\n" + "="*60)
    print("CONCLUÍDO!")
    print("="*60 + "\n")

    print("Próximos passos:")
    print("  1. Execute: python testar_rag.py")
    print("  2. Teste a busca vetorial")
    print("  3. Integre com o bot\n")


if __name__ == "__main__":
    try:
        asyncio.run(gerar_embeddings())
    except KeyboardInterrupt:
        print("\n\nProcesso interrompido pelo usuário.")
    except Exception as e:
        print(f"\n\nERRO CRÍTICO: {e}")
        logger.error(f"Erro ao gerar embeddings: {e}", exc_info=True)
