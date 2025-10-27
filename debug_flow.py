"""
Script de debug para testar o fluxo completo do bot.
"""
import asyncio
import sys
import logging

# Configurar logging detalhado
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from src.graph.workflow import criar_grafo_atendimento
from src.models.state import criar_estado_inicial

async def testar_fluxo_completo():
    """Testa o fluxo completo com uma mensagem simulada."""

    print("\n" + "="*60)
    print("TESTE DO FLUXO COMPLETO DO BOT")
    print("="*60 + "\n")

    # Dados de webhook simulado
    webhook_data = {
        "event": "messages.upsert",
        "data": {
            "key": {
                "remoteJid": "556299999999@s.whatsapp.net",
                "fromMe": False,
                "id": "TEST123"
            },
            "message": {
                "conversation": "Olá! Quanto custa drywall?"
            },
            "messageType": "conversation",
            "pushName": "Cliente Teste"
        }
    }

    try:
        # 1. Criar grafo
        print("1. Criando grafo...")
        grafo = criar_grafo_atendimento()
        print("   [OK] Grafo criado com sucesso\n")

        # 2. Criar estado inicial
        print("2. Criando estado inicial...")
        estado_inicial = criar_estado_inicial(webhook_data)
        print(f"   [OK] Estado criado")
        print(f"   - Cliente: {estado_inicial.get('cliente_numero')}")
        print(f"   - Nome: {estado_inicial.get('cliente_nome')}\n")

        # 3. Executar grafo
        print("3. Executando grafo...\n")
        resultado = await grafo.ainvoke(estado_inicial)

        # 4. Verificar resultado
        print("\n4. RESULTADO:")
        print("-" * 60)

        if resultado.get("erro"):
            print(f"[ERRO]: {resultado['erro']}")
            return False

        if resultado.get("resposta_agente"):
            print(f"[OK] Resposta do agente:")
            print(f"  {resultado['resposta_agente'][:200]}...")
        else:
            print("[AVISO] Nenhuma resposta do agente gerada")

        if resultado.get("fragmentos_resposta"):
            print(f"\n[OK] Fragmentos criados: {len(resultado['fragmentos_resposta'])}")
            for i, frag in enumerate(resultado['fragmentos_resposta'][:3], 1):
                print(f"  Fragmento {i}: {frag[:50]}...")
        else:
            print("\n[AVISO] Nenhum fragmento criado")

        print(f"\nAção final: {resultado.get('next_action')}")
        print("-" * 60)

        return True

    except Exception as e:
        print(f"\n[ERRO] ERRO NO TESTE: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    resultado = asyncio.run(testar_fluxo_completo())
    sys.exit(0 if resultado else 1)
