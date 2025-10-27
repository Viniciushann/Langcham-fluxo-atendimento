"""Diagnostico completo do sistema."""
import asyncio
import sys
import json
from datetime import datetime

# Redirect para arquivo
log_file = open("diagnostic_log.txt", "w", encoding="utf-8")
sys.stdout = log_file
sys.stderr = log_file

async def main():
    print("="*60)
    print(f"DIAGNOSTICO - {datetime.now()}")
    print("="*60)

    try:
        print("\n1. Importando modulos...")
        from src.graph.workflow import criar_grafo_atendimento
        from src.config.settings import get_settings
        print("   OK - Modulos importados")

        print("\n2. Verificando configuracoes...")
        settings = get_settings()
        print(f"   OpenAI Key: {'OK' if settings.openai_api_key else 'ERRO'}")
        print(f"   Supabase URL: {settings.supabase_url}")
        print(f"   Instance: {settings.whatsapp_instance}")

        print("\n3. Criando grafo...")
        grafo = criar_grafo_atendimento()
        print("   OK - Grafo criado")

        print("\n4. Criando estado de teste...")
        webhook_test = {
            "event": "messages.upsert",
            "data": {
                "key": {
                    "remoteJid": "5562999999999@s.whatsapp.net",
                    "fromMe": False,
                    "id": "TEST123"
                },
                "message": {
                    "conversation": "Teste"
                },
                "messageType": "conversation",
                "pushName": "Teste"
            }
        }

        estado = {
            "raw_webhook_data": {"body": webhook_test},
            "next_action": ""
        }
        print("   OK - Estado criado")

        print("\n5. Executando grafo (pode demorar 30s)...")
        print("   Aguarde...")

        resultado = await asyncio.wait_for(
            grafo.ainvoke(estado),
            timeout=60
        )

        print("\n6. RESULTADO:")
        print(f"   Erro: {resultado.get('erro')}")
        print(f"   Cliente numero: {resultado.get('cliente_numero')}")
        print(f"   Cliente nome: {resultado.get('cliente_nome')}")
        print(f"   Texto processado: {bool(resultado.get('texto_processado'))}")
        print(f"   Resposta agente: {bool(resultado.get('resposta_agente'))}")
        print(f"   Fragmentos: {len(resultado.get('respostas_fragmentadas', []))}")
        print(f"   Next action: {resultado.get('next_action')}")

        if resultado.get('resposta_agente'):
            print(f"\n7. RESPOSTA DO AGENTE:")
            print(f"   {resultado['resposta_agente'][:500]}")

        if resultado.get('erro'):
            print(f"\n8. DETALHES DO ERRO:")
            print(f"   {resultado.get('erro_detalhes')}")

        print("\n" + "="*60)
        print("DIAGNOSTICO CONCLUIDO COM SUCESSO")
        print("="*60)

    except asyncio.TimeoutError:
        print("\nERRO: Timeout - processo demorou mais de 60s")
    except Exception as e:
        print(f"\nERRO FATAL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
    log_file.close()

    # Ler e mostrar no console
    with open("diagnostic_log.txt", "r", encoding="utf-8") as f:
        content = f.read()
        print(content, file=sys.__stdout__)
