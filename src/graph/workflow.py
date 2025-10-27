"""
Grafo LangGraph - Workflow completo do sistema de atendimento.

Este módulo implementa o grafo StateGraph que conecta todos os nós
do sistema de atendimento via WhatsApp, desde a recepção do webhook
até o envio da resposta fragmentada ao cliente.

Autor: Sistema WhatsApp Bot
Data: 2025-10-21
"""

import logging
from typing import Any, Dict

from langgraph.graph import StateGraph, END

from src.models.state import AgentState, AcaoFluxo
from src.nodes import webhook, media, response, agent

# Configuração de logging
logger = logging.getLogger(__name__)


# ==============================================
# FUNÇÃO PRINCIPAL: CRIAR GRAFO
# ==============================================

def criar_grafo_atendimento():
    """
    Cria e compila o grafo StateGraph completo do sistema de atendimento.

    O grafo implementa o fluxo completo:
    1. Validação de webhook
    2. Verificação/cadastro de cliente
    3. Processamento de mídia (texto, áudio, imagem)
    4. Processamento com agente de IA (quando implementado)
    5. Fragmentação de resposta
    6. Envio sequencial ao WhatsApp

    Returns:
        Grafo compilado pronto para execução

    Example:
        >>> grafo = criar_grafo_atendimento()
        >>> result = await grafo.ainvoke({
        ...     "raw_webhook_data": webhook_data
        ... })
    """
    logger.info("=" * 60)
    logger.info("Criando grafo de atendimento...")
    logger.info("=" * 60)

    # ========== INICIALIZAR GRAFO ==========
    workflow = StateGraph(AgentState)

    # ========== ADICIONAR NÓS ==========

    logger.info("Adicionando nós ao grafo...")

    # Fase 1: Recepção e Cadastro
    workflow.add_node("validar_webhook", webhook.validar_webhook)
    workflow.add_node("verificar_cliente", webhook.verificar_cliente)
    workflow.add_node("cadastrar_cliente", webhook.cadastrar_cliente)
    logger.info("  [OK] Nós de webhook adicionados")

    # Fase 2: Processamento de Mídia
    # Adicionar nó virtual de roteamento
    def processar_midia_router(state: AgentState) -> AgentState:
        """Nó virtual que apenas passa o estado para o roteador."""
        return state

    workflow.add_node("processar_midia", processar_midia_router)
    workflow.add_node("processar_audio", media.processar_audio)
    workflow.add_node("processar_imagem", media.processar_imagem)
    workflow.add_node("processar_texto", media.processar_texto)
    logger.info("  [OK] Nós de mídia adicionados")

    # Fase 3: Agente de IA
    workflow.add_node("processar_agente", agent.processar_agente)
    logger.info("  [OK] Nó de agente adicionado")

    # Fase 4: Envio de Resposta
    workflow.add_node("fragmentar_resposta", response.fragmentar_resposta)
    workflow.add_node("enviar_respostas", response.enviar_respostas)
    logger.info("  [OK] Nós de resposta adicionados")

    # ========== DEFINIR ENTRY POINT ==========
    workflow.set_entry_point("validar_webhook")
    logger.info("  [OK] Entry point definido: validar_webhook")

    # ========== DEFINIR EDGES ==========

    logger.info("Definindo edges...")

    # Validar webhook -> verificar_cliente ou END
    workflow.add_conditional_edges(
        "validar_webhook",
        lambda state: state.get("next_action", AcaoFluxo.END.value),
        {
            AcaoFluxo.VERIFICAR_CLIENTE.value: "verificar_cliente",
            AcaoFluxo.END.value: END
        }
    )
    logger.info("  [OK] Edge: validar_webhook -> verificar_cliente | END")

    # Verificar cliente -> cadastrar ou processar mídia
    workflow.add_conditional_edges(
        "verificar_cliente",
        lambda state: state.get("next_action", AcaoFluxo.END.value),
        {
            AcaoFluxo.CADASTRAR_CLIENTE.value: "cadastrar_cliente",
            AcaoFluxo.PROCESSAR_MIDIA.value: "processar_midia",
            AcaoFluxo.END.value: END
        }
    )
    logger.info("  [OK] Edge: verificar_cliente -> cadastrar_cliente | processar_midia | END")

    # Cadastrar cliente -> verificar cliente novamente (confirmar cadastro)
    workflow.add_conditional_edges(
        "cadastrar_cliente",
        lambda state: state.get("next_action", AcaoFluxo.END.value),
        {
            AcaoFluxo.VERIFICAR_CLIENTE.value: "verificar_cliente",
            AcaoFluxo.END.value: END
        }
    )
    logger.info("  [OK] Edge: cadastrar_cliente -> verificar_cliente | END")

    # Router de tipo de mídia (conditional edges baseado em função)
    workflow.add_conditional_edges(
        "processar_midia",
        media.rotear_tipo_mensagem,
        {
            "processar_audio": "processar_audio",
            "processar_imagem": "processar_imagem",
            "processar_texto": "processar_texto"
        }
    )
    logger.info("  [OK] Edge: processar_midia -> [audio | imagem | texto]")

    # Todos os processadores de mídia -> processar_agente
    workflow.add_edge("processar_audio", "processar_agente")
    workflow.add_edge("processar_imagem", "processar_agente")
    workflow.add_edge("processar_texto", "processar_agente")
    logger.info("  [OK] Edge: [processadores de mídia] -> processar_agente")

    # Processar agente -> fragmentar resposta
    workflow.add_edge("processar_agente", "fragmentar_resposta")
    logger.info("  [OK] Edge: processar_agente -> fragmentar_resposta")

    # Fragmentar resposta -> enviar respostas
    workflow.add_conditional_edges(
        "fragmentar_resposta",
        lambda state: state.get("next_action", AcaoFluxo.END.value),
        {
            AcaoFluxo.ENVIAR_RESPOSTAS.value: "enviar_respostas",
            AcaoFluxo.ERRO.value: END,
            AcaoFluxo.END.value: END
        }
    )
    logger.info("  [OK] Edge: fragmentar_resposta -> enviar_respostas | END")

    # Enviar respostas -> END
    workflow.add_conditional_edges(
        "enviar_respostas",
        lambda state: state.get("next_action", AcaoFluxo.END.value),
        {
            AcaoFluxo.END.value: END,
            AcaoFluxo.ERRO.value: END
        }
    )
    logger.info("  [OK] Edge: enviar_respostas -> END")

    # ========== COMPILAR GRAFO ==========
    logger.info("Compilando grafo...")
    app = workflow.compile()

    logger.info("=" * 60)
    logger.info("Grafo compilado com sucesso!")
    logger.info("=" * 60)

    return app


# ==============================================
# FUNÇÃO DE VISUALIZAÇÃO
# ==============================================

def visualizar_grafo(salvar_arquivo: bool = True) -> str:
    """
    Gera visualização do grafo em formato Mermaid.

    Args:
        salvar_arquivo: Se True, salva em grafo_workflow.mmd

    Returns:
        str: Código Mermaid do grafo

    Example:
        >>> codigo_mermaid = visualizar_grafo()
        >>> print(codigo_mermaid)
    """
    logger.info("Gerando visualização do grafo...")

    try:
        app = criar_grafo_atendimento()

        # Gerar código Mermaid
        mermaid_code = app.get_graph().draw_mermaid()

        if salvar_arquivo:
            caminho = "grafo_workflow.mmd"
            with open(caminho, "w", encoding="utf-8") as f:
                f.write(mermaid_code)
            logger.info(f"Grafo salvo em: {caminho}")

        return mermaid_code

    except Exception as e:
        logger.error(f"Erro ao gerar visualização: {e}")
        raise


# ==============================================
# FUNÇÃO DE VISUALIZAÇÃO PNG (se disponível)
# ==============================================

def visualizar_grafo_png():
    """
    Tenta gerar visualização PNG do grafo (requer graphviz).

    Útil para Jupyter notebooks ou IDEs com suporte a imagens.
    """
    try:
        app = criar_grafo_atendimento()

        # Tentar gerar PNG
        try:
            from IPython.display import Image, display
            png_data = app.get_graph().draw_mermaid_png()
            display(Image(png_data))
            logger.info("Visualização PNG exibida")
        except ImportError:
            # Se não estiver no Jupyter, salvar em arquivo
            png_data = app.get_graph().draw_mermaid_png()
            with open("grafo_workflow.png", "wb") as f:
                f.write(png_data)
            logger.info("Grafo salvo em: grafo_workflow.png")

    except Exception as e:
        logger.error(f"Erro ao gerar PNG: {e}")
        logger.info("Tente instalar graphviz: pip install graphviz")
        # Fallback para Mermaid
        visualizar_grafo()


# ==============================================
# FUNÇÃO DE TESTE
# ==============================================

async def testar_grafo():
    """
    Testa a criação e compilação do grafo.

    Returns:
        bool: True se teste passou, False caso contrário
    """
    print("\n" + "="*60)
    print("TESTE DO GRAFO DE ATENDIMENTO")
    print("="*60 + "\n")

    try:
        # Criar grafo
        print("📊 Criando grafo...")
        grafo = criar_grafo_atendimento()
        print("✅ Grafo criado com sucesso!")

        # Verificar estrutura
        print("\n📋 Estrutura do grafo:")
        nodes = grafo.get_graph().nodes
        print(f"   Nós: {len(nodes)}")
        for node_id in nodes:
            print(f"     - {node_id}")

        # Gerar visualização
        print("\n🎨 Gerando visualização...")
        mermaid = visualizar_grafo(salvar_arquivo=True)
        print("✅ Visualização gerada!")

        print("\n" + "="*60)
        print("TESTE PASSOU!")
        print("="*60 + "\n")

        return True

    except Exception as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        import traceback
        traceback.print_exc()
        return False


# ==============================================
# EXPORTAÇÕES
# ==============================================

__all__ = [
    "criar_grafo_atendimento",
    "visualizar_grafo",
    "visualizar_grafo_png",
    "testar_grafo"
]


# ==============================================
# TESTE DIRETO
# ==============================================

if __name__ == "__main__":
    import asyncio

    # Executar teste
    asyncio.run(testar_grafo())
