# ⚡ Quick Start - WhatsApp Bot LangGraph

Guia rápido para começar em 5 minutos!

---

## 🎯 Configuração Rápida

### 1️⃣ Instalar Dependências (1 min)

```bash
# Ativar ambiente virtual
venv\Scripts\activate

# Instalar dependências
pip install -r requirements.txt
```

### 2️⃣ Configurar Ambiente (2 min)

```bash
# Copiar template
cp .env.example .env
```

Edite `.env` e preencha **APENAS** o essencial:

```env
# Obrigatório
OPENAI_API_KEY=sk-proj-xxx
SUPABASE_URL=https://xxx.supabase.co
SUPABASE_KEY=eyJxxx
REDIS_HOST=localhost
WHATSAPP_API_URL=https://sua-evolution-api.com
WHATSAPP_API_KEY=sua-key
WHATSAPP_INSTANCE=sua-instancia
POSTGRES_CONNECTION_STRING=postgresql://user:pass@localhost:5432/db
SECRET_KEY=your-secret-key-here
```

### 3️⃣ Iniciar Redis (30 segundos)

```bash
# Opção 1: Docker
docker run -d -p 6379:6379 redis

# Opção 2: Local (se já instalado)
redis-server
```

### 4️⃣ Testar Configuração (30 segundos)

```bash
python -c "from src.config.settings import get_settings; print('✅ OK!')"
```

### 5️⃣ Executar Bot (30 segundos)

```bash
python src/main.py
```

---

## 📱 Teste Rápido

### Teste Google Calendar

```bash
python test_google_calendar.py
```

**Na primeira execução:**
1. Um navegador abrirá
2. Faça login no Google
3. Autorize o aplicativo
4. Pronto! `token.json` criado

---

## 🗂️ Arquivos Principais

| Arquivo | Descrição |
|---------|-----------|
| `.env` | Suas configurações (criar do .env.example) |
| `requirements.txt` | Dependências Python |
| `src/config/settings.py` | Configurações validadas |
| `src/models/state.py` | Estado do agente LangGraph |
| `src/tools/scheduling.py` | Ferramenta de agendamento |

---

## 📖 Documentação

- **Instalação Completa**: `INSTALLATION.md`
- **README Principal**: `README.md`
- **Google Calendar**: `GOOGLE_CALENDAR_SETUP.md`
- **Status do Projeto**: `PROJECT_SETUP_COMPLETE.md`

---

## 🐛 Problemas Comuns

### "ModuleNotFoundError: No module named 'src'"

```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### "Redis connection refused"

```bash
# Verifique se está rodando
redis-cli ping

# Se não, inicie
docker start redis
```

### "OpenAI API key not found"

Verifique se `.env` foi criado e OPENAI_API_KEY está preenchido.

---

## ✅ Checklist Mínimo

- [ ] Python 3.11+ instalado
- [ ] `venv` ativado
- [ ] `pip install -r requirements.txt` executado
- [ ] `.env` criado e preenchido
- [ ] Redis rodando
- [ ] Teste passou: `python -c "from src.config.settings import get_settings; print('OK')"`

---

## 🚀 Próximos Passos

1. **Configurar Google Calendar** → `GOOGLE_CALENDAR_SETUP.md`
2. **Configurar Supabase** → Criar tabelas (SQL no `INSTALLATION.md`)
3. **Implementar Nodes** → Seguir roadmap no `README.md`
4. **Testar Webhook** → Configurar Evolution API

---

## 🆘 Ajuda

- **Instalação Detalhada**: `INSTALLATION.md`
- **Troubleshooting**: Seção de problemas no `INSTALLATION.md`
- **Arquitetura**: Diagramas no `README.md`

---

**Tempo estimado de setup**: ⏱️ 5-10 minutos

**Pronto para começar!** 🎉
