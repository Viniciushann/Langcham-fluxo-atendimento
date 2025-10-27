# 📦 Guia de Instalação - WhatsApp Bot LangGraph

## ✅ Pré-requisitos

Antes de começar, certifique-se de ter instalado:

- **Python 3.11 ou superior** ([Download](https://www.python.org/downloads/))
- **Git** ([Download](https://git-scm.com/downloads))
- **Redis** (opcional - pode usar Docker)
- **PostgreSQL** (ou usar Supabase)

## 🚀 Instalação Passo a Passo

### 1. Clone/Navegue até o Projeto

```bash
cd "C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Langcham. fluxo atendimento"
```

### 2. Crie o Ambiente Virtual Python

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Instale as Dependências

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. Configure as Variáveis de Ambiente

#### 4.1. Copie o arquivo de exemplo

```bash
cp .env.example .env
```

No Windows:
```bash
copy .env.example .env
```

#### 4.2. Edite o arquivo `.env` com suas credenciais

Abra o arquivo `.env` e preencha com suas credenciais reais:

```env
# OPENAI
OPENAI_API_KEY=sk-proj-SUAS_CREDENCIAIS_AQUI

# SUPABASE
SUPABASE_URL=https://seuprojetoid.supabase.co
SUPABASE_KEY=sua_chave_supabase_aqui

# REDIS
REDIS_HOST=localhost
REDIS_PORT=6379

# WHATSAPP
WHATSAPP_API_URL=https://sua-evolution-api.com
WHATSAPP_API_KEY=sua_chave_api
WHATSAPP_INSTANCE=sua_instancia

# POSTGRES
POSTGRES_CONNECTION_STRING=postgresql://usuario:senha@host:5432/database
```

### 5. Verifique a Instalação

Teste se as configurações estão corretas:

```bash
python -c "from src.config import get_settings; settings = get_settings(); print('✅ Configurações carregadas com sucesso!')"
```

Se aparecer algum erro, verifique se:
- O arquivo `.env` está preenchido corretamente
- Todas as variáveis obrigatórias estão definidas
- As credenciais estão válidas

## 🐳 Instalação com Docker (Alternativa)

Se você preferir usar Docker para Redis e PostgreSQL:

### 1. Instale Docker Desktop

- **Windows/Mac**: [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- **Linux**: Siga as instruções para sua distribuição

### 2. Suba os serviços

```bash
docker-compose up -d redis postgres
```

### 3. Configure o `.env` para usar os containers

```env
REDIS_HOST=localhost
REDIS_PORT=6379

POSTGRES_CONNECTION_STRING=postgresql://bot_user:sua_senha@localhost:5432/whatsapp_bot
```

## 📋 Obtendo as Credenciais Necessárias

### OpenAI API Key
1. Acesse [platform.openai.com](https://platform.openai.com/)
2. Faça login ou crie uma conta
3. Vá em **API Keys**
4. Clique em **Create new secret key**
5. Copie a chave (começa com `sk-`)

### Supabase
1. Acesse [supabase.com](https://supabase.com/)
2. Crie um novo projeto
3. Vá em **Settings** → **API**
4. Copie:
   - **Project URL** (SUPABASE_URL)
   - **anon/public key** (SUPABASE_KEY)
   - **Connection String** (POSTGRES_CONNECTION_STRING)

### Evolution API (WhatsApp)
1. Configure sua própria instância da Evolution API
2. Ou use um serviço gerenciado
3. Obtenha:
   - URL da API
   - API Key
   - Nome da instância

### Google Calendar (Opcional)
1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto
3. Ative a **Google Calendar API**
4. Crie credenciais OAuth 2.0
5. Baixe o arquivo `credentials.json`
6. Coloque na raiz do projeto

## 🧪 Testando a Instalação

### Teste 1: Importar Módulos

```bash
python -c "from src.config import get_settings; print('✅ Config OK')"
```

### Teste 2: Conectar ao Redis (se instalado)

```bash
python -c "import redis; r = redis.Redis(host='localhost', port=6379); r.ping(); print('✅ Redis OK')"
```

### Teste 3: Conectar ao Supabase

```bash
python -c "from supabase import create_client; from src.config import get_settings; s = get_settings(); client = create_client(s.supabase_url, s.supabase_key); print('✅ Supabase OK')"
```

## 🔧 Solução de Problemas Comuns

### Erro: "No module named 'pydantic_settings'"

```bash
pip install pydantic-settings
```

### Erro: "redis.exceptions.ConnectionError"

Certifique-se de que o Redis está rodando:

```bash
# Testar conexão
redis-cli ping
```

Se não estiver instalado, instale:

**Windows**: Use Docker ou baixe do [site oficial](https://redis.io/download/)

**Linux**:
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

**Mac**:
```bash
brew install redis
brew services start redis
```

### Erro: "ValidationError" ao carregar settings

Verifique se o arquivo `.env` existe e todas as variáveis obrigatórias estão preenchidas:

```bash
# Listar variáveis faltando
python -c "from src.config import get_settings; get_settings()"
```

### Erro: Python não reconhecido

Certifique-se de que Python está no PATH:

**Windows**: Reinstale Python marcando a opção "Add Python to PATH"

**Linux/Mac**: Use `python3` ao invés de `python`

## 📚 Próximos Passos

Após a instalação bem-sucedida:

1. ✅ Leia o arquivo `README.md` para entender o projeto
2. ✅ Consulte `AGENTE LANGGRAPH.txt` para o plano de implementação
3. ✅ Comece pela **Fase 1**: Implementar modelos e tipos em `src/models/state.py`
4. ✅ Siga o roadmap sequencialmente (Fases 0-12)

## 🆘 Suporte

Se encontrar problemas:

1. Verifique se todas as dependências estão instaladas: `pip list`
2. Verifique se o Python é 3.11+: `python --version`
3. Verifique os logs em `bot.log`
4. Consulte a documentação oficial das bibliotecas

## ✅ Checklist de Instalação Completa

- [ ] Python 3.11+ instalado
- [ ] Ambiente virtual criado e ativado
- [ ] Dependências instaladas (`requirements.txt`)
- [ ] Arquivo `.env` criado e preenchido
- [ ] Credenciais OpenAI configuradas
- [ ] Credenciais Supabase configuradas
- [ ] Redis instalado/configurado
- [ ] Configurações testadas com sucesso
- [ ] Pronto para começar a implementação!

---

**Boa instalação! 🚀**

Em caso de dúvidas, consulte a documentação oficial ou abra uma issue no repositório.
