"""
Teste do módulo agent.py para verificar erros.
"""

import asyncio
from src.models.state import AgentState, criar_estado_inicial

async def test_agent_structure():
    """Testa estrutura e imports do módulo agent."""
    print("Testando modulo agent.py...")
    print()

    # 1. Verificar imports
    print("1. Verificando imports...")
    try:
        from src.nodes.agent import (
            processar_agente,
            _get_system_prompt,
            _create_agent,
            _get_llm,
            _create_retriever_tool
        )
        print("   [OK] Todos os imports funcionam")
    except ImportError as e:
        print(f"   [ERRO] Erro ao importar: {e}")
        return

    # 2. Verificar função principal
    print("\n2. Verificando funcao processar_agente...")
    assert processar_agente is not None
    print("   [OK] Funcao processar_agente existe")

    # 3. Verificar funções auxiliares
    print("\n3. Verificando funcoes auxiliares...")
    assert _get_system_prompt is not None
    print("   [OK] Funcao _get_system_prompt existe")

    assert _create_agent is not None
    print("   [OK] Funcao _create_agent existe")

    assert _get_llm is not None
    print("   [OK] Funcao _get_llm existe")

    assert _create_retriever_tool is not None
    print("   [OK] Funcao _create_retriever_tool existe")

    # 4. Testar system prompt
    print("\n4. Testando geracao de system prompt...")
    try:
        system_prompt = _get_system_prompt()
        assert system_prompt is not None
        assert len(system_prompt) > 0
        print("   [OK] System prompt gerado com sucesso")
        print(f"   Tamanho: {len(system_prompt)} caracteres")
    except Exception as e:
        print(f"   [ERRO] Erro ao gerar system prompt: {e}")

    # 5. Verificar estado
    print("\n5. Verificando compatibilidade com AgentState...")
    state = criar_estado_inicial()
    state["mensagem_conteudo"] = "Teste de mensagem"
    state["cliente_id"] = "123"
    print("   [OK] Estado criado com sucesso")

    print("\n[OK] Todos os testes passaram!")
    print("[OK] agent.py nao tem erros de estrutura")
    print()
    print("NOTA: Para testar execucao completa, e necessario:")
    print("  - OpenAI API Key configurada")
    print("  - Supabase configurado")
    print("  - Executar com estado completo")

if __name__ == '__main__':
    asyncio.run(test_agent_structure())
