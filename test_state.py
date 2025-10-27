"""Teste simples para verificar persistência de estado."""
import asyncio
from src.nodes.media import processar_texto
from src.models.state import AgentState

async def main():
    print("=" * 60)
    print("TESTE DE PERSISTÊNCIA DE ESTADO")
    print("=" * 60)

    # Criar estado inicial
    state = AgentState(
        raw_webhook_data={},
        cliente_numero="5562999999999",
        cliente_nome="Teste",
        mensagem_tipo="conversation",
        mensagem_base64="Olá, como vai?",
        next_action=""
    )

    print("\n1. Estado ANTES de processar_texto:")
    print(f"   mensagem_base64: {state.get('mensagem_base64')}")
    print(f"   texto_processado: {state.get('texto_processado', 'NÃO DEFINIDO')}")

    # Processar texto
    print("\n2. Executando processar_texto...")
    state = await processar_texto(state)

    print("\n3. Estado DEPOIS de processar_texto:")
    print(f"   mensagem_base64: {state.get('mensagem_base64')}")
    print(f"   mensagem_conteudo: {state.get('mensagem_conteudo')}")
    print(f"   texto_processado: {state.get('texto_processado', 'NÃO DEFINIDO')}")

    # Verificar se campo existe
    if "texto_processado" in state:
        print("\n✅ Campo 'texto_processado' FOI adicionado ao estado")
        print(f"   Valor: '{state['texto_processado']}'")
    else:
        print("\n❌ Campo 'texto_processado' NÃO foi adicionado ao estado")

    print("\n" + "=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
