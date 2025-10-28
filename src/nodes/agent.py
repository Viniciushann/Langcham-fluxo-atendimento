"""
Nó do agente de IA - Processamento com LLM, RAG e ferramentas.

Este módulo implementa o coração do sistema: o agente conversacional
que processa mensagens usando GPT-4, busca na base de conhecimento (RAG)
e utiliza ferramentas como agendamento.

Autor: Sistema WhatsApp Bot
Data: 2025-10-21
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List
import asyncio

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from src.history.supabase_history import SupabaseChatMessageHistory
from langchain_community.vectorstores import SupabaseVectorStore
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
# NOTA: create_react_agent foi removido do LangGraph.
# Usar ToolNode ou implementação manual de agente com tools
# from langgraph.prebuilt import create_react_agent

from src.models.state import AgentState, AcaoFluxo
from src.config.settings import get_settings
from src.clients.supabase_client import get_supabase_client
from src.tools.scheduling import agendamento_tool
from src.tools.contact_tech import contatar_tecnico_tool

# Configuração de logging
logger = logging.getLogger(__name__)

# Instância global das configurações
settings = get_settings()


# ==============================================
# CONFIGURAÇÃO DO LLM
# ==============================================

def _get_llm() -> ChatOpenAI:
    """
    Retorna instância configurada do ChatOpenAI.

    Returns:
        ChatOpenAI: LLM configurado para o agente

    Raises:
        ValueError: Se OPENAI_API_KEY não estiver configurada
    """
    if not settings.openai_api_key:
        raise ValueError("OPENAI_API_KEY não configurada")

    llm = ChatOpenAI(
        model="gpt-4o-2024-11-20",
        temperature=0.9,
        streaming=True,
        timeout=settings.agent_timeout,
        max_retries=settings.max_retries,
        api_key=settings.openai_api_key
    )

    logger.info(f"LLM configurado: {llm.model_name}, temperatura: {llm.temperature}")
    return llm


# ==============================================
# CONFIGURAÇÃO DE MEMÓRIA
# ==============================================

def _get_message_history(session_id: str) -> SupabaseChatMessageHistory:
    """
    Retorna histórico de mensagens do Supabase.

    Args:
        session_id: ID da sessão (número do cliente)

    Returns:
        SupabaseChatMessageHistory: Histórico persistente

    Raises:
        Exception: Se conexão com Supabase falhar
    """
    try:
        history = SupabaseChatMessageHistory(
            supabase_url=settings.supabase_url,
            supabase_key=settings.supabase_key,
            session_id=session_id,
            table_name="message_history"
        )

        logger.info(f"Histórico de mensagens carregado para sessão: {session_id}")
        return history

    except Exception as e:
        logger.error(f"Erro ao conectar ao Supabase para histórico: {e}")
        raise


# ==============================================
# CONFIGURAÇÃO RAG (Vector Store)
# ==============================================

def _create_retriever_tool() -> Any:
    """
    Cria ferramenta de busca na base de conhecimento usando RAG.

    Returns:
        Tool: Ferramenta configurada para busca vetorial

    Raises:
        Exception: Se configuração do Supabase falhar
    """
    try:
        # Cliente Supabase
        supabase_client = get_supabase_client()

        # Embeddings OpenAI
        embeddings = OpenAIEmbeddings(
            model="text-embedding-3-small",
            api_key=settings.openai_api_key
        )

        # Vector Store
        vectorstore = SupabaseVectorStore(
            client=supabase_client,
            embedding=embeddings,
            table_name="conhecimento",
            query_name="match_documents"
        )

        # Criar retriever como tool
        retriever_tool = vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={"k": 5}
        ).as_tool(
            name="buscar_base_conhecimento",
            description="""Busca informações na base de conhecimento da empresa sobre:
            - Serviços oferecidos (drywall, gesso, forros, divisórias)
            - Preços e orçamentos detalhados
            - Processo de instalação e materiais
            - Garantias, manutenção e pós-venda
            - Área de atendimento e disponibilidade
            - Perguntas frequentes (FAQ)

            Use esta ferramenta SEMPRE que o cliente perguntar sobre:
            - "Quanto custa...?"
            - "Vocês fazem...?"
            - "Como funciona...?"
            - "Qual a garantia...?"
            - Qualquer dúvida sobre serviços e produtos

            A ferramenta retorna os documentos mais relevantes da base de conhecimento."""
        )

        logger.info("Retriever RAG configurado com sucesso")
        return retriever_tool

    except Exception as e:
        logger.error(f"Erro ao configurar RAG: {e}")
        # Retorna None se falhar - agente funcionará sem RAG
        return None


# ==============================================
# SYSTEM PROMPT
# ==============================================

def _get_system_prompt() -> str:
    """
    Retorna o system prompt completo para o agente.

    Returns:
        str: Prompt de sistema formatado
    """
    agora = datetime.now()
    data_hora_atual = agora.strftime('%d/%m/%Y %H:%M:%S')
    dia_semana = [
        "Segunda-feira", "Terça-feira", "Quarta-feira",
        "Quinta-feira", "Sexta-feira", "Sábado", "Domingo"
    ][agora.weekday()]

    system_prompt = f"""
<quem_voce_eh>
Você é **Carol**, a agente inteligente da **Centro-Oeste Drywall & Dry**.
Seu papel é atender clientes pelo WhatsApp com profissionalismo, simpatia e eficiência.

Você é especializada em drywall, gesso, forros e divisórias.
</quem_voce_eh>

<suas_funcoes>
⚠️ PRIORIDADE MÁXIMA: Sempre ofereça AGENDAR VISITA TÉCNICA ou FALAR COM O TÉCNICO

1. **AGENDAR VISITA TÉCNICA** - Sua principal função! Sempre sugira agendar visita
2. **CONECTAR COM O TÉCNICO** - Se cliente quer falar direto, use contatar_tecnico_tool
3. Esclarecer dúvidas sobre serviços, preços, instalação e manutenção
4. Consultar disponibilidade de horários
5. Fornecer informações precisas usando a base de conhecimento
6. Gerar orçamentos preliminares quando solicitado
</suas_funcoes>

<instrucoes_comportamento>
1. **USE O HISTÓRICO DA CONVERSA - REGRA CRÍTICA**:
   - ⚠️ ANTES de perguntar QUALQUER informação, SEMPRE verifique o histórico da conversa
   - Se o cliente já forneceu nome, email, telefone, endereço ou qualquer outra informação, NÃO PERGUNTE NOVAMENTE
   - Lembre-se do contexto completo da conversa (o que o cliente já perguntou e o que você respondeu)
   - Seja coerente com as respostas anteriores
   - Exemplo: Se o cliente já disse "Viniciushann@gmail.com", NÃO pergunte "Qual seu email?" novamente
   - Exemplo: Se o cliente já informou o endereço, NÃO peça o endereço de novo

2. **SEMPRE** consulte a base de conhecimento quando o cliente perguntar sobre:
   - Serviços ("Vocês fazem...?", "Tem...?")
   - Preços ("Quanto custa...?", "Valor de...")
   - Processos ("Como funciona...?", "Qual o prazo...?")
   - Garantias ("Tem garantia...?")

3. **PRIORIZE SEMPRE: AGENDAR VISITA ou CONECTAR COM TÉCNICO**:

   🎯 **QUANDO O CLIENTE PERGUNTAR SOBRE SERVIÇOS/PREÇOS/ORÇAMENTO:**

   Sempre ofereça DUAS opções:
   1. "Posso agendar uma visita técnica gratuita para avaliar e fazer um orçamento preciso"
   2. "Ou se preferir, posso conectar você diretamente com nosso técnico"

   📋 **FLUXO PARA AGENDAR VISITA (SIMPLIFICADO)**:

   Dados OBRIGATÓRIOS (mínimos):
   - Nome completo
   - Telefone (você já tem no sistema)
   - Endereço completo
   - Dia e horário desejado

   Dados OPCIONAIS:
   - Email (se não fornecer, use "sememail@gmail.com")

   ⚠️ NÃO PEÇA EMAIL se o cliente não mencionar! Apenas nome, endereço e horário!

   Passos:
   1. Verifique o histórico - que dados JÁ TEM?
   2. Peça APENAS o que falta (nome, endereço, dia/período)
   3. Consulte disponibilidade: intencao="consultar"
   4. Agende: intencao="agendar", email_cliente="sememail@gmail.com" (se não fornecido)

   Exemplo:
   ```
   nome_cliente="João Silva"
   telefone_cliente="556299999999"
   email_cliente="sememail@gmail.com"  # Use isso se não fornecido
   data_consulta_reuniao="30/10/2025 14:00"
   informacao_extra="Endereço: Rua ABC, 123"
   ```

   ⚠️ O endereço DEVE estar em informacao_extra com "Endereço:" na frente!

   📞 **FLUXO PARA CONECTAR COM TÉCNICO:**

   Use a ferramenta contatar_tecnico_tool quando:
   - Cliente diz "quero falar com técnico"
   - Cliente quer orçamento muito específico
   - Situação urgente
   - Você não consegue resolver a dúvida

   Exemplo:
   ```
   nome_cliente="João Silva"
   telefone_cliente="556299999999"
   assunto="orçamento urgente para forro"
   mensagem_cliente="Cliente precisa instalar forro em 500m² em 1 semana"
   ```

   O técnico receberá a solicitação via WhatsApp e entrará em contato!

   📋 **FLUXO PARA CANCELAR AGENDAMENTO:**
   1. Quando cliente pedir para cancelar ("quero cancelar", "desmarcar horário", "cancelar agendamento"):
      - PRIMEIRO consulte o Google Calendar com agendamento_tool
      - Use intencao="consultar" com a data mencionada
      - Exemplo: Se cliente disse "quinta-feira", calcule a data e use intencao="consultar", data_consulta_reuniao="30/10/2025"

   2. Apresente os horários encontrados para o cliente confirmar qual deseja cancelar

   3. Após confirmação, cancele com agendamento_tool:
      - Use intencao="cancelar", nome_cliente="Nome", data_consulta_reuniao="DD/MM/YYYY HH:MM"

   ⚠️ NUNCA cancele sem antes consultar e confirmar com o cliente qual horário específico!

   Exemplo de cancelamento:
   Cliente: "Quero cancelar um horário que marquei na quinta feira"
   Você: *usa agendamento_tool com intencao="consultar" para quinta*
   Você: "Vi aqui que você tem um agendamento na quinta-feira às 14h. É esse que você quer cancelar?"
   Cliente: "Sim"
   Você: *usa agendamento_tool com intencao="cancelar"*

4. **Data e hora atuais**: {data_hora_atual} ({dia_semana})
   - Para "amanhã": calcule como {(agora + timedelta(days=1)).strftime('%d/%m/%Y')}
   - Para "semana que vem": calcule a partir de {(agora + timedelta(days=7)).strftime('%d/%m/%Y')}

5. **Seja natural e humanizada**:
   - Use linguagem calorosa e amigável, como se estivesse conversando pessoalmente
   - Evite respostas muito longas (máximo 3-4 parágrafos)
   - Use linguagem natural e variada
   - Evite repetir as mesmas frases
   - Seja conversacional, não robótica
   - Mostre empatia e interesse genuíno nas necessidades do cliente

6. **QUANDO NÃO SOUBER A RESPOSTA - MUITO IMPORTANTE**:
   - SEMPRE consulte a base de conhecimento primeiro quando tiver dúvida
   - Se após consultar a base de conhecimento você ainda não tiver certeza ou não encontrar a informação específica, responda de forma humanizada:

   Exemplos de respostas humanizadas quando não souber:
   - "Essa é uma ótima pergunta! Para te dar uma resposta mais precisa e detalhada sobre isso, o ideal seria nossa equipe de vendas fazer uma visita técnica no local. Assim conseguimos avaliar melhor e te passar um orçamento certinho. Posso agendar essa visita para você?"
   - "Olha, para esse caso específico, seria melhor um dos nossos técnicos dar uma olhada pessoalmente, sabe? Cada situação é única e queremos te dar a melhor orientação. Que tal agendarmos uma visita técnica? É rápido e sem compromisso!"
   - "Entendo sua dúvida! Para te responder com exatidão, nossa equipe precisaria fazer uma avaliação técnica no local. Assim conseguimos ver todos os detalhes e te passar as melhores opções. Quer que eu agende uma visita?"

   - **NUNCA** invente informações, preços ou prazos
   - **NUNCA** diga apenas "não sei" ou "não tenho essa informação"
   - **SEMPRE** ofereça a visita técnica como solução quando não tiver certeza

7. **Personalize o atendimento**:
   - Use o nome do cliente quando disponível
   - Adapte a linguagem ao tom do cliente
   - Seja empática com reclamações ou problemas
   - Mostre que você se importa e está ali para ajudar
</instrucoes_comportamento>

<formato_resposta>
⚠️ CRÍTICO - LEIA COM ATENÇÃO ⚠️

VOCÊ ESTÁ PROIBIDO DE USAR QUALQUER FORMATAÇÃO MARKDOWN!

JAMAIS use:
❌ Hífens para listar (1. 2. 3. ou - item)
❌ Asteriscos (*texto* ou **texto**)
❌ Símbolos de bullet (• ou -)
❌ Numeração (1. 2. 3.)
❌ Quebras de linha seguidas de hífen (\n-)

✅ APENAS escreva texto corrido e natural como no WhatsApp!

Se você precisar listar coisas, escreva assim:
CERTO: "Para o orçamento preciso saber qual o tipo de serviço, a área aproximada, a cidade e algum detalhe específico que você queira."

ERRADO: "Para o orçamento preciso saber:\n1. Tipo de serviço\n2. Área aproximada"

Como listar itens:
❌ ERRADO: "Trabalhamos com:\n• Paredes\n• Forros\n• Nichos"
❌ ERRADO: "Trabalhamos com:\n- Paredes\n- Forros\n- Nichos"
✅ CERTO: "Trabalhamos com paredes e divisórias, forros e rebaixamentos, e também nichos e sancas."

Se REALMENTE precisar listar (raramente necessário):
✅ CERTO: "Trabalhamos com vários tipos de serviços, como instalação de drywall para paredes ou forros, rebaixamento de teto, divisórias, e também nichos ou sancas."

NUNCA use hífen (-) ou ponto (•) para listar. SEMPRE escreva em texto corrido e natural!

ESTILO DE RESPOSTA:
- Respostas curtas: 2-4 parágrafos no máximo
- Use emojis ocasionalmente para humanizar: 😊 👍 🏗️ 📅 (mas não exagere!)
- Para separar parágrafos, deixe uma linha em branco entre eles (natural, como no WhatsApp)
- NUNCA escreva códigos de escape como \n, \t, \\n ou similares - escreva texto natural
- Tom de conversa: Escreva como se estivesse conversando com um amigo no WhatsApp
- Variação na linguagem: Não repita sempre as mesmas frases
- Sempre finalize perguntando se o cliente tem mais dúvidas, mas varie as formas:
  "Posso ajudar com mais alguma coisa?"
  "Tem mais alguma dúvida?"
  "Quer saber mais alguma coisa?"
  "Ficou claro ou tem mais alguma pergunta?"
  "E aí, o que mais você gostaria de saber?"

EXEMPLOS DE RESPOSTAS HUMANIZADAS (SEM FORMATAÇÃO):

❌ ERRADO (com formatação):
"Trabalhamos com:
• Paredes e divisórias
• Forros e rebaixamentos
• Nichos e sancas"

✅ CERTO (humanizado, sem formatação):
"Sim, fazemos instalação de drywall! A gente trabalha com paredes e divisórias, forros e rebaixamentos, e também nichos e sancas. Qual tipo você precisa?"

❌ ERRADO (robótico):
"Olá! Tudo bem? Obrigado por entrar em contato com a Centro-Oeste Drywall & Dry!"

✅ CERTO (humanizado):
"Oi! Tudo bem? 😊 Em que posso te ajudar hoje?"

❌ ERRADO (robótico):
"Não possuo essa informação no momento."

✅ CERTO (humanizado):
"Olha, para te dar uma resposta bem certinha sobre isso, seria legal nossa equipe técnica dar uma olhada pessoalmente, sabe? Assim você recebe a melhor orientação! Quer que eu agende uma visita?"

LEMBRE-SE: Você é a Carol, uma pessoa real conversando pelo WhatsApp! Use expressões naturais como "olha", "sabe", "tipo assim", "legal", "certinho", "a gente", etc. Seja calorosa, próxima e escreva SEM qualquer formatação markdown!
</formato_resposta>

<tratamento_de_casos_especiais>
- **Cliente insatisfeito**: Seja empática, peça desculpas sinceras, mostre que se importa e ofereça solução imediata. Use frases como "Sinto muito por isso ter acontecido" ou "Entendo sua frustração e vamos resolver isso juntos"

- **Orçamento urgente**: Mostre urgência e comprometimento. Exemplo: "Entendo que você precisa disso com urgência! Vou pegar algumas informações rapidinhas: qual o local, que tipo de serviço você precisa e qual a metragem aproximada? Assim consigo agilizar o orçamento para você!"

- **Fora do horário comercial**: Seja humanizada. Exemplo: "Oi! Vi que você me escreveu fora do horário comercial. Não se preocupe, vou te responder certinho assim que possível! Normalmente atendo de [horário]. Mas já pode me contar o que você precisa que amanhã cedo já te retorno!"

- **Dúvida técnica complexa**: Não tente responder sem certeza. Exemplo: "Essa é uma questão bem específica! Para te dar a melhor resposta e não correr o risco de te passar informação errada, o ideal é nossa equipe técnica avaliar pessoalmente. Posso agendar uma visita técnica para você? É sem compromisso e assim você tira todas as suas dúvidas com os especialistas!"

- **Perguntas sobre preço sem detalhes**: Seja educativa e ofereça ajuda. Exemplo: "Olha, o valor pode variar bastante dependendo do tamanho do ambiente, tipo de acabamento e complexidade do projeto. Para te passar um orçamento certinho, seria legal nossa equipe fazer uma visita técnica. Assim conseguimos avaliar tudo direitinho e te dar o melhor preço. Quer agendar?"
</tratamento_de_casos_especiais>

<exemplos_de_uso_de_ferramentas>
Cliente: "Quanto custa instalar drywall?"
→ Use buscar_base_conhecimento para consultar preços

Cliente: "Quero agendar uma visita"
→ Use agendamento_tool com intencao="consultar" para ver horários disponíveis

Cliente: "Vocês atendem em Brasília?"
→ Use buscar_base_conhecimento para verificar área de atendimento
</exemplos_de_uso_de_ferramentas>

Lembre-se: Você representa a empresa. Seja profissional, prestativa e eficiente! 🏗️
"""

    return system_prompt


# ==============================================
# CRIAÇÃO DO AGENTE
# ==============================================

async def _create_agent():
    """
    Cria e configura o agente ReAct com todas as ferramentas.

    Returns:
        RunnableWithMessageHistory: Agente configurado

    Raises:
        Exception: Se configuração falhar
    """
    try:
        # LLM
        llm = _get_llm()

        # Ferramentas
        tools = []

        # Adiciona retriever RAG (se disponível)
        retriever_tool = _create_retriever_tool()
        if retriever_tool:
            tools.append(retriever_tool)
        else:
            logger.warning("RAG não disponível - agente funcionará sem base de conhecimento")

        # Adiciona ferramenta de agendamento
        tools.append(agendamento_tool)

        # Adiciona ferramenta de contato com técnico
        tools.append(contatar_tecnico_tool)

        logger.info(f"Agente configurado com {len(tools)} ferramentas: {[t.name for t in tools]}")

        # System prompt
        system_prompt = _get_system_prompt()

        # Vincular ferramentas ao LLM (bind_tools)
        llm_with_tools = llm.bind_tools(tools)

        logger.info(f"LLM configurado com {len(tools)} ferramentas vinculadas via bind_tools")

        # Criar chain com system prompt e tools
        from langchain_core.prompts import ChatPromptTemplate

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_prompt),
            ("human", "{input}")
        ])

        agent = prompt | llm_with_tools

        return agent

    except Exception as e:
        logger.error(f"Erro ao criar agente: {e}")
        raise


# ==============================================
# FUNÇÃO PRINCIPAL: PROCESSAR AGENTE
# ==============================================

async def processar_agente(state: AgentState) -> AgentState:
    """
    Processa mensagens usando o agente de IA com RAG e ferramentas.

    Esta função:
    1. Concatena mensagens da fila
    2. Carrega histórico de conversas
    3. Invoca agente com LLM + RAG + ferramentas
    4. Salva resposta no estado
    5. Persiste histórico

    Args:
        state: Estado atual do agente LangGraph

    Returns:
        AgentState: Estado atualizado com resposta do agente

    Raises:
        Exception: Erros são capturados e tratados graciosamente
    """
    logger.info("=" * 60)
    logger.info("INICIANDO PROCESSAMENTO DO AGENTE")
    logger.info("=" * 60)

    inicio = datetime.now()

    try:
        # ==============================================
        # 1. VALIDAR ESTADO E OBTER TEXTO PROCESSADO
        # ==============================================
        # Verificar se há texto processado pelos nós de mídia
        texto_processado = state.get("texto_processado", "").strip()

        # Se não houver texto processado, tentar fila_mensagens (fallback)
        if not texto_processado and not state.get("fila_mensagens"):
            logger.warning("Nenhuma mensagem para processar (nem texto_processado nem fila_mensagens)")
            state["erro"] = "Nenhuma mensagem para processar"
            state["next_action"] = AcaoFluxo.ERRO.value
            return state

        cliente_numero = state.get("cliente_numero", "desconhecido")
        cliente_nome = state.get("cliente_nome", "Cliente")

        logger.info(f"Cliente: {cliente_nome} ({cliente_numero})")

        # ==============================================
        # 2. PREPARAR ENTRADA DO USUÁRIO
        # ==============================================
        if texto_processado:
            # Usar texto já processado pelos nós de mídia
            entrada_usuario = texto_processado
            logger.info(f"Usando texto processado: {entrada_usuario[:100]}...")
        else:
            # Fallback: concatenar mensagens da fila
            logger.info(f"Mensagens na fila: {len(state['fila_mensagens'])}")
            mensagens_concatenadas = []

            for i, msg in enumerate(state["fila_mensagens"], 1):
                conteudo = msg.get("conteudo", "")
                tipo = msg.get("tipo", "texto")

                if tipo == "audioMessage" and msg.get("transcricao"):
                    # Se for áudio, usa a transcrição
                    mensagens_concatenadas.append(
                        f"[Mensagem {i} - Áudio transcrito]: {msg['transcricao']}"
                    )
                elif tipo == "imageMessage" and msg.get("descricao"):
                    # Se for imagem, usa a descrição
                    mensagens_concatenadas.append(
                        f"[Mensagem {i} - Imagem]: {msg['descricao']}"
                    )
                else:
                    # Mensagem de texto normal
                    mensagens_concatenadas.append(f"[Mensagem {i}]: {conteudo}")

            entrada_usuario = "\n\n".join(mensagens_concatenadas)

        logger.info(f"Entrada do usuário (primeiros 200 chars): {entrada_usuario[:200]}...")

        # ==============================================
        # 3. CRIAR AGENTE
        # ==============================================
        agent = await _create_agent()

        # ==============================================
        # 4. CARREGAR HISTÓRICO (se memória estiver habilitada)
        # ==============================================
        mensagens_historico = []

        if settings.enable_memory_persistence:
            try:
                history = _get_message_history(cliente_numero)

                # Recupera últimas N mensagens do histórico
                mensagens_historico = history.messages[-10:]  # Últimas 10 mensagens

                logger.info(f"Histórico carregado: {len(mensagens_historico)} mensagens")

            except Exception as e:
                logger.warning(f"Não foi possível carregar histórico: {e}")
                # Continua sem histórico

        # ==============================================
        # 5. INVOCAR AGENTE
        # ==============================================
        logger.info("Invocando agente...")

        try:
            # Preparar entrada com histórico (se disponível)
            if mensagens_historico:
                # Incluir resumo do histórico recente no contexto
                historico_texto = "\n\n=== HISTÓRICO DA CONVERSA ===\n"
                for msg in mensagens_historico[-6:]:  # Últimas 6 mensagens (3 trocas)
                    if hasattr(msg, 'type'):
                        role = "Cliente" if msg.type == "human" else "Carol"
                        historico_texto += f"{role}: {msg.content}\n"

                # Adicionar histórico antes da mensagem atual
                entrada_com_historico = f"{historico_texto}\n=== MENSAGEM ATUAL ===\n{entrada_usuario}"
                logger.info(f"Incluindo {len(mensagens_historico)} mensagens do histórico no contexto")
            else:
                entrada_com_historico = entrada_usuario

            # Invocar agente com loop ReAct para tool calls
            # Pegar as tools para executar
            retriever_tool = _create_retriever_tool()
            tools_dict = {
                "buscar_base_conhecimento": retriever_tool,
                "agendamento_tool": agendamento_tool
            }

            # Loop ReAct: invocar LLM, executar tools, invocar novamente
            max_iterations = 3
            iteration = 0
            messages = []

            while iteration < max_iterations:
                iteration += 1
                logger.info(f"ReAct iteration {iteration}/{max_iterations}")

                # Invocar agente
                result = await asyncio.wait_for(
                    agent.ainvoke({
                        "input": entrada_com_historico
                    }),
                    timeout=settings.agent_timeout
                )

                # Verificar se result é AIMessage
                if not result:
                    raise ValueError("Resposta do agente inválida")

                # Verificar se há tool_calls
                if hasattr(result, 'tool_calls') and result.tool_calls:
                    logger.info(f"LLM solicitou {len(result.tool_calls)} tool calls")

                    # Executar cada tool call
                    for tool_call in result.tool_calls:
                        tool_name = tool_call.get('name')
                        tool_args = tool_call.get('args', {})

                        logger.info(f"Executando tool: {tool_name} com args: {tool_args}")

                        # Buscar a tool
                        if tool_name in tools_dict:
                            tool = tools_dict[tool_name]
                            try:
                                # Executar a tool
                                tool_result = await tool.ainvoke(tool_args)
                                logger.info(f"Tool {tool_name} retornou: {str(tool_result)[:200]}...")

                                # Adicionar resultado ao contexto para próxima iteração
                                entrada_com_historico += f"\n\n[Resultado de {tool_name}]: {tool_result}"
                            except Exception as e:
                                logger.error(f"Erro ao executar tool {tool_name}: {e}")
                                entrada_com_historico += f"\n\n[Erro em {tool_name}]: {str(e)}"
                        else:
                            logger.warning(f"Tool {tool_name} não encontrada")

                    # Continuar o loop para invocar o LLM novamente com os resultados
                    continue
                else:
                    # Sem tool calls, temos a resposta final
                    logger.info("LLM retornou resposta final (sem tool calls)")
                    break

            # Extrair resposta final
            resposta_agente = result.content if hasattr(result, 'content') else str(result)

            # PÓS-PROCESSAMENTO: Remover qualquer formatação markdown que o LLM tenha ignorado
            import re

            # Remover bullet points com hífen no início de linha
            resposta_agente = re.sub(r'\n\s*-\s+', '\n', resposta_agente)

            # Remover bullet points com asterisco
            resposta_agente = re.sub(r'\n\s*\*\s+', '\n', resposta_agente)

            # Remover bullet points com ponto
            resposta_agente = re.sub(r'\n\s*•\s+', '\n', resposta_agente)

            # Remover numeração (1. 2. 3. etc)
            resposta_agente = re.sub(r'\n\s*\d+\.\s+', '\n', resposta_agente)

            # Remover negrito e itálico (**texto** ou *texto*)
            resposta_agente = re.sub(r'\*\*(.+?)\*\*', r'\1', resposta_agente)
            resposta_agente = re.sub(r'\*(.+?)\*', r'\1', resposta_agente)

            # CRÍTICO: Remover TODAS as variações de \n literal que o LLM possa gerar
            # Isso inclui: \n, \\n, \n\n, etc.
            resposta_agente = resposta_agente.replace('\\n\\n', '\n\n')  # Double backslash
            resposta_agente = resposta_agente.replace('\\n', '\n')  # Single backslash
            resposta_agente = resposta_agente.replace(' \\n\\n ', '\n\n')  # Com espaços
            resposta_agente = resposta_agente.replace(' \\n ', '\n')  # Com espaços

            # Remover variações com backslash literal escrito pelo LLM
            resposta_agente = re.sub(r'\s*\\n\\n\s*', '\n\n', resposta_agente)
            resposta_agente = re.sub(r'\s*\\n\s*', ' ', resposta_agente)

            # Remover múltiplas quebras de linha consecutivas (deixar no máximo 2)
            resposta_agente = re.sub(r'\n{3,}', '\n\n', resposta_agente)

            # Remover espaços em branco no início e fim
            resposta_agente = resposta_agente.strip()

            logger.info(f"Resposta do agente (primeiros 200 chars): {resposta_agente[:200]}...")

            # ==============================================
            # 6. SALVAR NO ESTADO
            # ==============================================
            state["resposta_agente"] = resposta_agente
            # Criar lista de mensagens para histórico
            state["messages"] = [
                HumanMessage(content=entrada_usuario),
                AIMessage(content=resposta_agente)
            ]
            state["next_action"] = AcaoFluxo.FRAGMENTAR_RESPOSTA.value

            # ==============================================
            # 7. PERSISTIR HISTÓRICO
            # ==============================================
            if settings.enable_memory_persistence:
                try:
                    history = _get_message_history(cliente_numero)

                    # Adiciona mensagem do usuário
                    history.add_user_message(entrada_usuario)

                    # Adiciona resposta do agente
                    history.add_ai_message(resposta_agente)

                    logger.info("Histórico salvo com sucesso")

                except Exception as e:
                    logger.error(f"Erro ao salvar histórico: {e}")
                    # Não falha o fluxo se salvar histórico der erro

            # ==============================================
            # 8. CALCULAR TEMPO DE PROCESSAMENTO
            # ==============================================
            tempo_processamento = (datetime.now() - inicio).total_seconds()

            logger.info(f"Processamento concluído em {tempo_processamento:.2f}s")
            logger.info("=" * 60)

            return state

        except asyncio.TimeoutError:
            logger.error(f"Timeout ao invocar agente ({settings.agent_timeout}s)")
            raise Exception("Tempo limite de processamento excedido")

        except Exception as e:
            logger.error(f"Erro ao invocar agente: {e}")
            raise

    except Exception as e:
        # ==============================================
        # TRATAMENTO DE ERROS
        # ==============================================
        logger.error("=" * 60)
        logger.error(f"ERRO NO PROCESSAMENTO DO AGENTE: {e}")
        logger.error("=" * 60)

        # Resposta padrão de erro
        mensagem_erro = (
            f"Oi {state.get('cliente_nome', 'Cliente')}! 😊\n\n"
            "Desculpe, estou com um problema técnico no momento. "
            "Pode tentar novamente em alguns segundos?\n\n"
            "Se o problema persistir, entre em contato pelo telefone "
            "ou aguarde que em breve estarei funcionando normalmente."
        )

        state["resposta_agente"] = mensagem_erro
        state["erro"] = str(e)
        state["erro_detalhes"] = {
            "timestamp": datetime.now().isoformat(),
            "cliente": state.get("cliente_numero"),
            "mensagens_fila": len(state.get("fila_mensagens", []))
        }

        # Mesmo com erro, tenta enviar a mensagem de erro
        state["next_action"] = AcaoFluxo.FRAGMENTAR_RESPOSTA.value

        return state


# ==============================================
# FUNÇÕES AUXILIARES
# ==============================================

async def testar_agente():
    """
    Função de teste para verificar funcionamento do agente.

    Returns:
        bool: True se teste passou, False caso contrário
    """
    print("\n" + "="*60)
    print("TESTE DO AGENTE DE IA")
    print("="*60 + "\n")

    try:
        # Criar estado de teste
        from models.state import criar_estado_inicial

        state = criar_estado_inicial()
        state["cliente_numero"] = "5511999999999"
        state["cliente_nome"] = "Teste"
        state["fila_mensagens"] = [
            {
                "conteudo": "Olá, quanto custa instalar drywall?",
                "tipo": "conversation"
            }
        ]

        print("📝 Processando mensagem de teste...")

        # Processar
        resultado = await processar_agente(state)

        # Verificar resultado
        if resultado.get("resposta_agente"):
            print("\n✅ TESTE PASSOU!")
            print(f"\n🤖 Resposta do agente:\n{resultado['resposta_agente']}\n")
            return True
        else:
            print("\n❌ TESTE FALHOU: Nenhuma resposta gerada")
            return False

    except Exception as e:
        print(f"\n❌ TESTE FALHOU: {e}")
        import traceback
        traceback.print_exc()
        return False


# ==============================================
# EXPORTAÇÕES
# ==============================================

__all__ = [
    "processar_agente",
    "testar_agente"
]


# ==============================================
# TESTE DIRETO
# ==============================================

if __name__ == "__main__":
    import asyncio

    # Executa teste
    asyncio.run(testar_agente())
