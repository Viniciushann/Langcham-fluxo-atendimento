# 🚀 GUIA COMPLETO DE DEPLOY - PASSO A PASSO

## Servidor Hetzner com Portainer, Traefik, Redis e Evolution API

Este guia mostra EXATAMENTE como fazer o deploy do WhatsApp Bot no seu servidor Hetzner que já possui:
- ✅ Docker instalado
- ✅ Portainer configurado
- ✅ Traefik (SSL/HTTPS)
- ✅ Evolution API
- ✅ Redis
- ✅ PostgreSQL (Supabase)

---

## 📋 PRÉ-REQUISITOS

### No Seu Computador Local:
- [x] Git instalado
- [x] Projeto clonado/baixado
- [x] Credenciais configuradas (.env)
- [x] credentials.json do Google Calendar na raiz do projeto

### No Servidor Hetzner:
- [x] Acesso SSH (root@seu-ip)
- [x] Portainer rodando (https://portainer.seu-dominio.com)
- [x] Traefik configurado para SSL
- [x] Evolution API funcionando
- [x] Redis stack ativo
- [x] DNS configurado para o domínio

---

## 🎯 RESUMO DO QUE VAMOS FAZER

1. Preparar o projeto localmente
2. Enviar para o servidor
3. Fazer deploy no Portainer
4. Configurar webhook da Evolution API
5. Testar funcionamento

**Tempo estimado: 15-20 minutos**

---

## 📝 PASSO 1: PREPARAR PROJETO LOCALMENTE

### 1.1 Verificar Estrutura do Projeto

```bash
cd "C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Langcham. fluxo atendimento"

# Verificar se tem todos os arquivos necessários
dir
```

**Arquivos obrigatórios:**
- ✅ Dockerfile
- ✅ docker-compose.yml
- ✅ requirements.txt
- ✅ .env (com suas credenciais)
- ✅ credentials.json (Google Calendar)
- ✅ Pasta src/ com todo o código

### 1.2 Configurar Variáveis de Ambiente

```bash
# Se ainda não tem o .env, copie do template
copy .env.template .env

# Edite o .env com suas credenciais reais
notepad .env
```

**Variáveis OBRIGATÓRIAS para produção:**

```env
# Evolution API
WHATSAPP_API_URL=https://evolution.centrooestedrywalldry.com.br
WHATSAPP_API_KEY=sua-chave-real
WHATSAPP_INSTANCE=Centro_oeste_draywal

# OpenAI
OPENAI_API_KEY=sk-proj-...

# Supabase
SUPABASE_URL=https://znyypdwnqdlvqwwvffzk.supabase.co
SUPABASE_KEY=eyJ...

# Redis (IMPORTANTE: use "redis" não "localhost")
REDIS_HOST=redis
REDIS_PORT=6379

# PostgreSQL
POSTGRES_CONNECTION_STRING=postgresql://postgres:senha@db.znyypdwnqdlvqwwvffzk.supabase.co:5432/postgres?sslmode=require

# Aplicação
ENVIRONMENT=production
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO

# Domínio
DOMAIN=seu-dominio.com
```

### 1.3 Verificar credentials.json

```bash
# Verificar se existe
dir credentials.json

# Deve ser um arquivo JSON válido do Google Cloud
# Se não tem, veja GOOGLE_CALENDAR_SETUP.md
```

---

## 📤 PASSO 2: ENVIAR PARA O SERVIDOR

### Opção A: Via Git (RECOMENDADO)

#### 2.1 Criar Repositório Git Privado

1. Vá em https://github.com/new
2. Nome: `whatsapp-bot-langchain` (ou outro nome)
3. **IMPORTANTE:** Marque como **PRIVADO**
4. Crie o repositório

#### 2.2 Preparar Projeto para Git

```bash
cd "C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Langcham. fluxo atendimento"

# Inicializar Git (se ainda não iniciado)
git init

# Adicionar remote
git remote add origin https://github.com/seu-usuario/whatsapp-bot-langchain.git

# IMPORTANTE: Verificar .gitignore
# Deve conter:
# .env
# credentials.json
# token.json
type .gitignore
```

#### 2.3 Fazer Commit e Push

```bash
# Ver o que será commitado (NÃO deve mostrar .env ou credentials.json)
git status

# Adicionar arquivos
git add .

# Commit
git commit -m "Deploy: WhatsApp Bot LangChain v1.0"

# Push
git push -u origin main
```

#### 2.4 Clonar no Servidor

```bash
# Conectar no servidor
ssh root@seu-ip-hetzner

# Ir para /opt
cd /opt

# Clonar repositório
git clone https://github.com/seu-usuario/whatsapp-bot-langchain.git whatsapp-bot

# Entrar na pasta
cd whatsapp-bot

# Verificar arquivos
ls -la
```

### Opção B: Via SCP (Alternativa)

```bash
# Compactar projeto (excluindo arquivos desnecessários)
tar -czf whatsapp-bot.tar.gz --exclude='.venv' --exclude='__pycache__' --exclude='*.log' .

# Enviar para servidor
scp whatsapp-bot.tar.gz root@seu-ip:/opt/

# No servidor, descompactar
ssh root@seu-ip
cd /opt
tar -xzf whatsapp-bot.tar.gz -C whatsapp-bot
cd whatsapp-bot
```

---

## 📁 PASSO 3: CONFIGURAR .ENV NO SERVIDOR

```bash
# No servidor (/opt/whatsapp-bot)
cd /opt/whatsapp-bot

# Criar .env a partir do template
cp .env.template .env

# Editar com nano
nano .env
```

**Cole as variáveis de produção:**

```env
WHATSAPP_API_URL=https://evolution.centrooestedrywalldry.com.br
WHATSAPP_API_KEY=8773E1C40430-4626-B896-1302789BA4D9
WHATSAPP_INSTANCE=Centro_oeste_draywal

OPENAI_API_KEY=sk-proj-...

SUPABASE_URL=https://znyypdwnqdlvqwwvffzk.supabase.co
SUPABASE_KEY=eyJ...

REDIS_HOST=redis
REDIS_PORT=6379
REDIS_PASSWORD=
REDIS_DB=0

POSTGRES_CONNECTION_STRING=postgresql://postgres:FBB1qGOo1wtlKBk2@db.znyypdwnqdlvqwwvffzk.supabase.co:5432/postgres?sslmode=require

GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json

BOT_PHONE_NUMBER=556292745972
MESSAGE_GROUP_DELAY=25
MAX_FRAGMENT_SIZE=300

AGENT_TIMEOUT=60
MAX_RETRIES=3
ENABLE_MEMORY_PERSISTENCE=True

ENVIRONMENT=production
PORT=8000
HOST=0.0.0.0
LOG_LEVEL=INFO

SECRET_KEY=gere-uma-chave-aqui-com-secrets-token-urlsafe
CORS_ORIGINS=https://evolution.centrooestedrywalldry.com.br

DOMAIN=seu-dominio.com
TELEFONE_TECNICO=556298540075
```

**Salvar:** Ctrl+O, Enter, Ctrl+X

---

## 📁 PASSO 4: COPIAR credentials.json PARA O SERVIDOR

```bash
# Do seu computador local
scp "C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Langcham. fluxo atendimento\credentials.json" root@seu-ip:/opt/whatsapp-bot/

# Verificar no servidor
ssh root@seu-ip
cd /opt/whatsapp-bot
ls -la credentials.json
```

---

## 🐳 PASSO 5: DEPLOY NO PORTAINER

### 5.1 Acessar Portainer

Abra no navegador: `https://portainer.seu-dominio.com`

### 5.2 Criar Novo Stack

1. Menu lateral: **Stacks**
2. Botão: **+ Add stack**
3. Nome: `whatsapp-bot`
4. Build method: **Repository** ou **Upload**

### 5.3 Opção A: Via Repository (se usou Git)

- **Repository URL:** `https://github.com/seu-usuario/whatsapp-bot-langchain`
- **Repository reference:** `refs/heads/main`
- **Compose path:** `docker-compose.yml`
- **Authentication:** Configurar se repositório privado

### 5.4 Opção B: Via Upload/Editor

Cole o conteúdo do **docker-compose.yml**:

```yaml
version: '3.8'

services:
  whatsapp-bot:
    image: whatsapp-bot-langchain:latest
    build:
      context: /opt/whatsapp-bot
      dockerfile: Dockerfile
    container_name: whatsapp-bot
    restart: unless-stopped

    environment:
      - WHATSAPP_API_URL=${WHATSAPP_API_URL}
      - WHATSAPP_API_KEY=${WHATSAPP_API_KEY}
      - WHATSAPP_INSTANCE=${WHATSAPP_INSTANCE}
      - OPENAI_API_KEY=${OPENAI_API_KEY}
      - SUPABASE_URL=${SUPABASE_URL}
      - SUPABASE_KEY=${SUPABASE_KEY}
      - REDIS_HOST=redis
      - REDIS_PORT=6379
      - POSTGRES_CONNECTION_STRING=${POSTGRES_CONNECTION_STRING}
      - GOOGLE_CALENDAR_CREDENTIALS_FILE=/app/credentials.json
      - BOT_PHONE_NUMBER=${BOT_PHONE_NUMBER}
      - MESSAGE_GROUP_DELAY=25
      - MAX_FRAGMENT_SIZE=300
      - AGENT_TIMEOUT=60
      - MAX_RETRIES=3
      - ENABLE_MEMORY_PERSISTENCE=True
      - ENVIRONMENT=production
      - PORT=8000
      - HOST=0.0.0.0
      - LOG_LEVEL=INFO
      - SECRET_KEY=${SECRET_KEY}
      - CORS_ORIGINS=${CORS_ORIGINS}
      - TELEFONE_TECNICO=${TELEFONE_TECNICO}

    volumes:
      - /opt/whatsapp-bot/credentials.json:/app/credentials.json:ro
      - /opt/whatsapp-bot/token.json:/app/token.json
      - whatsapp-bot-logs:/app/logs

    ports:
      - "8000:8000"

    networks:
      - traefik-public
      - redis_default

    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.whatsapp-bot.rule=Host(`bot.${DOMAIN}`)"
      - "traefik.http.routers.whatsapp-bot.entrypoints=websecure"
      - "traefik.http.routers.whatsapp-bot.tls.certresolver=letsencrypt"
      - "traefik.http.services.whatsapp-bot.loadbalancer.server.port=8000"
      - "traefik.docker.network=traefik-public"

    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s

networks:
  traefik-public:
    external: true
  redis_default:
    external: true

volumes:
  whatsapp-bot-logs:
    driver: local
```

### 5.5 Adicionar Environment Variables

Na seção **Environment variables**, clique em **+ add environment variable** e adicione:

| Nome | Valor |
|------|-------|
| WHATSAPP_API_KEY | sua-chave-evolution |
| OPENAI_API_KEY | sk-proj-... |
| SUPABASE_KEY | eyJ... |
| POSTGRES_CONNECTION_STRING | postgresql://... |
| SECRET_KEY | sua-chave-secreta |
| DOMAIN | seu-dominio.com |
| TELEFONE_TECNICO | 556298540075 |

*Ou carregue do arquivo .env*

### 5.6 Deploy!

Click **Deploy the stack**

Aguarde o build (pode levar 2-5 minutos na primeira vez)

---

## ✅ PASSO 6: VERIFICAR DEPLOYMENT

### 6.1 Ver Logs no Portainer

1. Vá em **Containers**
2. Clique em `whatsapp-bot`
3. Vá em **Logs**
4. **Scroll** até o final

**Logs esperados:**
```
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6.2 Health Check

```bash
# No navegador ou via curl
curl https://bot.seu-dominio.com/health

# Resposta esperada:
{
  "status": "healthy",
  "environment": "production",
  "timestamp": "2025-10-28T12:00:00",
  ...
}
```

### 6.3 Verificar Networks

```bash
# No servidor
docker network inspect redis_default

# Deve mostrar o container whatsapp-bot conectado
```

---

## 🔗 PASSO 7: CONFIGURAR WEBHOOK DA EVOLUTION API

### 7.1 Acessar Evolution API

```
https://evolution.centrooestedrywalldry.com.br/manager
```

### 7.2 Configurar Webhook na Instância

1. Selecione a instância: **Centro_oeste_draywal**
2. Vá em **Webhooks** ou **Settings**
3. Configure:

**Webhook URL:**
```
https://bot.seu-dominio.com/webhook
```

**Events/Eventos:**
- ☑️ messages.upsert (OBRIGATÓRIO)
- ☑️ messages.update (opcional)

**Configurações:**
- ☑️ webhookBase64: **true** (IMPORTANTE!)
- ☑️ webhookByEvents: **true**

4. **Salvar**

### 7.3 Testar Webhook

```bash
# Enviar mensagem de teste
curl -X POST https://bot.seu-dominio.com/webhook \
  -H "Content-Type: application/json" \
  -d '{"test": true}'

# Deve retornar HTTP 200
```

---

## 📱 PASSO 8: TESTAR O BOT

### 8.1 Enviar Mensagem no WhatsApp

Envie uma mensagem para o número do bot: **+55 62 9274-5972**

**Exemplos de teste:**
```
"Olá"
"Quero agendar uma visita"
"Quanto custa drywall?"
```

### 8.2 Verificar Logs em Tempo Real

```bash
# No servidor
cd /opt/whatsapp-bot
docker logs -f whatsapp-bot

# Ou no Portainer: Containers > whatsapp-bot > Logs > Auto-refresh ON
```

### 8.3 Verificar no Supabase

Acesse: https://znyypdwnqdlvqwwvffzk.supabase.co

1. **Table Editor**
2. Tabela: **leads**
3. Deve aparecer o cliente
4. Tabela: **message_history**
5. Deve aparecer a conversa

---

## 🔧 PASSO 9: CONFIGURAÇÕES ADICIONAIS

### 9.1 Configurar DNS (se ainda não fez)

No seu provedor de DNS, adicione:

```
Tipo: A
Nome: bot
Valor: IP-DO-SERVIDOR-HETZNER
TTL: 300
```

Aguarde propagação (2-10 minutos)

### 9.2 Verificar SSL

```bash
# Testar certificado
curl -vI https://bot.seu-dominio.com/health

# Deve mostrar certificado Let's Encrypt válido
```

### 9.3 Criar Tabelas no Supabase (se ainda não fez)

Execute o SQL em: https://znyypdwnqdlvqwwvffzk.supabase.co

```sql
-- Ver arquivo: create_tables.sql ou setup_rag_supabase.sql
```

---

## 🔄 ATUALIZAÇÕES FUTURAS

### Atualizar o Bot

```bash
# 1. No seu computador, fazer mudanças
git add .
git commit -m "Update: descrição"
git push

# 2. No servidor
cd /opt/whatsapp-bot
git pull

# 3. No Portainer
# Vá em Stacks > whatsapp-bot
# Clique em "Update the stack"
# Ou: Pull and redeploy
```

### Rollback em Caso de Problema

```bash
# No servidor
cd /opt/whatsapp-bot
git log --oneline  # Ver commits
git checkout <hash-commit-anterior>

# No Portainer: Update stack
```

---

## 📊 MONITORAMENTO

### Ver Logs

```bash
# Logs completos
docker logs whatsapp-bot

# Últimas 100 linhas
docker logs --tail 100 whatsapp-bot

# Tempo real
docker logs -f whatsapp-bot

# Filtrar erros
docker logs whatsapp-bot 2>&1 | grep ERROR
```

### Verificar Recursos

```bash
# CPU e Memória
docker stats whatsapp-bot

# No Portainer: Containers > whatsapp-bot > Stats
```

### Healthcheck

```bash
# Status do container
docker inspect whatsapp-bot | grep -A 5 Health

# Endpoint HTTP
curl https://bot.seu-dominio.com/health
```

---

## ⚠️ TROUBLESHOOTING

### Problema: Container não inicia

```bash
# Ver logs de erro
docker logs whatsapp-bot

# Verificar se porta está livre
ss -tulpn | grep 8000

# Recriar container
docker-compose down
docker-compose up -d
```

### Problema: Webhook não recebe mensagens

1. Verificar webhook configurado na Evolution API
2. Testar manualmente: `curl -X POST https://bot.seu-dominio.com/webhook`
3. Ver logs: `docker logs -f whatsapp-bot`
4. Verificar firewall: porta 443 aberta

### Problema: Erro de conexão com Redis

```bash
# Verificar se Redis está rodando
docker ps | grep redis

# Testar conexão
docker exec whatsapp-bot ping redis

# Verificar network
docker network inspect redis_default
```

### Problema: Google Calendar não funciona

```bash
# Verificar se credentials.json foi copiado
docker exec whatsapp-bot ls -la /app/credentials.json

# Copiar novamente
docker cp credentials.json whatsapp-bot:/app/

# Restart
docker restart whatsapp-bot
```

---

## ✅ CHECKLIST FINAL

- [ ] Bot respondendo mensagens no WhatsApp
- [ ] Webhook Evolution API configurado
- [ ] SSL funcionando (https://bot.seu-dominio.com)
- [ ] Health check retornando 200
- [ ] Logs sem erros
- [ ] Redis conectado
- [ ] Supabase salvando conversas
- [ ] Google Calendar agendando
- [ ] Notificações ao técnico funcionando

---

## 📚 PRÓXIMOS PASSOS

1. **Monitoramento:** Configure alertas (Prometheus/Grafana)
2. **Backup:** Configure backup automático do Redis e logs
3. **CI/CD:** Implemente GitHub Actions para deploy automático
4. **Testes:** Crie testes automatizados
5. **Documentação:** Documente processos específicos do negócio

---

## 🆘 SUPORTE

### Logs Importantes

```bash
# Bot
docker logs -f whatsapp-bot

# Redis
docker logs -f redis

# Traefik
docker logs -f traefik

# Evolution API
docker logs -f evolution-api
```

### Arquivos Importantes

```
/opt/whatsapp-bot/.env
/opt/whatsapp-bot/credentials.json
/opt/whatsapp-bot/docker-compose.yml
/opt/whatsapp-bot/logs/
```

### Comandos Úteis

```bash
# Restart
docker restart whatsapp-bot

# Stop
docker stop whatsapp-bot

# Start
docker start whatsapp-bot

# Rebuild
docker-compose up -d --build

# Remove e recria
docker-compose down
docker-compose up -d
```

---

## 🎉 PARABÉNS!

Seu WhatsApp Bot está no ar! 🚀

O bot agora está:
- ✅ Rodando em produção no Hetzner
- ✅ Com SSL/HTTPS automático
- ✅ Integrado com Evolution API
- ✅ Salvando dados no Supabase
- ✅ Usando Redis para fila
- ✅ Agendando no Google Calendar
- ✅ Notificando o técnico automaticamente

**Aproveite! 🎊**
