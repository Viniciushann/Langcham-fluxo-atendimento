# 🤖 Documentação do Agente de IA

Documentação completa do nó `agent.py` - o coração do sistema de atendimento.

---

## 📋 Visão Geral

O **agente de IA** é responsável por processar mensagens dos clientes usando GPT-4, buscar informações na base de conhecimento (RAG) e executar ações através de ferramentas (como agendamento).

### Arquivo
- **Localização**: `src/nodes/agent.py`
- **Função Principal**: `processar_agente(state: AgentState) -> AgentState`

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────┐
│                   processar_agente()                     │
│                                                          │
│  1. Valida estado e concatena mensagens                 │
│  2. Carrega histórico do PostgreSQL                     │
│  3. Cria agente ReAct com:                              │
│     - LLM: GPT-4o                                       │
│     - Tools: [RAG, Agendamento]                         │
│     - System Prompt: Carol (assistente)                 │
│  4. Invoca agente (timeout: 120s)                       │
│  5. Salva resposta no estado                            │
│  6. Persiste histórico                                  │
│                                                          │
└─────────────────────────────────────────────────────────┘
```

---

## ⚙️ Componentes

### 1. **LLM - ChatOpenAI**

```python
ChatOpenAI(
    model="gpt-4o-2024-11-20",
    temperature=0.9,
    streaming=True,
    timeout=120,
    max_retries=3
)
```

**Características:**
- ✅ Modelo: GPT-4o (otimizado)
- ✅ Temperatura: 0.9 (criativo mas controlado)
- ✅ Streaming: Habilitado
- ✅ Timeout: 120 segundos
- ✅ Retries: até 3 tentativas

### 2. **Memória - PostgresChatMessageHistory**

```python
PostgresChatMessageHistory(
    connection_string=settings.postgres_connection_string,
    session_id=cliente_numero,
    table_name="message_history"
)
```

**Características:**
- ✅ Persistência em PostgreSQL
- ✅ Session ID = número do cliente
- ✅ Histórico das últimas 10 mensagens
- ✅ Carregamento automático no início
- ✅ Salvamento automático após resposta

### 3. **RAG - SupabaseVectorStore**

```python
SupabaseVectorStore(
    client=supabase_client,
    embedding=OpenAIEmbeddings("text-embedding-3-small"),
    table_name="conhecimento",
    query_name="match_documents"
)
```

**Características:**
- ✅ Embeddings: text-embedding-3-small
- ✅ Busca vetorial por similaridade
- ✅ Top K: 5 documentos mais relevantes
- ✅ Tabela: `conhecimento`

**Ferramenta RAG:**
```python
retriever_tool = vectorstore.as_retriever(
    search_kwargs={"k": 5}
).as_tool(
    name="buscar_base_conhecimento",
    description="Busca informações sobre serviços, preços, garantias..."
)
```

### 4. **Ferramentas**

| Ferramenta | Descrição | Uso |
|------------|-----------|-----|
| `buscar_base_conhecimento` | Busca vetorial RAG | Dúvidas sobre serviços, preços |
| `agendamento_tool` | Agendamento Google Calendar | Agendar/cancelar/consultar horários |

### 5. **System Prompt - Carol**

**Personalidade:**
- Nome: Carol
- Empresa: Centro-Oeste Drywall & Dry
- Tom: Profissional, simpática, objetiva
- Especialidade: Drywall, gesso, forros

**Instruções:**
1. Sempre consultar base de conhecimento para dúvidas
2. Usar ferramenta de agendamento quando solicitado
3. Respostas curtas (2-4 parágrafos)
4. Emojis ocasionais 😊
5. Nunca inventar informações

**Formato de Resposta:**
- Objetiva mas amigável
- Máximo 3-4 parágrafos
- Quebrar em parágrafos se longo
- Sempre perguntar se tem mais dúvidas

---

## 🔄 Fluxo de Processamento

### Passo a Passo

#### 1️⃣ **Validação do Estado**
```python
if not state.get("fila_mensagens"):
    state["erro"] = "Nenhuma mensagem para processar"
    state["next_action"] = AcaoFluxo.ERRO.value
    return state
```

#### 2️⃣ **Concatenação de Mensagens**
```python
mensagens_concatenadas = []
for msg in state["fila_mensagens"]:
    if tipo == "audioMessage":
        mensagens_concatenadas.append(msg['transcricao'])
    elif tipo == "imageMessage":
        mensagens_concatenadas.append(msg['descricao'])
    else:
        mensagens_concatenadas.append(msg['conteudo'])

entrada_usuario = "\n\n".join(mensagens_concatenadas)
```

#### 3️⃣ **Carregamento de Histórico**
```python
if settings.enable_memory_persistence:
    history = _get_message_history(cliente_numero)
    mensagens_historico = history.messages[-10:]  # Últimas 10
```

#### 4️⃣ **Criação do Agente**
```python
agent = create_react_agent(
    llm=ChatOpenAI(...),
    tools=[retriever_tool, agendamento_tool],
    state_modifier=system_prompt
)
```

#### 5️⃣ **Invocação do Agente**
```python
result = await asyncio.wait_for(
    agent.ainvoke({
        "messages": [*mensagens_historico, HumanMessage(entrada_usuario)]
    }),
    timeout=120
)

resposta_agente = result["messages"][-1].content
```

#### 6️⃣ **Salvamento no Estado**
```python
state["resposta_agente"] = resposta_agente
state["messages"] = result["messages"]
state["next_action"] = AcaoFluxo.FRAGMENTAR_RESPOSTA.value
```

#### 7️⃣ **Persistência do Histórico**
```python
if settings.enable_memory_persistence:
    history.add_user_message(entrada_usuario)
    history.add_ai_message(resposta_agente)
```

---

## 🛠️ Configurações

### Variáveis de Ambiente

```env
# LLM
OPENAI_API_KEY=sk-proj-xxx
AGENT_MODEL=gpt-4o-2024-11-20
AGENT_TEMPERATURE=0.9
AGENT_MAX_TOKENS=2000
AGENT_TIMEOUT=120
AGENT_MAX_ITERATIONS=10

# Memória
POSTGRES_CONNECTION_STRING=postgresql://...
ENABLE_MEMORY_PERSISTENCE=true

# RAG
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=xxx
```

### Configurações no settings.py

```python
settings = get_settings()

# Acessar configurações
settings.agent_model          # "gpt-4o-2024-11-20"
settings.agent_temperature    # 0.9
settings.agent_timeout        # 120
settings.enable_memory_persistence  # True
```

---

## 🎯 Casos de Uso

### Caso 1: Pergunta sobre Serviços

**Entrada:**
```
Cliente: "Quanto custa instalar drywall em uma sala de 20m²?"
```

**Processamento:**
1. Agente identifica que é pergunta sobre preço
2. Usa `buscar_base_conhecimento`
3. Recupera documentos sobre preços e instalação
4. Gera resposta baseada nos documentos

**Saída:**
```
Olá! 😊

Para uma sala de 20m², o valor varia entre R$ 80-120/m²
dependendo do tipo de drywall escolhido:

• Drywall padrão: R$ 80-90/m²
• Drywall verde (resistente à umidade): R$ 95-110/m²
• Drywall RF (resistente ao fogo): R$ 100-120/m²

Quer agendar uma visita técnica gratuita para um orçamento
mais preciso? 👍
```

### Caso 2: Agendamento

**Entrada:**
```
Cliente: "Quero agendar uma visita técnica para amanhã de tarde"
```

**Processamento:**
1. Agente detecta intenção de agendamento
2. Calcula data (amanhã = hoje + 1 dia)
3. Usa `agendamento_tool` com `intencao="consultar"`
4. Filtra horários da tarde
5. Apresenta opções

**Saída:**
```
Claro! 📅

Tenho estes horários disponíveis amanhã (22/10) à tarde:

• 14:00 - 15:00
• 15:00 - 16:00
• 16:00 - 17:00

Qual você prefere?
```

### Caso 3: Múltiplas Mensagens

**Entrada:**
```
Fila de mensagens:
1. "Oi"
2. "Preciso de ajuda"
3. "Quero instalar gesso no teto"
```

**Processamento:**
1. Concatena as 3 mensagens
2. Contextualiza que é sobre instalação de gesso
3. Busca informações na base de conhecimento
4. Responde de forma completa

**Saída:**
```
Olá! Tudo bem? 😊

Que bom que entrou em contato! Trabalhamos com instalação
de forro de gesso.

Posso te passar mais informações sobre valores e prazos.
Qual o tamanho aproximado do teto?
```

---

## 🚨 Tratamento de Erros

### Timeout

```python
try:
    result = await asyncio.wait_for(
        agent.ainvoke(...),
        timeout=120
    )
except asyncio.TimeoutError:
    logger.error("Timeout ao invocar agente")
    state["resposta_agente"] = "Desculpe, erro técnico..."
    state["next_action"] = AcaoFluxo.FRAGMENTAR_RESPOSTA.value
```

### Erro de API (OpenAI)

```python
except Exception as e:
    logger.error(f"Erro ao invocar agente: {e}")
    mensagem_erro = (
        "Oi! 😊\n\n"
        "Desculpe, estou com um problema técnico no momento. "
        "Pode tentar novamente em alguns segundos?"
    )
    state["resposta_agente"] = mensagem_erro
```

### RAG Indisponível

```python
retriever_tool = _create_retriever_tool()
if retriever_tool:
    tools.append(retriever_tool)
else:
    logger.warning("RAG não disponível - agente sem base de conhecimento")
    # Continua funcionando sem RAG
```

---

## 📊 Logging

### Logs Gerados

```
INFO: ============================================================
INFO: INICIANDO PROCESSAMENTO DO AGENTE
INFO: ============================================================
INFO: Cliente: João Silva (5511999999999)
INFO: Mensagens na fila: 2
INFO: Entrada do usuário (primeiros 200 chars): [Mensagem 1]: Olá...
INFO: LLM configurado: gpt-4o-2024-11-20, temperatura: 0.9
INFO: Retriever RAG configurado com sucesso
INFO: Agente configurado com 2 ferramentas: ['buscar_base_conhecimento', 'agendamento_tool']
INFO: Histórico carregado: 5 mensagens
INFO: Invocando agente...
INFO: Resposta do agente (primeiros 200 chars): Olá! Tudo bem? 😊...
INFO: Histórico salvo com sucesso
INFO: Processamento concluído em 3.45s
INFO: ============================================================
```

---

## 🧪 Testes

### Teste Automático

```bash
python src/nodes/agent.py
```

**Executa:**
1. Cria estado de teste
2. Adiciona mensagem: "Olá, quanto custa instalar drywall?"
3. Processa com agente
4. Verifica se resposta foi gerada
5. Exibe resultado

### Teste Manual

```python
import asyncio
from src.nodes.agent import processar_agente
from src.models.state import criar_estado_inicial

async def teste():
    state = criar_estado_inicial()
    state["cliente_numero"] = "5511999999999"
    state["cliente_nome"] = "Teste"
    state["fila_mensagens"] = [
        {"conteudo": "Quanto custa drywall?", "tipo": "conversation"}
    ]

    resultado = await processar_agente(state)
    print(resultado["resposta_agente"])

asyncio.run(teste())
```

---

## 📈 Performance

### Métricas Típicas

- **Tempo médio**: 2-5 segundos
- **Timeout**: 120 segundos
- **Taxa de sucesso**: >99%
- **Chamadas de ferramentas**: 1-3 por mensagem

### Otimizações

1. **Cache de embeddings** (futuro)
2. **Histórico limitado** (últimas 10 mensagens)
3. **Timeout configurável**
4. **Retry automático** (max 3)

---

## 🔧 Manutenção

### Atualizar System Prompt

Edite a função `_get_system_prompt()` em `src/nodes/agent.py`:

```python
def _get_system_prompt() -> str:
    return """
    <quem_voce_eh>
    # Altere aqui a personalidade
    </quem_voce_eh>
    """
```

### Adicionar Nova Ferramenta

```python
# Em _create_agent()
tools = [
    retriever_tool,
    agendamento_tool,
    nova_ferramenta_tool  # Adicione aqui
]
```

### Ajustar Temperatura

```env
# .env
AGENT_TEMPERATURE=0.7  # Mais conservador
# ou
AGENT_TEMPERATURE=1.0  # Mais criativo
```

---

## 📚 Referências

- [LangGraph Docs](https://python.langchain.com/docs/langgraph)
- [ReAct Agent](https://python.langchain.com/docs/modules/agents/agent_types/react)
- [OpenAI GPT-4](https://platform.openai.com/docs/models/gpt-4)
- [RAG Tutorial](https://python.langchain.com/docs/use_cases/question_answering/)

---

**Status**: ✅ Implementado e funcional
**Última atualização**: 2025-10-21
