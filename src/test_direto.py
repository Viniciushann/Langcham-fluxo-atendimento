"""
Script para testar o bot diretamente sem API.

Este script permite testar o fluxo completo do bot executando
o grafo LangGraph sem precisar subir o servidor FastAPI.

Uso:
    python test_direto.py
"""

import asyncio
import sys
from pathlib import Path

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent))

from src.graph.workflow import criar_grafo_atendimento
from src.models.state import AgentState


async def testar_bot():
    """
    Testa o bot diretamente executando o grafo.
    """
    print()
    print("=" * 70)
    print("TESTE DIRETO DO BOT - SEM API")
    print("=" * 70)
    print()

    # Criar grafo
    print("[1] Criando grafo de atendimento...")
    app = criar_grafo_atendimento()
    print("[OK] Grafo criado!")
    print()

    # Webhook simulado
    print("[2] Preparando webhook simulado...")
    webhook_data = {
        "event": "messages.upsert",
        "instance": "test-instance",
        "data": {
            "key": {
                "remoteJid": "556281091167@s.whatsapp.net",
                "id": "TEST123",
                "fromMe": False
            },
            "pushName": "Teste Cliente",
            "message": {
                "conversation": "Quero agendar uma visita para amanhã de tarde"
            },
            "messageType": "conversation"
        }
    }
    print("[OK] Webhook preparado!")
    print()

    # Criar estado inicial
    print("[3] Criando estado inicial...")
    initial_state: AgentState = {
        "raw_webhook_data": {"body": webhook_data},
        "next_action": ""
    }
    print("[OK] Estado criado!")
    print()

    # Executar grafo
    print("[4] Executando grafo...")
    print("-" * 70)
    try:
        final_state = await app.ainvoke(initial_state)
        print("-" * 70)
        print("[OK] Grafo executado!")
        print()

        # Exibir resultado
        print("=" * 70)
        print("RESULTADO DO PROCESSAMENTO")
        print("=" * 70)
        print()

        print(f"Cliente: {final_state.get('cliente_nome', 'N/A')}")
        print(f"Telefone: {final_state.get('cliente_numero', 'N/A')}")
        print(f"Tipo: {final_state.get('tipo_mensagem', 'N/A')}")
        print()

        print(f"Mensagem recebida:")
        print(f"  {final_state.get('mensagem_conteudo', 'N/A')[:100]}...")
        print()

        if final_state.get('resposta_agente'):
            print(f"Resposta do agente:")
            print(f"  {final_state.get('resposta_agente', 'N/A')[:200]}...")
            print()

        fragmentos = final_state.get('respostas_fragmentadas', [])
        print(f"Fragmentos enviados: {len(fragmentos)}")
        if fragmentos:
            for i, frag in enumerate(fragmentos, 1):
                print(f"  [{i}] {len(frag)} chars: {frag[:50]}...")
        print()

        if final_state.get('erro'):
            print(f"ERRO: {final_state['erro']}")
        else:
            print("[OK] Processamento concluído sem erros!")

        print()
        print("=" * 70)

        return True

    except Exception as e:
        print("-" * 70)
        print(f"[ERRO] Falha na execução: {e}")
        import traceback
        traceback.print_exc()
        return False


async def testar_diferentes_tipos():
    """
    Testa diferentes tipos de mensagem.
    """
    print()
    print("=" * 70)
    print("TESTE COM DIFERENTES TIPOS DE MENSAGEM")
    print("=" * 70)
    print()

    app = criar_grafo_atendimento()

    # Casos de teste
    casos = [
        {
            "nome": "Mensagem de texto simples",
            "mensagem": "Olá, gostaria de informações sobre seus serviços",
            "tipo": "conversation"
        },
        {
            "nome": "Agendamento",
            "mensagem": "Quero agendar uma visita para amanhã às 14h",
            "tipo": "conversation"
        },
        {
            "nome": "Pergunta sobre preço",
            "mensagem": "Quanto custa instalação de drywall por m²?",
            "tipo": "conversation"
        }
    ]

    for i, caso in enumerate(casos, 1):
        print(f"\n[Teste {i}] {caso['nome']}")
        print("-" * 70)

        webhook_data = {
            "event": "messages.upsert",
            "instance": "test-instance",
            "data": {
                "key": {
                    "remoteJid": f"55629999999{i}@s.whatsapp.net",
                    "id": f"TEST{i}",
                    "fromMe": False
                },
                "pushName": f"Cliente {i}",
                "message": {
                    "conversation": caso["mensagem"]
                },
                "messageType": caso["tipo"]
            }
        }

        initial_state: AgentState = {
            "raw_webhook_data": {"body": webhook_data},
            "next_action": ""
        }

        try:
            final_state = await app.ainvoke(initial_state)
            print(f"[OK] Cliente: {final_state.get('cliente_nome')}")
            print(f"[OK] Mensagem: {caso['mensagem'][:50]}...")
            print(f"[OK] Processado com sucesso!")
        except Exception as e:
            print(f"[ERRO] {e}")

    print()
    print("=" * 70)
    print("TESTES CONCLUÍDOS")
    print("=" * 70)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Testa o bot diretamente")
    parser.add_argument(
        "--multi",
        action="store_true",
        help="Executar testes com múltiplos casos"
    )

    args = parser.parse_args()

    if args.multi:
        asyncio.run(testar_diferentes_tipos())
    else:
        asyncio.run(testar_bot())
