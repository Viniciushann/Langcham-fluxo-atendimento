# 📂 Estrutura do Projeto - WhatsApp Bot LangGraph

## 🌳 Árvore de Diretórios

```
whatsapp_bot/
│
├── 📄 .env.example              # Template de variáveis de ambiente
├── 📄 .gitignore                # Arquivos ignorados pelo Git
├── 📄 requirements.txt          # Dependências Python
├── 📄 pyproject.toml            # Configuração do projeto (PEP 518)
├── 📄 README.md                 # Documentação principal
├── 📄 INSTALL.md                # Guia de instalação
├── 📄 STRUCTURE.md              # Este arquivo
│
├── 📁 src/                      # Código fonte principal
│   ├── 📄 __init__.py
│   ├── 📄 main.py               # [A CRIAR] Aplicação FastAPI
│   │
│   ├── 📁 config/               # ✅ Configurações
│   │   ├── 📄 __init__.py
│   │   └── 📄 settings.py       # ✅ Pydantic Settings (COMPLETO)
│   │
│   ├── 📁 models/               # [Fase 1] Modelos e tipos
│   │   ├── 📄 __init__.py
│   │   └── 📄 state.py          # [A CRIAR] AgentState TypedDict
│   │
│   ├── 📁 clients/              # [Fase 2] Clientes externos
│   │   ├── 📄 __init__.py
│   │   ├── 📄 supabase_client.py    # [A CRIAR] Cliente Supabase
│   │   ├── 📄 redis_client.py       # [A CRIAR] Gerenciador de fila
│   │   └── 📄 whatsapp_client.py    # [A CRIAR] Cliente Evolution API
│   │
│   ├── 📁 nodes/                # [Fases 3-5, 8] Nós do grafo
│   │   ├── 📄 __init__.py
│   │   ├── 📄 webhook.py        # [A CRIAR] Recepção e validação
│   │   ├── 📄 media.py          # [A CRIAR] Processamento de mídia
│   │   ├── 📄 queue.py          # [A CRIAR] Gerenciamento de fila
│   │   ├── 📄 agent.py          # [A CRIAR] Agente principal com RAG
│   │   └── 📄 response.py       # [A CRIAR] Formatação e envio
│   │
│   ├── 📁 tools/                # [Fase 6] Ferramentas do agente
│   │   ├── 📄 __init__.py
│   │   └── 📄 scheduling.py     # [A CRIAR] Agendamento Google Calendar
│   │
│   └── 📁 graph/                # [Fase 9] Construção do grafo
│       ├── 📄 __init__.py
│       └── 📄 workflow.py       # [A CRIAR] Definição do StateGraph
│
└── 📁 tests/                    # [Fase 11] Testes
    ├── 📄 __init__.py
    ├── 📄 conftest.py           # [A CRIAR] Fixtures compartilhadas
    ├── 📄 test_nodes.py         # [A CRIAR] Testes dos nós
    ├── 📄 test_webhook.py       # [A CRIAR] Testes de webhook
    ├── 📄 test_media.py         # [A CRIAR] Testes de mídia
    ├── 📄 test_queue.py         # [A CRIAR] Testes de fila
    ├── 📄 test_agent.py         # [A CRIAR] Testes do agente
    ├── 📄 test_integracao.py    # [A CRIAR] Testes de integração
    └── 📄 test_api.py           # [A CRIAR] Testes da API
```

## 📊 Status de Implementação

### ✅ Fase 0: Preparação (COMPLETO)
- ✅ Estrutura de pastas criada
- ✅ `requirements.txt` completo
- ✅ `.env.example` documentado
- ✅ `.gitignore` configurado
- ✅ `pyproject.toml` criado
- ✅ `src/config/settings.py` implementado com Pydantic Settings
- ✅ Todos os `__init__.py` criados
- ✅ `README.md` e `INSTALL.md` criados

### 📝 Próximas Fases

#### Fase 1: Modelos e Tipos
- [ ] `src/models/state.py` - AgentState TypedDict
- [ ] Enums: TipoMensagem, AcaoFluxo, IntencaoAgendamento

#### Fase 2: Clientes Externos
- [ ] `src/clients/supabase_client.py` - SupabaseClient
- [ ] `src/clients/redis_client.py` - RedisQueue
- [ ] `src/clients/whatsapp_client.py` - WhatsAppClient

#### Fase 3: Webhook e Cadastro
- [ ] `src/nodes/webhook.py` - validar_webhook, verificar_cliente, cadastrar_cliente

#### Fase 4: Processamento de Mídia
- [ ] `src/nodes/media.py` - processar_audio, processar_imagem, processar_texto

#### Fase 5: Gerenciamento de Fila
- [ ] `src/nodes/queue.py` - gerenciar_fila, aguardar_mensagens

#### Fase 6: Ferramentas de Agendamento
- [ ] `src/tools/scheduling.py` - agendamento_tool, Google Calendar

#### Fase 7: Agente de IA
- [ ] `src/nodes/agent.py` - processar_agente com RAG

#### Fase 8: Formatação e Envio
- [ ] `src/nodes/response.py` - fragmentar_resposta, enviar_respostas

#### Fase 9: Construção do Grafo
- [ ] `src/graph/workflow.py` - criar_grafo_atendimento

#### Fase 10: API Principal
- [ ] `src/main.py` - FastAPI, endpoints, background tasks

#### Fase 11: Testes
- [ ] Testes unitários para todos os módulos
- [ ] Testes de integração
- [ ] Coverage > 70%

#### Fase 12: Deploy
- [ ] Dockerfile
- [ ] docker-compose.yml
- [ ] Scripts de deploy

## 📦 Módulos Principais

### 1. `src/config/` - Configurações
**Status**: ✅ COMPLETO

Gerencia todas as variáveis de ambiente e configurações da aplicação.

**Arquivos**:
- `settings.py` - Classe Settings com Pydantic
- Validação automática de variáveis
- Singleton pattern para acesso global

**Uso**:
```python
from src.config import get_settings

settings = get_settings()
print(settings.openai_api_key)
```

### 2. `src/models/` - Modelos e Tipos
**Status**: ⏳ PENDENTE (Fase 1)

Define o estado compartilhado do agente e tipos auxiliares.

**Arquivos a criar**:
- `state.py` - AgentState (TypedDict)
- Enums para tipos de mensagens e ações

### 3. `src/clients/` - Clientes Externos
**Status**: ⏳ PENDENTE (Fase 2)

Integrações com serviços externos.

**Arquivos a criar**:
- `supabase_client.py` - Buscar/cadastrar clientes, RAG
- `redis_client.py` - Gerenciamento de fila
- `whatsapp_client.py` - Evolution API

### 4. `src/nodes/` - Nós do Grafo
**Status**: ⏳ PENDENTE (Fases 3-5, 8)

Implementação dos nós do LangGraph.

**Arquivos a criar**:
- `webhook.py` - Recepção e validação
- `media.py` - Processamento de áudio/imagem
- `queue.py` - Fila Redis
- `agent.py` - Agente LLM com RAG
- `response.py` - Envio de respostas

### 5. `src/tools/` - Ferramentas
**Status**: ⏳ PENDENTE (Fase 6)

Tools para o agente LangChain.

**Arquivos a criar**:
- `scheduling.py` - Google Calendar API

### 6. `src/graph/` - Grafo LangGraph
**Status**: ⏳ PENDENTE (Fase 9)

Construção e compilação do StateGraph.

**Arquivos a criar**:
- `workflow.py` - Definição completa do grafo

### 7. `tests/` - Testes
**Status**: ⏳ PENDENTE (Fase 11)

Testes unitários e de integração.

**Arquivos a criar**:
- Testes para cada módulo
- Fixtures compartilhadas
- Testes de integração

## 🔗 Fluxo de Dependências

```
main.py
  ↓
workflow.py (grafo)
  ↓
nodes/ (webhook, media, queue, agent, response)
  ↓
clients/ (supabase, redis, whatsapp)
  ↓
models/ (state, enums)
  ↓
config/ (settings)
```

## 📝 Convenções de Código

### Nomenclatura
- **Arquivos**: `snake_case.py`
- **Classes**: `PascalCase`
- **Funções**: `snake_case()`
- **Constantes**: `UPPER_CASE`
- **Variáveis privadas**: `_prefixo`

### Docstrings
Usar Google Style:

```python
def funcao_exemplo(param: str) -> dict:
    """
    Breve descrição da função.

    Args:
        param: Descrição do parâmetro

    Returns:
        dict: Descrição do retorno

    Raises:
        ValueError: Quando ocorre erro
    """
    pass
```

### Type Hints
Sempre usar type hints completos:

```python
from typing import Optional, List, Dict

def processar(dados: Dict[str, str]) -> Optional[List[str]]:
    ...
```

### Imports
Organizar em grupos:

```python
# Standard library
import os
import sys

# Third-party
from fastapi import FastAPI
from langchain import LLM

# Local
from src.config import get_settings
from src.models import AgentState
```

## 🎯 Próximo Passo

Execute a **Fase 1** para criar os modelos e tipos:

```bash
# Consulte o arquivo AGENTE LANGGRAPH.txt
# Procure pela seção "Fase 1: Modelo de Estado e Tipos"
# Implemente src/models/state.py
```

---

**Estrutura criada com sucesso! 🎉**

Consulte `README.md` para o overview completo e `INSTALL.md` para instruções de instalação.
