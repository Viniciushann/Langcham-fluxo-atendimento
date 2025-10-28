# ⚡ DEPLOY RÁPIDO VIA GITHUB - COMANDOS PRONTOS

## Servidor: 46.62.155.254

**COPIE E COLE OS COMANDOS ABAIXO NA ORDEM** 🚀

---

## 📋 PASSO 1: GERAR CHAVE SSH (5 min)

```bash
# Gerar chave SSH
ssh-keygen -t ed25519 -C "github-deploy-bot" -f ~/.ssh/github_deploy

# Quando perguntar senha, apenas ENTER (sem senha)

# Copiar chave pública para o servidor
ssh-copy-id -i ~/.ssh/github_deploy.pub root@46.62.155.254

# Digite a senha do servidor quando pedir

# Testar (NÃO deve pedir senha agora)
ssh -i ~/.ssh/github_deploy root@46.62.155.254
# Se conectou sem senha = SUCESSO!
# Digite 'exit' para sair
```

---

## 🔑 PASSO 2: OBTER CHAVE PRIVADA PARA GITHUB

```bash
# Windows (PowerShell):
Get-Content ~/.ssh/github_deploy | clip

# Windows (Git Bash):
cat ~/.ssh/github_deploy | clip.exe

# Linux/Mac:
cat ~/.ssh/github_deploy | pbcopy

# OU simplesmente exibir na tela:
cat ~/.ssh/github_deploy
```

**COPIE TODO O CONTEÚDO** (incluindo `-----BEGIN` e `-----END`)

---

## 🐙 PASSO 3: CRIAR REPOSITÓRIO GITHUB

### 3.1 Criar Repositório

1. Vá em: https://github.com/new
2. **Repository name:** `whatsapp-bot-langchain`
3. **Description:** `WhatsApp Bot com LangChain e Evolution API`
4. **Visibilidade:** ✅ **Private** (IMPORTANTE!)
5. Clique em **Create repository**

### 3.2 Configurar Secrets

1. No repositório criado, clique em **Settings**
2. Menu lateral: **Secrets and variables** > **Actions**
3. Clique em **New repository secret**

**Adicione estes 5 secrets:**

| Nome | Valor |
|------|-------|
| `SERVER_HOST` | `46.62.155.254` |
| `SERVER_USER` | `root` |
| `SERVER_PORT` | `22` |
| `SSH_PRIVATE_KEY` | Cole a chave privada completa (do passo 2) |
| `DOMAIN` | `centrooestedrywalldry.com.br` |

---

## 📤 PASSO 4: ENVIAR CÓDIGO PARA GITHUB

```bash
# Navegar para o projeto
cd "C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Langcham. fluxo atendimento"

# Inicializar Git (se ainda não fez)
git init

# Adicionar remote (SUBSTITUA seu-usuario pelo seu usuário do GitHub)
git remote add origin https://github.com/seu-usuario/whatsapp-bot-langchain.git

# Verificar o que será commitado (NÃO deve mostrar .env ou credentials.json)
git status

# Adicionar arquivos
git add .

# Commit
git commit -m "feat: Setup inicial com deploy automático"

# Push (PRIMEIRA VEZ vai pedir usuário e token do GitHub)
git push -u origin main
```

**Se pedir autenticação:**
- Usuário: seu username do GitHub
- Senha: usar **Personal Access Token** (não a senha normal)
  - Criar token: https://github.com/settings/tokens/new
  - Scopes: `repo` e `workflow`

---

## 🖥️ PASSO 5: PREPARAR SERVIDOR (10 min)

```bash
# Conectar no servidor
ssh root@46.62.155.254

# Navegar para /opt
cd /opt

# Clonar repositório (SUBSTITUA seu-usuario)
git clone https://github.com/seu-usuario/whatsapp-bot-langchain.git whatsapp-bot

# Entrar na pasta
cd whatsapp-bot

# Configurar .env
cp .env.template .env
nano .env
```

**Cole no .env (edite as credenciais se necessário):**

```env
WHATSAPP_API_URL=https://evolution.centrooestedrywalldry.com.br
WHATSAPP_API_KEY=8773E1C40430-4626-B896-1302789BA4D9
WHATSAPP_INSTANCE=Centro_oeste_draywal

OPENAI_API_KEY=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

SUPABASE_URL=https://znyypdwnqdlvqwwvffzk.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InpueXlwZHducWRsdnF3d3ZmZnprIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTk3NjE2MzgsImV4cCI6MjA3NTMzNzYzOH0.iKzAS6qHOHXPJ6aXQ3lmaoAvvp1VQmizDHDVvWLzdMA

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

SECRET_KEY=whatsapp-bot-secret-key-change-this-in-production
CORS_ORIGINS=https://evolution.centrooestedrywalldry.com.br

DOMAIN=centrooestedrywalldry.com.br
TELEFONE_TECNICO=556298540075
```

**Salvar:** `Ctrl+O`, `Enter`, `Ctrl+X`

---

## 📁 PASSO 6: COPIAR credentials.json

### Do Windows para o servidor:

```bash
# No seu computador (PowerShell ou Git Bash)
scp "C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Langcham. fluxo atendimento\credentials.json" root@46.62.155.254:/opt/whatsapp-bot/

# Digite a senha do servidor quando pedir
```

### Verificar no servidor:

```bash
# No servidor
cd /opt/whatsapp-bot
ls -la credentials.json
# Deve mostrar o arquivo
```

---

## 🐳 PASSO 7: PRIMEIRO DEPLOY MANUAL

```bash
# No servidor (/opt/whatsapp-bot)
docker-compose build
docker-compose up -d

# Aguardar ~1-2 minutos

# Verificar se está rodando
docker ps | grep whatsapp-bot

# Ver logs
docker logs -f whatsapp-bot

# Deve mostrar:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# Ctrl+C para sair dos logs

# Testar health
curl http://localhost:8000/health

# Deve retornar JSON com "status": "healthy"
```

**Se deu certo até aqui = SUCESSO! ✅**

---

## 🚀 PASSO 8: TESTAR DEPLOY AUTOMÁTICO

### No seu computador:

```bash
# Fazer uma mudança simples
cd "C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Langcham. fluxo atendimento"

# Editar README
echo "# Teste de deploy automático" >> README.md

# Commit e push
git add .
git commit -m "test: Deploy automático via GitHub"
git push origin main
```

### No GitHub:

1. Vá em: `https://github.com/seu-usuario/whatsapp-bot-langchain`
2. Clique na aba **Actions**
3. Você verá "Deploy to Hetzner" rodando (bolinha amarela girando)
4. Clique nele para ver os logs em tempo real
5. Aguarde ~2-3 minutos
6. Deve ficar verde ✅ = Deploy automático funcionou!

---

## ✅ VERIFICAR SE FUNCIONOU

```bash
# No servidor
ssh root@46.62.155.254
cd /opt/whatsapp-bot

# Ver último commit
git log --oneline -1
# Deve mostrar "test: Deploy automático via GitHub"

# Ver se container está rodando
docker ps | grep whatsapp-bot

# Ver logs
docker logs --tail 50 whatsapp-bot

# Testar
curl http://localhost:8000/health
```

---

## 🎉 PRONTO! DEPLOY AUTOMÁTICO CONFIGURADO!

Agora **TODA VEZ** que você fizer:

```bash
git add .
git commit -m "sua mensagem"
git push origin main
```

O bot será **atualizado automaticamente** no servidor em 2-3 minutos! 🚀

---

## 📱 TESTAR O BOT

Envie mensagem WhatsApp para: **+55 62 9274-5972**

```
"Olá"
"Quero agendar uma visita"
"Quanto custa drywall?"
```

---

## 🔧 COMANDOS ÚTEIS

### Ver Logs do GitHub Actions
```
https://github.com/seu-usuario/whatsapp-bot-langchain/actions
```

### Ver Logs do Bot no Servidor
```bash
ssh root@46.62.155.254
docker logs -f whatsapp-bot
```

### Restart Manual (se necessário)
```bash
ssh root@46.62.155.254
cd /opt/whatsapp-bot
docker-compose restart
```

### Ver Status
```bash
ssh root@46.62.155.254
docker ps | grep whatsapp-bot
docker stats whatsapp-bot
```

---

## ⚡ WORKFLOW DIÁRIO

```bash
# 1. Fazer mudanças no código
code src/nodes/agent.py

# 2. Testar localmente (opcional)
python src/main.py

# 3. Commit
git add .
git commit -m "feat: Nova funcionalidade"

# 4. Push (DEPLOY AUTOMÁTICO!)
git push origin main

# 5. Aguardar 2-3 minutos
# 6. Testar no WhatsApp

# Simples assim! 🎊
```

---

## 🆘 PROBLEMAS?

### Deploy falhou no GitHub Actions

```bash
# Ver erro específico em:
# GitHub > Actions > Click no deploy falhado > Ver steps
```

### Container não inicia no servidor

```bash
ssh root@46.62.155.254
cd /opt/whatsapp-bot
docker logs whatsapp-bot
# Ver erro específico
```

### SSH não conecta

```bash
# Testar manualmente
ssh -i ~/.ssh/github_deploy root@46.62.155.254

# Se falhar, verificar chave pública no servidor:
ssh root@46.62.155.254  # Com senha
cat ~/.ssh/authorized_keys | grep github
```

---

## 📚 DOCUMENTAÇÃO COMPLETA

- **DEPLOY_GITHUB.md** - Guia detalhado completo
- **DEPLOY_PASSO_A_PASSO.md** - Deploy via Portainer
- **.github/workflows/deploy.yml** - Configuração do GitHub Actions

---

**Bom deploy! 🚀**
