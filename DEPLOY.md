# 🚀 GUIA DE DEPLOY - SERVIDOR HETZNER COM PORTAINER

## 📋 Pré-requisitos

Seu servidor Hetzner já possui:

- ✅ Docker instalado
- ✅ Portainer configurado
- ✅ Traefik (para SSL/HTTPS)
- ✅ Evolution API (stack "evolution")
- ✅ Redis (stack "redis")
- ✅ PostgreSQL (stack "postgres")
- ✅ n8n (opcional)

## 🎯 Arquitetura do Deploy

```
┌─────────────────────────────────────────────┐
│           SERVIDOR HETZNER                   │
├─────────────────────────────────────────────┤
│                                              │
│  ┌──────────────────────────────────────┐  │
│  │         Traefik (SSL/HTTPS)           │  │
│  └──────────────────────────────────────┘  │
│                     │                        │
│  ┌──────────────────────────────────────┐  │
│  │      WhatsApp Bot (Porta 8000)       │  │
│  │  - FastAPI + LangChain + LangGraph   │  │
│  │  - OpenAI GPT-4                       │  │
│  │  - Supabase (PostgreSQL + Vectors)   │  │
│  └──────────────────────────────────────┘  │
│          │              │                    │
│  ┌───────────┐   ┌──────────────┐          │
│  │   Redis   │   │  Evolution   │          │
│  │  (Stack)  │   │     API      │          │
│  └───────────┘   └──────────────┘          │
│                                              │
└─────────────────────────────────────────────┘
```

---

## 📦 PASSO 1: Preparar o Projeto Localmente

### 1.1 Criar arquivo

Certifique-se de que todas as dependências estão listadas:

```bash
pip freeze > requirements.txt
```

### 1.2 Copiar credentials.json do Google Calendar

O arquivo `credentials.json` deve estar na raiz do projeto.

### 1.3 Configurar .env de produção

Copie `.env.production` para `.env` e preencha com suas credenciais:

```bash
cp .env.production .env
```

Edite o arquivo `.env` e configure:

- `WHATSAPP_API_KEY` - Chave da Evolution API
- `OPENAI_API_KEY` - Chave da OpenAI
- `SUPABASE_KEY` - Chave do Supabase
- `POSTGRES_CONNECTION_STRING` - String de conexão do Supabase
- `SECRET_KEY` - Gere uma chave única
- `DOMAIN` - Seu domínio (ex: `meusite.com`)

**Gerar SECRET_KEY:**

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

---

## 🐳 PASSO 2: Build da Imagem Docker

### 2.1 Fazer build local (opcional, para testar)

```bash
docker build -t whatsapp-bot-langchain:latest .
```

### 2.2 Testar localmente

```bash
docker-compose up -d
```

Acesse: `http://localhost:8000/health`

---

## 📤 PASSO 3: Enviar para o Servidor

### Opção A: Via Git (Recomendado)

1. **Criar repositório Git privado** (GitHub, GitLab, Bitbucket)

2. **Adicionar .gitignore:**

```gitignore
.env
credentials.json
token.json
*.log
__pycache__/
.venv/
```

3. **Fazer commit e push:**

```bash
git init
git add .
git commit -m "Initial commit - WhatsApp Bot"
git remote add origin https://github.com/seu-usuario/whatsapp-bot.git
git push -u origin main
```

4. **No servidor Hetzner, clonar o repositório:**

```bash
ssh root@seu-servidor-hetzner
cd /opt
git clone https://github.com/seu-usuario/whatsapp-bot.git
cd whatsapp-bot
```

### Opção B: Via SCP (Alternativa)

```bash
# Compactar projeto
tar -czf whatsapp-bot.tar.gz .

# Enviar para servidor
scp whatsapp-bot.tar.gz root@seu-servidor:/opt/

# No servidor, descompactar
ssh root@seu-servidor
cd /opt
tar -xzf whatsapp-bot.tar.gz
```

---

## 🎛️ PASSO 4: Deploy no Portainer

### 4.1 Acessar Portainer

Acesse: `https://portainer.seu-dominio.com`

### 4.2 Criar novo Stack

1. Vá em **Stacks** → **Add stack**
2. Nome: `whatsapp-bot`
3. Build method: **Upload** ou **Git repository**

### 4.3 Configurar Variáveis de Ambiente

No Portainer, vá em **Environment variables** e adicione:

```env
WHATSAPP_API_URL=https://evolution.centrooestedrywalldry.com.br
WHATSAPP_API_KEY=sua-chave-evolution
WHATSAPP_INSTANCE=Centro_oeste_draywal
OPENAI_API_KEY=sk-proj-xxxxx
SUPABASE_URL=https://znyypdwnqdlvqwwvffzk.supabase.co
SUPABASE_KEY=eyJhbGc...
REDIS_HOST=redis
REDIS_PORT=6379
POSTGRES_CONNECTION_STRING=postgresql://postgres:senha@db.znyypdwnqdlvqwwvffzk.supabase.co:5432/postgres
SECRET_KEY=sua-chave-secreta-gerada
DOMAIN=seu-dominio.com
```

### 4.4 Configurar Networks

Certifique-se de que o stack está conectado às networks:

- ✅ `traefik-public` (para SSL)
- ✅ `redis_default` (para Redis)

### 4.5 Deploy!

Clique em **Deploy the stack**

---

## 🔧 PASSO 5: Configurar Supabase

### 5.1 Criar Tabelas

Acesse o Supabase SQL Editor e execute:

```sql
-- Copiar conteúdo de create_tables.sql
-- Criar tabelas: leads, message_history, conhecimento
```

### 5.2 Habilitar Row Level Security (RLS)

```sql
ALTER TABLE leads ENABLE ROW LEVEL SECURITY;
ALTER TABLE message_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE conhecimento ENABLE ROW LEVEL SECURITY;

-- Criar políticas
CREATE POLICY "Enable all for service role" ON leads
  FOR ALL USING (true);

CREATE POLICY "Enable all for service role" ON message_history
  FOR ALL USING (true);

CREATE POLICY "Enable all for service role" ON conhecimento
  FOR ALL USING (true);
```

### 5.3 Popular Base de Conhecimento

Use o n8n (stack existente) ou script Python para popular a tabela `conhecimento` com informações sobre:

- Serviços de drywall
- Preços
- Processos
- FAQs

---

## 🌐 PASSO 6: Configurar DNS e SSL

### 6.1 Adicionar registro DNS

No seu provedor de DNS, adicione:

```
Tipo: A
Nome: bot
Valor: IP-DO-SERVIDOR-HETZNER
TTL: 300
```

### 6.2 Verificar SSL

O Traefik gerará automaticamente o certificado SSL via Let's Encrypt.

Aguarde 2-5 minutos e acesse:

```
https://bot.seu-dominio.com/health
```

Deve retornar:

```json
{
  "status": "healthy",
  "environment": "production",
  ...
}
```

---

## 🔗 PASSO 7: Configurar Webhook da Evolution API

### 7.1 Acessar Evolution API

```
https://evolution.centrooestedrywalldry.com.br/manager
```

### 7.2 Configurar Webhook

No painel da instância `Centro_oeste_draywal`, configure:

**Webhook URL:**

```
https://bot.seu-dominio.com/webhook
```

**Eventos:**

- ✅ messages.upsert

**Configurações:**

- ✅ webhookBase64: true

---

## ✅ PASSO 8: Verificações Finais

### 8.1 Health Check

```bash
curl https://bot.seu-dominio.com/health
```

### 8.2 Verificar Logs

No Portainer:

1. Vá em **Containers**
2. Clique em `whatsapp-bot`
3. Vá em **Logs**

### 8.3 Testar Webhook

Envie mensagem WhatsApp para o número conectado e verifique:

- ✅ Webhook recebido
- ✅ Mensagem processada
- ✅ Resposta enviada

---

## 🔄 Atualização do Bot

### Atualizar via Git:

```bash
ssh root@seu-servidor
cd /opt/whatsapp-bot
git pull
docker-compose down
docker-compose up -d --build
```

### Atualizar via Portainer:

1. Vá em **Stacks** → `whatsapp-bot`
2. Clique em **Editor**
3. Faça alterações necessárias
4. Clique em **Update the stack**

---

## 📊 Monitoramento

### Logs em Tempo Real:

```bash
docker logs -f whatsapp-bot
```

### Métricas:

Portainer Dashboard mostra:

- CPU e Memória
- Network I/O
- Uptime
- Health status

---

## 🆘 Troubleshooting

### Problema: Container não inicia

**Solução:**

```bash
docker logs whatsapp-bot
# Verificar erro específico
```

### Problema: Não conecta ao Redis

**Verificar:** Network `redis_default` está configurada?

```bash
docker network ls
docker network inspect redis_default
```

### Problema: Evolution API não recebe webhook

**Verificar:**

1. DNS do domínio `bot.seu-dominio.com` está correto?
2. Firewall permite porta 443?
3. Traefik está rodando?

```bash
docker ps | grep traefik
```

### Problema: Google Calendar não funciona

**Solução:**

1. Copiar `credentials.json` para o volume:

```bash
docker cp credentials.json whatsapp-bot:/app/credentials.json
docker restart whatsapp-bot
```

---

## 📞 Contatos de Suporte

- **Evolution API:** https://doc.evolution-api.com
- **Supabase:** https://supabase.com/docs
- **LangChain:** https://python.langchain.com/docs

---

## ✅ Checklist Final

- [ ] Servidor Hetzner configurado
- [ ] Portainer funcionando
- [ ] Redis stack ativo
- [ ] Evolution API configurada
- [ ] Supabase tabelas criadas
- [ ] DNS configurado
- [ ] SSL funcionando (HTTPS)
- [ ] Webhook Evolution configurado
- [ ] Google Calendar credentials copiado
- [ ] Stack WhatsApp Bot deployado
- [ ] Health check OK
- [ ] Teste de mensagem funcionando

---

**🎉 DEPLOY CONCLUÍDO COM SUCESSO!**

Seu WhatsApp Bot está rodando em produção no servidor Hetzner!
