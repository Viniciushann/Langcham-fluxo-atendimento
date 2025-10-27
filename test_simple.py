"""Teste simples do fluxo."""
import asyncio
import os
os.environ['PYTHONIOENCODING'] = 'utf-8'

from src.graph.workflow import criar_grafo_atendimento

async def test():
    webhook_data = {
        "event": "messages.upsert",
        "data": {
            "key": {
                "remoteJid": "556299999999@s.whatsapp.net",
                "fromMe": False,
                "id": "TEST123"
            },
            "message": {
                "conversation": "Ola! Quanto custa drywall?"
            },
            "messageType": "conversation",
            "pushName": "Cliente Teste"
        }
    }

    print("Criando grafo...")
    grafo = criar_grafo_atendimento()

    print("Criando estado...")
    estado = {"raw_webhook_data": {"body": webhook_data}, "next_action": ""}

    print("Executando grafo...")
    resultado = await grafo.ainvoke(estado)

    print("\nRESULTADO:")
    print(f"  Erro: {resultado.get('erro')}")
    print(f"  Resposta agente: {bool(resultado.get('resposta_agente'))}")
    print(f"  Fragmentos: {len(resultado.get('fragmentos_resposta', []))}")
    print(f"  Acao final: {resultado.get('next_action')}")

    if resultado.get('resposta_agente'):
        print(f"\nResposta: {resultado['resposta_agente'][:200]}")

asyncio.run(test())
