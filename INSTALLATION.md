# 🚀 Guia de Instalação - WhatsApp Bot LangGraph

Este guia fornece instruções passo a passo para configurar o projeto do zero.

---

## ✅ Pré-requisitos

- **Python 3.11+** instalado
- **Git** instalado
- Contas criadas:
  - [OpenAI](https://platform.openai.com/) - Para GPT-4 e Whisper
  - [Supabase](https://supabase.com/) - Banco de dados e vetorização
  - [Evolution API](https://evolution-api.com/) - API do WhatsApp
  - [Google Cloud Console](https://console.cloud.google.com/) - Para Google Calendar

---

## 📦 Passo 1: Clonar e Instalar Dependências

### 1.1 Clone o repositório (ou navegue até a pasta do projeto)

```bash
cd "C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Langcham. fluxo atendimento"
```

### 1.2 Crie um ambiente virtual

```bash
python -m venv venv
```

### 1.3 Ative o ambiente virtual

**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### 1.4 Instale as dependências

```bash
pip install -r requirements.txt
```

---

## ⚙️ Passo 2: Configurar Variáveis de Ambiente

### 2.1 Copie o arquivo de exemplo

```bash
cp .env.example .env
```

### 2.2 Preencha as variáveis no arquivo `.env`

Abra o arquivo `.env` e configure:

#### **OpenAI**
```env
OPENAI_API_KEY=sk-proj-your-key-here
```
- Obtenha em: https://platform.openai.com/api-keys

#### **Supabase**
```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
```
- Obtenha em: Supabase Dashboard > Project Settings > API

#### **Redis**
```env
REDIS_HOST=localhost
REDIS_PORT=6379
```
- Se usar local: instale com `docker run -d -p 6379:6379 redis`
- Se usar Redis Cloud: configure host/password

#### **WhatsApp (Evolution API)**
```env
WHATSAPP_API_URL=https://sua-evolution-api.com
WHATSAPP_API_KEY=sua-api-key
WHATSAPP_INSTANCE=sua-instancia
```
- Configure sua instância Evolution API
- Anote a URL, API Key e nome da instância

#### **PostgreSQL**
```env
POSTGRES_CONNECTION_STRING=postgresql://user:password@localhost:5432/whatsapp_bot
```
- Pode usar o Postgres do Supabase ou local

#### **Google Calendar**
```env
GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json
GOOGLE_CALENDAR_TOKEN_FILE=token.json
```
- Siga o guia `GOOGLE_CALENDAR_SETUP.md` para configurar

---

## 🗄️ Passo 3: Configurar Banco de Dados

### 3.1 Supabase - Criar Tabelas

Acesse o Supabase SQL Editor e execute:

```sql
-- Tabela de clientes
CREATE TABLE IF NOT EXISTS clientes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    numero VARCHAR(20) UNIQUE NOT NULL,
    nome VARCHAR(255),
    email VARCHAR(255),
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- Tabela de conversas
CREATE TABLE IF NOT EXISTS conversas (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    cliente_id UUID REFERENCES clientes(id),
    mensagem TEXT NOT NULL,
    role VARCHAR(20) NOT NULL, -- 'user' ou 'assistant'
    timestamp TIMESTAMP DEFAULT NOW(),
    metadata JSONB
);

-- Tabela para RAG (base de conhecimento)
CREATE TABLE IF NOT EXISTS conhecimento (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conteudo TEXT NOT NULL,
    embedding vector(1536), -- Para embeddings OpenAI
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Índice para busca vetorial
CREATE INDEX IF NOT EXISTS conhecimento_embedding_idx
ON conhecimento USING ivfflat (embedding vector_cosine_ops);
```

### 3.2 Habilitar Extensões

```sql
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
```

---

## 📅 Passo 4: Configurar Google Calendar

Siga o guia detalhado em `GOOGLE_CALENDAR_SETUP.md`:

1. Criar projeto no Google Cloud Console
2. Ativar Google Calendar API
3. Criar credenciais OAuth 2.0 (tipo Desktop)
4. Baixar `credentials.json` e colocar na raiz do projeto
5. Executar primeira autenticação

---

## 🔧 Passo 5: Configurar Redis (Local)

### Opção A: Docker (Recomendado)

```bash
docker run -d -p 6379:6379 --name redis redis:latest
```

### Opção B: Instalação Local

**Windows:**
- Baixe: https://github.com/microsoftarchive/redis/releases
- Ou use WSL: `sudo apt-get install redis-server`

**Linux:**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**Mac:**
```bash
brew install redis
brew services start redis
```

### Testar conexão:
```bash
redis-cli ping
# Resposta esperada: PONG
```

---

## 🧪 Passo 6: Testar Configuração

### 6.1 Testar Google Calendar

```bash
python test_google_calendar.py
```

### 6.2 Testar Conexões

Crie um arquivo `test_setup.py`:

```python
import asyncio
from src.config.settings import get_settings

async def test_connections():
    settings = get_settings()

    print("✅ Settings carregadas com sucesso!")
    print(f"📊 OpenAI: {settings.openai_api_key[:10]}...")
    print(f"📊 Supabase: {settings.supabase_url}")
    print(f"📊 Redis: {settings.redis_host}:{settings.redis_port}")
    print(f"📊 WhatsApp: {settings.whatsapp_instance}")

if __name__ == "__main__":
    asyncio.run(test_connections())
```

Execute:
```bash
python test_setup.py
```

---

## 🚀 Passo 7: Executar o Bot

### 7.1 Modo Desenvolvimento

```bash
python src/main.py
```

### 7.2 Modo Produção (com Uvicorn)

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🔍 Verificação de Saúde

Após iniciar, acesse:

- **Health Check**: http://localhost:8000/health
- **Webhook**: http://localhost:8000/webhook (POST)

---

## 📝 Estrutura de Pastas Criada

```
whatsapp_bot/
├── .env                      # Configurações (NÃO commitar!)
├── .env.example              # Exemplo de configurações
├── .gitignore                # Arquivos ignorados
├── requirements.txt          # Dependências Python
├── pyproject.toml            # Configurações do projeto
├── README.md                 # Documentação principal
├── INSTALLATION.md           # Este arquivo
├── GOOGLE_CALENDAR_SETUP.md  # Setup do Google Calendar
│
├── credentials.json          # Google OAuth (NÃO commitar!)
├── token.json                # Google Token (NÃO commitar!)
│
├── src/
│   ├── __init__.py
│   ├── config/
│   │   ├── __init__.py
│   │   └── settings.py       # Configurações Pydantic
│   ├── models/
│   │   ├── __init__.py
│   │   └── state.py          # AgentState TypedDict
│   ├── clients/
│   │   ├── __init__.py
│   │   ├── supabase_client.py
│   │   ├── redis_client.py
│   │   └── whatsapp_client.py
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── webhook.py
│   │   ├── media.py
│   │   ├── queue.py
│   │   ├── agent.py
│   │   └── response.py
│   ├── tools/
│   │   ├── __init__.py
│   │   └── scheduling.py
│   ├── graph/
│   │   ├── __init__.py
│   │   └── workflow.py
│   └── main.py
│
└── tests/
    ├── __init__.py
    └── test_nodes.py
```

---

## 🐛 Troubleshooting

### Erro: "No module named 'src'"

```bash
# Adicione o diretório ao PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Ou execute como módulo
python -m src.main
```

### Erro: "Redis connection refused"

```bash
# Verifique se Redis está rodando
redis-cli ping

# Se não, inicie:
docker start redis
# ou
sudo systemctl start redis
```

### Erro: "Supabase authentication failed"

- Verifique se SUPABASE_URL e SUPABASE_KEY estão corretos
- Teste no Supabase Dashboard > API > Test

### Erro: "Google Calendar authentication"

- Delete `token.json` e refaça autenticação
- Verifique se `credentials.json` é do tipo "Desktop app"

---

## 📚 Próximos Passos

1. ✅ Configurar webhook da Evolution API para apontar para seu servidor
2. ✅ Implementar os nós do LangGraph (seguir README.md)
3. ✅ Testar fluxo completo de mensagens
4. ✅ Popular base de conhecimento RAG
5. ✅ Deploy em produção

---

## 🆘 Suporte

- Documentação completa: `README.md`
- Configuração Google Calendar: `GOOGLE_CALENDAR_SETUP.md`
- Issues: Crie uma issue no repositório

---

## 📋 Checklist de Instalação

- [ ] Python 3.11+ instalado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Arquivo `.env` criado e preenchido
- [ ] Supabase configurado (tabelas criadas)
- [ ] Redis rodando
- [ ] Google Calendar configurado (`credentials.json`)
- [ ] Teste de conexões passou
- [ ] Bot iniciado com sucesso
- [ ] Health check respondendo

✅ **Se todos os itens estão marcados, você está pronto para começar!**
