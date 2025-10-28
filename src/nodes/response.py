"""
Nó de envio de respostas - Fragmentação e envio para WhatsApp.

Este módulo implementa a fragmentação inteligente de respostas longas
e o envio sequencial para o WhatsApp, simulando uma conversa natural.

Autor: Sistema WhatsApp Bot
Data: 2025-10-21
"""

import re
import logging
import asyncio
from datetime import datetime
from typing import List

from src.models.state import AgentState, AcaoFluxo
from src.config.settings import get_settings
from src.clients.whatsapp_client import WhatsAppClient

# Configuração de logging
logger = logging.getLogger(__name__)

# Instância global das configurações
settings = get_settings()


# ==============================================
# FRAGMENTAÇÃO DE TEXTO
# ==============================================

def quebrar_texto_inteligente(texto: str, max_chars: int = 300) -> List[str]:
    """
    Quebra texto em fragmentos respeitando parágrafos e frases completas.

    Algoritmo:
    1. Se texto <= max_chars, retorna como está
    2. Divide por parágrafos (\\n\\n)
    3. Para cada parágrafo maior que max_chars:
       - Divide por frases (terminadas em . ! ?)
       - Agrupa frases até atingir max_chars
       - Garante que não quebra no meio de uma frase

    Args:
        texto: Texto a ser fragmentado
        max_chars: Tamanho máximo de cada fragmento (default: 300)

    Returns:
        List[str]: Lista de fragmentos

    Example:
        >>> texto = "Olá! Tudo bem?\\n\\nEste é um exemplo."
        >>> fragmentos = quebrar_texto_inteligente(texto, 20)
        >>> print(fragmentos)
        ['Olá! Tudo bem?', 'Este é um exemplo.']
    """
    # Validação
    if not texto or not texto.strip():
        return []

    # Se já é menor que max, retorna direto
    if len(texto) <= max_chars:
        return [texto.strip()]

    # Dividir por parágrafos
    paragrafos = texto.split('\n\n')
    fragmentos = []

    for paragrafo in paragrafos:
        paragrafo = paragrafo.strip()
        if not paragrafo:
            continue

        # Se parágrafo é pequeno, adiciona direto
        if len(paragrafo) <= max_chars:
            fragmentos.append(paragrafo)
            continue

        # Parágrafo grande - dividir por frases
        # Pattern: captura frase + pontuação + espaço
        frases = re.split(r'([.!?]+\s+)', paragrafo)

        fragmento_atual = ""

        for i in range(0, len(frases), 2):
            # Frase atual + pontuação (se houver)
            frase = frases[i]
            pontuacao = frases[i + 1] if i + 1 < len(frases) else ""
            texto_completo = frase + pontuacao

            # Tenta adicionar ao fragmento atual
            if len(fragmento_atual) + len(texto_completo) <= max_chars:
                fragmento_atual += texto_completo
            else:
                # Fragmento atual está cheio
                if fragmento_atual:
                    fragmentos.append(fragmento_atual.strip())

                # Inicia novo fragmento
                # Se a frase sozinha é maior que max_chars, quebra por palavras
                if len(texto_completo) > max_chars:
                    # Quebra por palavras
                    palavras = texto_completo.split()
                    temp = ""

                    for palavra in palavras:
                        if len(temp) + len(palavra) + 1 <= max_chars:
                            temp += (" " if temp else "") + palavra
                        else:
                            if temp:
                                fragmentos.append(temp.strip())
                            temp = palavra

                    fragmento_atual = temp
                else:
                    fragmento_atual = texto_completo

        # Adiciona último fragmento
        if fragmento_atual:
            fragmentos.append(fragmento_atual.strip())

    # Remove fragmentos vazios
    fragmentos = [f for f in fragmentos if f.strip()]

    return fragmentos


def fragmentar_resposta(state: AgentState) -> AgentState:
    """
    Fragmenta a resposta do agente em múltiplas mensagens.

    Esta função pega a resposta completa gerada pelo agente e a divide
    em fragmentos menores para envio sequencial, simulando uma conversa
    natural e evitando mensagens muito longas.

    Args:
        state: Estado atual do agente LangGraph

    Returns:
        AgentState: Estado atualizado com fragmentos

    Example:
        >>> state["resposta_agente"] = "Olá!\\n\\nComo posso ajudar?"
        >>> state = fragmentar_resposta(state)
        >>> print(state["respostas_fragmentadas"])
        ['Olá!', 'Como posso ajudar?']
    """
    logger.info("=" * 60)
    logger.info("INICIANDO FRAGMENTAÇÃO DE RESPOSTA")
    logger.info("=" * 60)

    inicio = datetime.now()

    try:
        # ==============================================
        # 1. VALIDAR RESPOSTA
        # ==============================================
        resposta_agente = state.get("resposta_agente", "")

        if not resposta_agente or not resposta_agente.strip():
            logger.warning("Nenhuma resposta do agente para fragmentar")
            state["erro"] = "Resposta vazia"
            state["next_action"] = AcaoFluxo.ERRO.value
            return state

        logger.info(f"Resposta do agente ({len(resposta_agente)} chars):")
        logger.info(f"{resposta_agente[:200]}...")

        # ==============================================
        # 2. OBTER MAX_FRAGMENT_SIZE
        # ==============================================
        max_fragment_size = settings.max_fragment_size

        logger.info(f"Tamanho máximo de fragmento: {max_fragment_size} chars")

        # ==============================================
        # 3. FRAGMENTAR
        # ==============================================
        fragmentos = quebrar_texto_inteligente(resposta_agente, max_fragment_size)

        if not fragmentos:
            logger.warning("Nenhum fragmento gerado")
            # Usa resposta original como único fragmento
            fragmentos = [resposta_agente]

        logger.info(f"✅ Resposta fragmentada em {len(fragmentos)} parte(s)")

        # Log de cada fragmento
        for i, fragmento in enumerate(fragmentos, 1):
            logger.info(f"  Fragmento {i}/{len(fragmentos)} ({len(fragmento)} chars): {fragmento[:50]}...")

        # ==============================================
        # 4. SALVAR NO ESTADO
        # ==============================================
        state["respostas_fragmentadas"] = fragmentos
        state["next_action"] = AcaoFluxo.ENVIAR_RESPOSTAS.value

        # ==============================================
        # 5. MÉTRICAS
        # ==============================================
        tempo_processamento = (datetime.now() - inicio).total_seconds()

        logger.info(f"Fragmentação concluída em {tempo_processamento:.3f}s")
        logger.info("=" * 60)

        return state

    except Exception as e:
        logger.error("=" * 60)
        logger.error(f"ERRO NA FRAGMENTAÇÃO: {e}")
        logger.error("=" * 60)

        # Em caso de erro, usa resposta original sem fragmentar
        state["respostas_fragmentadas"] = [state.get("resposta_agente", "Erro ao processar resposta")]
        state["next_action"] = AcaoFluxo.ENVIAR_RESPOSTAS.value
        state["erro"] = str(e)

        return state


# ==============================================
# LIMPEZA DE MENSAGENS
# ==============================================

def limpar_mensagem(texto: str) -> str:
    """
    Normaliza quebras de linha e remove caracteres problemáticos.

    Operações realizadas:
    - Normaliza quebras de linha Windows (\\r\\n) para Unix (\\n)
    - Normaliza quebras de linha Mac (\\r) para Unix (\\n)
    - Substitui tabs (\\t) por espaços

    Args:
        texto: Texto a ser limpo

    Returns:
        str: Texto normalizado

    Example:
        >>> limpar_mensagem('Teste\\r\\ncom\\tquebras')
        'Teste\\ncom quebras'
    """
    if not texto:
        return ""

    # Sequência de limpeza (ordem importa!)
    texto_limpo = (
        texto
        .replace('\r\n', '\n')   # Normalizar quebras de linha Windows
        .replace('\r', '\n')     # Normalizar quebras de linha Mac
        .replace('\t', ' ')      # Substituir tabs por espaços
    )

    return texto_limpo


# ==============================================
# ENVIO DE RESPOSTAS
# ==============================================

async def enviar_respostas(state: AgentState) -> AgentState:
    """
    Envia fragmentos de resposta para o WhatsApp de forma sequencial.

    Esta função:
    1. Valida fragmentos
    2. Instancia WhatsAppClient
    3. Para cada fragmento:
       - Envia status "digitando"
       - Limpa caracteres especiais
       - Envia mensagem (com retry)
       - Aguarda intervalo natural
    4. Registra estatísticas

    Args:
        state: Estado atual do agente LangGraph

    Returns:
        AgentState: Estado atualizado

    Raises:
        Exception: Erros são capturados e logados, mas não interrompem o fluxo
    """
    logger.info("=" * 60)
    logger.info("INICIANDO ENVIO DE RESPOSTAS")
    logger.info("=" * 60)

    inicio = datetime.now()

    # Estatísticas
    total_fragmentos = 0
    enviados_sucesso = 0
    enviados_erro = 0

    try:
        # ==============================================
        # 1. VALIDAR FRAGMENTOS
        # ==============================================
        fragmentos = state.get("respostas_fragmentadas", [])

        if not fragmentos:
            logger.warning("Nenhum fragmento para enviar")
            state["erro"] = "Nenhum fragmento disponível"
            state["next_action"] = AcaoFluxo.END.value
            return state

        total_fragmentos = len(fragmentos)
        cliente_numero = state.get("cliente_numero", "")

        if not cliente_numero:
            logger.error("Número do cliente não encontrado no estado")
            state["erro"] = "Número do cliente ausente"
            state["next_action"] = AcaoFluxo.ERRO.value
            return state

        logger.info(f"Cliente: {cliente_numero}")
        logger.info(f"Total de fragmentos a enviar: {total_fragmentos}")

        # ==============================================
        # 2. INSTANCIAR WHATSAPP CLIENT
        # ==============================================
        whatsapp = WhatsAppClient(
            base_url=settings.whatsapp_api_url,
            api_key=settings.whatsapp_api_key,
            instance=settings.whatsapp_instance
        )

        logger.info("WhatsAppClient inicializado")

        # ==============================================
        # 3. ENVIAR FRAGMENTOS
        # ==============================================
        intervalo_entre_mensagens = 1.5  # segundos

        for i, fragmento in enumerate(fragmentos, 1):
            logger.info("-" * 40)
            logger.info(f"Fragmento {i}/{total_fragmentos}")
            logger.info(f"Tamanho: {len(fragmento)} chars")
            logger.info(f"Preview: {fragmento[:100]}...")

            # ==============================================
            # 3.1 ENVIAR STATUS "DIGITANDO"
            # ==============================================
            try:
                await whatsapp.enviar_status_typing(cliente_numero)
                logger.info("✅ Status 'digitando' enviado")
            except Exception as e:
                logger.warning(f"Erro ao enviar status digitando: {e}")
                # Não é crítico, continua

            # Aguarda um pouco para parecer que está digitando
            await asyncio.sleep(0.5)

            # ==============================================
            # 3.2 LIMPAR MENSAGEM
            # ==============================================
            mensagem_limpa = limpar_mensagem(fragmento)

            # ==============================================
            # 3.3 ENVIAR MENSAGEM (COM RETRY)
            # ==============================================
            max_tentativas = 3
            tentativa = 0
            enviado = False

            while tentativa < max_tentativas and not enviado:
                tentativa += 1

                try:
                    logger.info(f"Tentativa {tentativa}/{max_tentativas} de envio...")

                    resultado = await whatsapp.enviar_mensagem(
                        telefone=cliente_numero,
                        texto=mensagem_limpa
                    )

                    # Se chegou aqui sem exceção, consideramos sucesso
                    if resultado:
                        logger.info(f"[OK] Fragmento {i}/{total_fragmentos} enviado com sucesso!")
                        enviados_sucesso += 1
                        enviado = True
                    else:
                        logger.warning(f"[AVISO] Resposta vazia da API")

                        if tentativa < max_tentativas:
                            logger.info(f"Aguardando 2s antes de tentar novamente...")
                            await asyncio.sleep(2)

                except Exception as e:
                    logger.error(f"[ERRO] Erro ao enviar fragmento: {e}")

                    if tentativa < max_tentativas:
                        logger.info(f"Aguardando 2s antes de tentar novamente...")
                        await asyncio.sleep(2)

            # Verificar se conseguiu enviar
            if not enviado:
                logger.error(f"❌ Falha ao enviar fragmento {i} após {max_tentativas} tentativas")
                enviados_erro += 1
                # Continua para próximo fragmento ao invés de parar tudo

            # ==============================================
            # 3.4 AGUARDAR INTERVALO NATURAL
            # ==============================================
            if i < total_fragmentos:  # Não espera após última mensagem
                logger.info(f"Aguardando {intervalo_entre_mensagens}s antes do próximo fragmento...")
                await asyncio.sleep(intervalo_entre_mensagens)

        # ==============================================
        # 4. ESTATÍSTICAS FINAIS
        # ==============================================
        tempo_total = (datetime.now() - inicio).total_seconds()

        logger.info("=" * 60)
        logger.info("ESTATÍSTICAS DE ENVIO")
        logger.info("=" * 60)
        logger.info(f"Total de fragmentos: {total_fragmentos}")
        logger.info(f"Enviados com sucesso: {enviados_sucesso}")
        logger.info(f"Erros: {enviados_erro}")
        logger.info(f"Taxa de sucesso: {(enviados_sucesso/total_fragmentos)*100:.1f}%")
        logger.info(f"Tempo total: {tempo_total:.2f}s")
        logger.info("=" * 60)

        # ==============================================
        # 5. ATUALIZAR ESTADO
        # ==============================================
        state["next_action"] = AcaoFluxo.END.value

        # Salvar estatísticas no estado
        state["envio_stats"] = {
            "total_fragmentos": total_fragmentos,
            "enviados_sucesso": enviados_sucesso,
            "enviados_erro": enviados_erro,
            "tempo_total": tempo_total,
            "taxa_sucesso": (enviados_sucesso / total_fragmentos) * 100 if total_fragmentos > 0 else 0
        }

        return state

    except Exception as e:
        # ==============================================
        # TRATAMENTO DE ERROS CRÍTICOS
        # ==============================================
        logger.error("=" * 60)
        logger.error(f"ERRO CRÍTICO NO ENVIO DE RESPOSTAS: {e}")
        logger.error("=" * 60)

        state["erro"] = str(e)
        state["next_action"] = AcaoFluxo.ERRO.value

        # Salvar estatísticas mesmo em erro
        state["envio_stats"] = {
            "total_fragmentos": total_fragmentos,
            "enviados_sucesso": enviados_sucesso,
            "enviados_erro": enviados_erro,
            "erro": str(e)
        }

        return state


# ==============================================
# FUNÇÕES AUXILIARES DE TESTE
# ==============================================

async def testar_fragmentacao():
    """
    Testa a função de fragmentação com diferentes tamanhos de texto.

    Returns:
        bool: True se teste passou, False caso contrário
    """
    print("\n" + "="*60)
    print("TESTE DE FRAGMENTAÇÃO")
    print("="*60 + "\n")

    # Texto de teste
    texto_longo = """Olá! Tudo bem? 😊

Que bom que entrou em contato! Trabalhamos com instalação de drywall, gesso e forros.

Nossos serviços incluem:
• Paredes de drywall
• Divisórias
• Forros e rebaixamentos
• Nichos e sancas

Os preços variam de R$ 80 a R$ 120 por m², dependendo do tipo de material e acabamento escolhido.

Gostaria de agendar uma visita técnica gratuita para fazermos um orçamento mais preciso? 👍"""

    print(f"📝 Texto original ({len(texto_longo)} chars):")
    print(texto_longo)
    print("\n" + "-"*60 + "\n")

    # Fragmentar
    fragmentos = quebrar_texto_inteligente(texto_longo, max_chars=150)

    print(f"✂️ Fragmentado em {len(fragmentos)} parte(s):\n")

    for i, fragmento in enumerate(fragmentos, 1):
        print(f"[Fragmento {i}] ({len(fragmento)} chars):")
        print(fragmento)
        print()

    # Verificar
    if len(fragmentos) > 0:
        print("✅ TESTE PASSOU!")
        return True
    else:
        print("❌ TESTE FALHOU!")
        return False


async def testar_limpeza():
    """
    Testa a função de limpeza de mensagens.

    Returns:
        bool: True se teste passou, False caso contrário
    """
    print("\n" + "="*60)
    print("TESTE DE LIMPEZA DE MENSAGENS")
    print("="*60 + "\n")

    textos_teste = [
        'Teste com "aspas"',
        'Teste com \n quebra de linha',
        'Teste com *asteriscos* e _underscores_',
        'Teste com #hashtag',
        'Teste com \\ barra invertida',
    ]

    for texto in textos_teste:
        limpo = limpar_mensagem(texto)
        print(f"Original: {repr(texto)}")
        print(f"Limpo:    {repr(limpo)}")
        print()

    print("✅ TESTE CONCLUÍDO!")
    return True


# ==============================================
# EXPORTAÇÕES
# ==============================================

__all__ = [
    "quebrar_texto_inteligente",
    "limpar_mensagem",
    "fragmentar_resposta",
    "enviar_respostas",
    "testar_fragmentacao",
    "testar_limpeza"
]


# ==============================================
# TESTE DIRETO
# ==============================================

if __name__ == "__main__":
    import asyncio

    async def main():
        print("\n🧪 Executando testes...\n")

        # Teste de fragmentação
        await testar_fragmentacao()

        # Teste de limpeza
        await testar_limpeza()

        print("\n✅ Todos os testes concluídos!\n")

    asyncio.run(main())
