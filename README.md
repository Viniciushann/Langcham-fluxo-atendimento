# 🤖 WhatsApp Bot com LangGraph - Guia de Implementação

Sistema inteligente de atendimento automatizado via WhatsApp com agendamento, processamento de múltiplas mídias (áudio, imagem, texto) e RAG (Retrieval-Augmented Generation).

---

## 📋 Índice

- [Visão Geral](#-visão-geral)
- [Funcionalidades](#-funcionalidades)
- [Arquitetura](#-arquitetura)
- [Pré-requisitos](#-pré-requisitos)
- [Roadmap de Implementação](#-roadmap-de-implementação)
- [Estrutura do Projeto](#-estrutura-do-projeto)
- [Tecnologias Utilizadas](#-tecnologias-utilizadas)
- [Como Começar](#-como-começar)
- [Fluxo de Trabalho](#-fluxo-de-trabalho)
- [Estimativa de Tempo](#-estimativa-de-tempo)

---

## 🎯 Visão Geral

Este projeto implementa um bot de WhatsApp completo usando **LangGraph** para orquestração de fluxos, com capacidades avançadas de:

- ✅ Atendimento conversacional inteligente com memória persistente
- ✅ Processamento de áudio usando OpenAI Whisper
- ✅ Análise de imagens com GPT-4 Vision
- ✅ Sistema de agendamento integrado ao Google Calendar
- ✅ RAG para consultas à base de conhecimento da empresa
- ✅ Controle de concorrência com fila Redis
- ✅ Respostas fragmentadas naturais para melhor experiência

---

## 🚀 Funcionalidades

### 1. **Processamento Multi-Mídia**
- **Texto**: Processamento direto de mensagens de texto
- **Áudio**: Transcrição automática com Whisper
- **Imagem**: Análise e descrição com GPT-4 Vision

### 2. **Sistema de Agendamento**
- Consultar horários disponíveis
- Agendar consultas/reuniões
- Cancelar agendamentos
- Reagendar eventos
- Integração com Google Calendar

### 3. **RAG (Retrieval-Augmented Generation)**
- Base de conhecimento vetorizada no Supabase
- Respostas precisas sobre serviços da empresa
- Informações atualizadas automaticamente

### 4. **Gestão de Conversas**
- Memória persistente no PostgreSQL
- Contexto de conversas anteriores
- Histórico completo de interações

### 5. **Controle de Concorrência**
- Fila de mensagens no Redis
- Agrupamento inteligente de mensagens (13s)
- Processamento sequencial por cliente

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────┐
│                    WEBHOOK (Evolution API)                   │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ FASE 1: RECEPÇÃO E VALIDAÇÃO                                │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────┐ │
│  │  Validar    │───▶│  Verificar   │───▶│   Cadastrar    │ │
│  │  Webhook    │    │   Cliente    │    │    Cliente     │ │
│  └─────────────┘    └──────────────┘    └────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ FASE 2: PROCESSAMENTO DE MÍDIA                              │
│  ┌─────────────┐    ┌──────────────┐    ┌────────────────┐ │
│  │  Processar  │    │  Processar   │    │   Processar    │ │
│  │    Áudio    │    │    Imagem    │    │     Texto      │ │
│  │  (Whisper)  │    │  (GPT-4V)    │    │   (Direto)     │ │
│  └─────────────┘    └──────────────┘    └────────────────┘ │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ FASE 3: FILA E AGRUPAMENTO                                  │
│  ┌─────────────┐    ┌──────────────┐                       │
│  │  Gerenciar  │───▶│   Aguardar   │                       │
│  │    Fila     │    │  Mensagens   │                       │
│  │   (Redis)   │    │    (13s)     │                       │
│  └─────────────┘    └──────────────┘                       │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ FASE 4: AGENTE INTELIGENTE                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │           AGENTE LangGraph (GPT-4o)                  │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────────┐ │  │
│  │  │    RAG     │  │ Agendamento│  │    Memória     │ │  │
│  │  │ (Supabase) │  │  (Google)  │  │ (PostgreSQL)   │ │  │
│  │  └────────────┘  └────────────┘  └────────────────┘ │  │
│  └──────────────────────────────────────────────────────┘  │
└──────────────────────────┬──────────────────────────────────┘
                           │
                           ▼
┌─────────────────────────────────────────────────────────────┐
│ FASE 5: ENVIO DE RESPOSTA                                   │
│  ┌─────────────┐    ┌──────────────┐                       │
│  │ Fragmentar  │───▶│    Enviar    │                       │
│  │  Resposta   │    │   Respostas  │                       │
│  │ (Inteligente│    │ (WhatsApp)   │                       │
│  └─────────────┘    └──────────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

---

## 📦 Pré-requisitos

### Software Necessário:
- **Python 3.11+** instalado
- **Docker** e **Docker Compose** (opcional, mas recomendado)
- **Git** para controle de versão

### Contas e APIs:
1. **OpenAI API Key** - Para GPT-4, Whisper e embeddings
2. **Supabase** - Banco de dados PostgreSQL + Vector Store
3. **Redis** - Para fila de mensagens (pode usar local ou Docker)
4. **Evolution API** - API WhatsApp Business
5. **Google Cloud Console** - Para Google Calendar API

### Conhecimentos Recomendados:
- Python básico/intermediário
- Conceitos de APIs REST
- Async/await em Python
- Noções básicas de Docker (opcional)

---

## 🗺️ Roadmap de Implementação

O projeto está dividido em **12 fases** sequenciais. Cada fase depende da anterior.

### **Fase 0: Preparação do Ambiente** ⏱️ ~30min
- Criar estrutura de pastas
- Configurar `requirements.txt`
- Implementar `settings.py` com Pydantic
- Criar `.env.example`
- **Resultado**: Projeto estruturado e pronto para desenvolvimento

### **Fase 1: Modelo de Estado e Tipos** ⏱️ ~45min
- Definir `AgentState` (TypedDict)
- Criar enums (TipoMensagem, AcaoFluxo, etc)
- Adicionar type hints completos
- **Resultado**: Tipos e estado compartilhado definidos

### **Fase 2: Clientes Externos** ⏱️ ~2h
- Implementar `SupabaseClient` (buscar/cadastrar clientes)
- Implementar `RedisQueue` (gerenciamento de fila)
- Implementar `WhatsAppClient` (Evolution API)
- **Resultado**: Clientes externos funcionando

### **Fase 3: Webhook e Cadastro** ⏱️ ~1.5h
- Criar `validar_webhook`
- Criar `verificar_cliente`
- Criar `cadastrar_cliente`
- **Resultado**: Recepção e validação de mensagens

### **Fase 4: Processamento de Mídia** ⏱️ ~2h
- Implementar `processar_audio` (Whisper)
- Implementar `processar_imagem` (GPT-4 Vision)
- Implementar `processar_texto`
- Criar `rotear_tipo_mensagem`
- **Resultado**: Todas as mídias sendo processadas

### **Fase 5: Gerenciamento de Fila** ⏱️ ~1h
- Criar `gerenciar_fila` (controle de concorrência)
- Criar `aguardar_mensagens` (agrupamento)
- **Resultado**: Fila Redis funcionando

### **Fase 6: Ferramentas de Agendamento** ⏱️ ~2.5h
- Implementar `agendamento_tool`
- Criar `consultar_horarios`
- Criar `agendar_horario`
- Criar `cancelar_horario`
- **Resultado**: Integração com Google Calendar

### **Fase 7: Agente de IA com RAG** ⏱️ ~2h
- Configurar LLM (GPT-4o)
- Implementar memória PostgreSQL
- Configurar RAG com Supabase
- Criar system prompt completo
- **Resultado**: Agente inteligente funcionando

### **Fase 8: Formatação e Envio** ⏱️ ~1h
- Implementar `fragmentar_resposta`
- Implementar `enviar_respostas`
- Adicionar status "digitando"
- **Resultado**: Respostas naturais sendo enviadas

### **Fase 9: Construção do Grafo** ⏱️ ~1.5h
- Montar grafo completo no LangGraph
- Conectar todos os nós
- Definir conditional edges
- **Resultado**: Grafo compilado e funcionando

### **Fase 10: API Principal** ⏱️ ~1.5h
- Criar aplicação FastAPI
- Implementar endpoint `/webhook/whatsapp`
- Adicionar background tasks
- Criar health check
- **Resultado**: API recebendo webhooks

### **Fase 11: Testes** ⏱️ ~2h
- Criar testes unitários
- Criar testes de integração
- Testar API
- **Resultado**: Coverage > 70%

### **Fase 12: Deploy e Documentação** ⏱️ ~1.5h
- Criar Dockerfile
- Configurar docker-compose
- Documentar API
- Criar scripts de deploy
- **Resultado**: Projeto pronto para produção

---

## 📁 Estrutura do Projeto

```
whatsapp_bot/
├── .env.example                 # Template de variáveis de ambiente
├── .gitignore                   # Arquivos ignorados pelo Git
├── requirements.txt             # Dependências Python
├── README.md                    # Este arquivo
├── Dockerfile                   # Imagem Docker
├── docker-compose.yml           # Orquestração de containers
│
├── src/                         # Código fonte
│   ├── __init__.py
│   │
│   ├── config/                  # Configurações
│   │   ├── __init__.py
│   │   └── settings.py          # Carregamento de env vars
│   │
│   ├── models/                  # Modelos e tipos
│   │   ├── __init__.py
│   │   └── state.py             # AgentState e enums
│   │
│   ├── clients/                 # Clientes externos
│   │   ├── __init__.py
│   │   ├── supabase_client.py   # Cliente Supabase
│   │   ├── redis_client.py      # Gerenciador de fila
│   │   └── whatsapp_client.py   # Cliente Evolution API
│   │
│   ├── nodes/                   # Nós do grafo LangGraph
│   │   ├── __init__.py
│   │   ├── webhook.py           # Recepção e validação
│   │   ├── media.py             # Processamento de mídia
│   │   ├── queue.py             # Gerenciamento de fila
│   │   ├── agent.py             # Agente principal
│   │   └── response.py          # Formatação e envio
│   │
│   ├── tools/                   # Ferramentas do agente
│   │   ├── __init__.py
│   │   └── scheduling.py        # Agendamento Google Calendar
│   │
│   ├── graph/                   # Definição do grafo
│   │   ├── __init__.py
│   │   └── workflow.py          # Construção do StateGraph
│   │
│   └── main.py                  # Aplicação FastAPI
│
├── tests/                       # Testes
│   ├── __init__.py
│   ├── conftest.py              # Fixtures compartilhadas
│   ├── test_webhook.py          # Testes de webhook
│   ├── test_media.py            # Testes de mídia
│   ├── test_queue.py            # Testes de fila
│   ├── test_agent.py            # Testes do agente
│   ├── test_integracao.py       # Testes de integração
│   └── test_api.py              # Testes da API
│
└── scripts/                     # Scripts utilitários
    ├── deploy.sh                # Script de deploy
    └── backup.sh                # Script de backup
```

---

## 🛠️ Tecnologias Utilizadas

### Core
- **LangGraph** (>=0.2.0) - Orquestração de fluxos do agente
- **LangChain** (>=0.3.0) - Framework para LLM
- **FastAPI** - API web assíncrona
- **Python 3.11+** - Linguagem base

### Integrações
- **OpenAI API** - GPT-4o, Whisper, Embeddings
- **Supabase** - PostgreSQL + Vector Store
- **Redis** - Fila de mensagens
- **Evolution API** - WhatsApp Business
- **Google Calendar API** - Agendamento

### Bibliotecas
- **langchain-openai** - Integração OpenAI
- **langchain-community** - Ferramentas da comunidade
- **supabase-py** - Cliente Python Supabase
- **redis** - Cliente Redis
- **httpx** - Cliente HTTP async
- **pydantic** - Validação de dados
- **pytest** - Framework de testes

---

## 🚀 Como Começar

### Opção 1: Instalação Local

```bash
# 1. Clone ou crie o diretório do projeto
cd "C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Langcham. fluxo atendimento"

# 2. Crie ambiente virtual Python
python -m venv venv
venv\Scripts\activate  # Windows
# ou
source venv/bin/activate  # Linux/Mac

# 3. Instale dependências (após criar requirements.txt)
pip install -r requirements.txt

# 4. Configure variáveis de ambiente
# Copie .env.example para .env e preencha as credenciais

# 5. Execute a aplicação
python src/main.py
```

### Opção 2: Docker (Recomendado para Produção)

```bash
# 1. Configure .env com suas credenciais

# 2. Build e execute
docker-compose up -d

# 3. Verifique logs
docker-compose logs -f bot

# 4. Health check
curl http://localhost:8000/health
```

---

## 🔄 Fluxo de Trabalho Completo

### 1. **Cliente envia mensagem no WhatsApp**
   - Texto: "Quero agendar uma consulta"
   - Áudio: Mensagem de voz
   - Imagem: Foto de um problema

### 2. **Evolution API captura e envia webhook**
   ```json
   POST /webhook/whatsapp
   {
     "event": "messages.upsert",
     "data": { ... }
   }
   ```

### 3. **Bot processa no grafo LangGraph**
   - ✅ Valida webhook
   - ✅ Verifica/cadastra cliente
   - ✅ Processa mídia (transcreve/analisa)
   - ✅ Adiciona à fila Redis
   - ✅ Aguarda agrupamento (13s)
   - ✅ Processa com agente IA
   - ✅ Fragmenta resposta
   - ✅ Envia resposta ao cliente

### 4. **Cliente recebe resposta**
   - Mensagens fragmentadas naturais
   - Status "digitando" entre mensagens
   - Resposta contextualizada e precisa

---

## ⏱️ Estimativa de Tempo

### Desenvolvimento Completo
- **Total**: 15-20 horas
- **Por fase**: 30min - 2.5h cada

### Divisão Sugerida (4 dias)
- **Dia 1**: Fases 0-3 (Setup + Webhook + Cadastro) - ~5h
- **Dia 2**: Fases 4-6 (Mídia + Fila + Ferramentas) - ~5.5h
- **Dia 3**: Fases 7-9 (Agente + Resposta + Grafo) - ~5h
- **Dia 4**: Fases 10-12 (API + Testes + Deploy) - ~5h

### Desenvolvimento Intensivo
- **1-2 dias**: Implementação completa
- **+ 1 dia**: Testes e ajustes
- **+ meio dia**: Deploy e documentação

---

## 📝 Variáveis de Ambiente (.env)

```env
# OpenAI
OPENAI_API_KEY=sk-...

# Supabase
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJ...

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_PASSWORD=  # opcional

# WhatsApp (Evolution API)
WHATSAPP_API_URL=https://sua-evolution-api.com
WHATSAPP_API_KEY=sua-chave
WHATSAPP_INSTANCE=sua-instancia

# PostgreSQL (Memória de conversas)
POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost:5432/whatsapp_bot

# Google Calendar
GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json
```

---

## ✅ Checklist de Implementação

### Antes de Começar
- [ ] Python 3.11+ instalado
- [ ] Credenciais OpenAI obtidas
- [ ] Conta Supabase criada
- [ ] Redis instalado/configurado
- [ ] Evolution API configurada
- [ ] Google Calendar API ativada

### Durante Implementação
- [ ] Seguir fases na ordem (0 → 12)
- [ ] Testar cada fase antes de avançar
- [ ] Commit após cada fase concluída
- [ ] Documentar problemas encontrados

### Após Implementação
- [ ] Todos os testes passando
- [ ] Coverage > 70%
- [ ] Documentação completa
- [ ] Deploy funcional
- [ ] Webhook configurado
- [ ] Monitoramento ativo

---

## 🎯 Próximos Passos

### 1. **Execute a Fase 0**
   - Crie a estrutura de pastas
   - Configure o `requirements.txt`
   - Implemente o `settings.py`

### 2. **Configure as Credenciais**
   - Obtenha todas as API Keys necessárias
   - Preencha o arquivo `.env`

### 3. **Siga o Roadmap**
   - Execute cada fase sequencialmente
   - Valide antes de avançar
   - Documente suas decisões

### 4. **Teste Localmente**
   - Use o endpoint `/test/message`
   - Simule diferentes cenários
   - Verifique logs

### 5. **Deploy em Produção**
   - Use Docker para facilitar
   - Configure monitoramento
   - Faça backup regular

---

## 📚 Recursos Úteis

### Documentação Oficial
- [LangGraph Docs](https://langchain-ai.github.io/langgraph/)
- [LangChain Docs](https://python.langchain.com/)
- [FastAPI Docs](https://fastapi.tiangolo.com/)
- [Evolution API Docs](https://doc.evolution-api.com/)
- [Supabase Docs](https://supabase.com/docs)

### Arquivo de Referência
- `AGENTE LANGGRAPH.txt` - Plano completo de implementação com prompts detalhados para cada fase

---

## 🤝 Suporte e Contribuições

### Problemas Comuns
- **Erro de importação**: Verifique PYTHONPATH
- **Redis não conecta**: Verifique REDIS_HOST e porta
- **Timeout Supabase**: Verifique firewall/VPN
- **OpenAI rate limit**: Implemente retry logic

### Como Contribuir
1. Fork o projeto
2. Crie uma branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -am 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request

---

## 📄 Licença

MIT License - Sinta-se livre para usar e modificar este projeto.

---

## 👨‍💻 Autor

**Vinicius Soutenio**

---

**Bom desenvolvimento! 🚀**

Para começar, consulte o arquivo `AGENTE LANGGRAPH.txt` e execute a **Fase 0** para criar a estrutura base do projeto.
