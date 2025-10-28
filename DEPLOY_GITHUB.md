# 🚀 DEPLOY AUTOMÁTICO VIA GITHUB

## Deploy automático no Hetzner via GitHub Actions

Este guia mostra como configurar deploy automático: **você faz push no GitHub → bot atualiza automaticamente no servidor!**

---

## 🎯 O QUE VAI ACONTECER

Quando você fizer `git push`:
1. ✅ GitHub Actions inicia automaticamente
2. ✅ Valida o código Python
3. ✅ Conecta no servidor Hetzner via SSH
4. ✅ Faz `git pull` das mudanças
5. ✅ Rebuilda a imagem Docker
6. ✅ Reinicia o container
7. ✅ Verifica se está funcionando
8. ✅ Você recebe notificação de sucesso/falha

**Tempo total: ~2-3 minutos por deploy** ⚡

---

## 📋 PRÉ-REQUISITOS

### No GitHub:
- [x] Repositório criado (privado recomendado)
- [x] Acesso de administrador ao repositório

### No Servidor Hetzner:
- [x] Projeto clonado em `/opt/whatsapp-bot`
- [x] Docker e docker-compose instalados
- [x] Acesso SSH configurado

---

## 🔐 PASSO 1: GERAR CHAVE SSH

### 1.1 No Seu Computador

```bash
# Gerar chave SSH (se ainda não tem)
ssh-keygen -t ed25519 -C "github-deploy-whatsapp-bot" -f ~/.ssh/github_deploy

# Windows: usar Git Bash ou WSL
# Vai criar 2 arquivos:
# ~/.ssh/github_deploy (chave privada)
# ~/.ssh/github_deploy.pub (chave pública)
```

### 1.2 Copiar Chave Pública para o Servidor

```bash
# Copiar chave pública para o servidor
ssh-copy-id -i ~/.ssh/github_deploy.pub root@SEU-IP-HETZNER

# Ou manualmente:
cat ~/.ssh/github_deploy.pub
# Copie o conteúdo

# No servidor:
ssh root@SEU-IP-HETZNER
mkdir -p ~/.ssh
nano ~/.ssh/authorized_keys
# Cole a chave pública
# Salve: Ctrl+O, Enter, Ctrl+X
```

### 1.3 Testar Conexão SSH

```bash
# Testar se funciona
ssh -i ~/.ssh/github_deploy root@SEU-IP-HETZNER

# Deve conectar sem pedir senha
# Se funcionar, está pronto!
```

---

## 🔑 PASSO 2: CONFIGURAR SECRETS NO GITHUB

### 2.1 Acessar Settings do Repositório

1. Vá no seu repositório: `https://github.com/seu-usuario/whatsapp-bot-langchain`
2. Clique em **Settings**
3. Menu lateral: **Secrets and variables** > **Actions**
4. Clique em **New repository secret**

### 2.2 Adicionar Secrets

Adicione os seguintes secrets (um por um):

#### SECRET 1: SERVER_HOST
```
Name: SERVER_HOST
Value: SEU-IP-HETZNER
```
Exemplo: `157.230.123.45`

#### SECRET 2: SERVER_USER
```
Name: SERVER_USER
Value: root
```

#### SECRET 3: SERVER_PORT
```
Name: SERVER_PORT
Value: 22
```
(ou outra porta se mudou o SSH)

#### SECRET 4: SSH_PRIVATE_KEY
```
Name: SSH_PRIVATE_KEY
Value: [conteúdo completo da chave privada]
```

**Como obter a chave privada:**

```bash
# No seu computador
cat ~/.ssh/github_deploy

# Copie TODO o conteúdo, incluindo:
# -----BEGIN OPENSSH PRIVATE KEY-----
# ... linhas da chave ...
# -----END OPENSSH PRIVATE KEY-----
```

**IMPORTANTE:** Cole EXATAMENTE como está, incluindo as linhas BEGIN e END!

#### SECRET 5: DOMAIN (opcional)
```
Name: DOMAIN
Value: seu-dominio.com
```

### 2.3 Verificar Secrets

Você deve ter:
- ✅ SERVER_HOST
- ✅ SERVER_USER
- ✅ SERVER_PORT
- ✅ SSH_PRIVATE_KEY
- ✅ DOMAIN (opcional)

---

## 📁 PASSO 3: PREPARAR O SERVIDOR

### 3.1 Clonar Repositório no Servidor (se ainda não fez)

```bash
# Conectar no servidor
ssh root@SEU-IP-HETZNER

# Navegar para /opt
cd /opt

# Clonar repositório
git clone https://github.com/seu-usuario/whatsapp-bot-langchain.git whatsapp-bot

# Entrar na pasta
cd whatsapp-bot

# Configurar .env
cp .env.template .env
nano .env
# Preencher com credenciais
# Salvar: Ctrl+O, Enter, Ctrl+X

# Copiar credentials.json (se ainda não fez)
# Do seu computador:
# scp credentials.json root@SEU-IP:/opt/whatsapp-bot/
```

### 3.2 Fazer o Primeiro Deploy Manual

```bash
# No servidor (/opt/whatsapp-bot)
docker-compose build
docker-compose up -d

# Verificar se está rodando
docker ps | grep whatsapp-bot

# Ver logs
docker logs -f whatsapp-bot

# Testar
curl http://localhost:8000/health
```

---

## 🚀 PASSO 4: TESTAR DEPLOY AUTOMÁTICO

### 4.1 Fazer uma Mudança no Código

```bash
# No seu computador (pasta do projeto)
cd "C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Langcham. fluxo atendimento"

# Fazer uma mudança simples (exemplo)
echo "# Deploy test" >> README.md

# Commit e push
git add .
git commit -m "test: Deploy automático via GitHub Actions"
git push origin main
```

### 4.2 Acompanhar o Deploy

1. Vá no GitHub: `https://github.com/seu-usuario/whatsapp-bot-langchain`
2. Clique na aba **Actions**
3. Você verá o workflow "Deploy to Hetzner" rodando
4. Clique nele para ver os logs em tempo real

### 4.3 Ver Etapas do Deploy

Você verá as seguintes etapas:

```
✅ Checkout code
✅ Setup Python
✅ Validate Python syntax
✅ Deploy to Server
   🚀 Starting deployment...
   📥 Pulling latest changes...
   🔄 Rebuilding Docker image...
   🔄 Restarting container...
   ⏳ Waiting for container to start...
   ✅ Container is running!
   🏥 Checking health...
   🧹 Cleaning up old images...
   🎉 Deployment complete!
✅ Deployment Success
```

### 4.4 Verificar no Servidor

```bash
# No servidor
cd /opt/whatsapp-bot

# Ver se pegou as mudanças
git log --oneline -5

# Ver se container está rodando
docker ps | grep whatsapp-bot

# Ver logs
docker logs --tail 50 whatsapp-bot

# Testar
curl https://bot.seu-dominio.com/health
```

---

## 🎨 WORKFLOW CUSTOMIZADO

O arquivo `.github/workflows/deploy.yml` faz:

### Gatilhos (Quando executa):
```yaml
on:
  push:
    branches:
      - main          # Push na branch main
      - production    # Push na branch production
  workflow_dispatch:  # Botão manual no GitHub
```

### Passos:
1. **Checkout:** Baixa o código
2. **Validate:** Valida sintaxe Python
3. **Deploy:** Conecta SSH e atualiza servidor
4. **Notify:** Notifica sucesso/falha

---

## 🔄 FLUXO DE TRABALHO DIÁRIO

### Desenvolvendo Localmente

```bash
# 1. Fazer mudanças no código
code src/nodes/agent.py

# 2. Testar localmente
python src/main.py

# 3. Commit
git add .
git commit -m "feat: Adiciona nova funcionalidade"

# 4. Push (dispara deploy automático!)
git push origin main

# 5. Aguardar ~2-3 minutos
# GitHub Actions faz o deploy automaticamente

# 6. Verificar no WhatsApp
# Enviar mensagem de teste
```

### Deploy Manual (via GitHub)

1. Vá em **Actions**
2. Selecione "Deploy to Hetzner"
3. Clique em **Run workflow**
4. Selecione a branch
5. Clique em **Run workflow**

---

## 🐛 TROUBLESHOOTING

### Deploy falhou - "Permission denied"

**Problema:** SSH não consegue conectar

**Solução:**
```bash
# Verificar se chave pública está no servidor
ssh root@SEU-IP
cat ~/.ssh/authorized_keys
# Deve conter a chave pública github_deploy.pub

# Testar conexão manualmente
ssh -i ~/.ssh/github_deploy root@SEU-IP
```

### Deploy falhou - "Container failed to start"

**Problema:** Container não iniciou

**Solução:**
```bash
# No servidor
cd /opt/whatsapp-bot
docker logs whatsapp-bot

# Ver erro específico
# Geralmente é:
# - Erro no .env
# - Porta já em uso
# - Erro no código
```

### Deploy falhou - "git pull failed"

**Problema:** Conflito no servidor

**Solução:**
```bash
# No servidor
cd /opt/whatsapp-bot

# Descartar mudanças locais
git reset --hard HEAD
git clean -fd

# Tentar pull novamente
git pull origin main
```

### GitHub Actions não dispara

**Problema:** Workflow não executa

**Solução:**
1. Verificar se arquivo está em `.github/workflows/deploy.yml`
2. Verificar se branch está correta (main ou production)
3. Ver aba Actions > selecionar workflow > Enable workflow

---

## 🔒 SEGURANÇA

### ✅ Boas Práticas

1. **Use repositório privado** para código com lógica de negócio
2. **Nunca commite** .env ou credentials.json
3. **Use secrets do GitHub** para informações sensíveis
4. **Rotacione chaves SSH** periodicamente
5. **Limite acesso** ao repositório (só colaboradores)

### ⚠️ NUNCA Comite:
```
❌ .env
❌ credentials.json
❌ token.json
❌ Chaves SSH (.pem, .key)
❌ Senhas ou tokens
```

O `.gitignore` já protege esses arquivos!

---

## 📊 MONITORAMENTO

### Ver Histórico de Deploys

1. GitHub > **Actions**
2. Ver todos os deploys anteriores
3. Clicar em qualquer um para ver logs
4. Ver duração, status, erros

### Notificações

Configure notificações em:
- GitHub Settings > Notifications
- Receba email quando deploy falhar

### Badges (opcional)

Adicione ao README.md:

```markdown
![Deploy Status](https://github.com/seu-usuario/whatsapp-bot-langchain/actions/workflows/deploy.yml/badge.svg)
```

---

## 🚀 RECURSOS AVANÇADOS

### Deploy em Múltiplos Ambientes

Crie workflows separados:
- `.github/workflows/deploy-staging.yml` (branch develop)
- `.github/workflows/deploy-production.yml` (branch main)

### Testes Automatizados

Adicione antes do deploy:

```yaml
- name: Run Tests
  run: |
    pip install -r requirements.txt
    pytest tests/
```

### Notificação no Slack/Discord

Adicione step:

```yaml
- name: Notify Slack
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

### Rollback Automático

Adicione step para reverter se falhar:

```yaml
- name: Rollback on Failure
  if: failure()
  run: |
    ssh user@server "cd /opt/whatsapp-bot && git checkout HEAD~1 && docker-compose restart"
```

---

## ✅ CHECKLIST FINAL

### GitHub:
- [ ] Repositório criado (privado)
- [ ] Arquivo `.github/workflows/deploy.yml` commitado
- [ ] Secrets configurados (SERVER_HOST, SERVER_USER, SSH_PRIVATE_KEY, etc)
- [ ] Actions habilitadas

### Servidor:
- [ ] Projeto clonado em `/opt/whatsapp-bot`
- [ ] Chave SSH pública adicionada em `~/.ssh/authorized_keys`
- [ ] .env configurado
- [ ] credentials.json copiado
- [ ] Primeiro deploy manual funcionando

### Teste:
- [ ] Push de teste funcionou
- [ ] GitHub Actions executou sem erros
- [ ] Container reiniciou no servidor
- [ ] Bot responde mensagens
- [ ] Health check OK

---

## 🎉 PRONTO!

Agora você tem **deploy automático** via GitHub! 🚀

**Workflow:**
```
Código local → git push → GitHub Actions → Deploy automático → Bot atualizado
```

**Benefícios:**
- ✅ Deploy em 2-3 minutos
- ✅ Sem comandos manuais no servidor
- ✅ Histórico completo de deploys
- ✅ Rollback fácil se necessário
- ✅ Notificações automáticas

**Aproveite!** 🎊

---

## 📚 RECURSOS ADICIONAIS

- [GitHub Actions Docs](https://docs.github.com/en/actions)
- [SSH Action](https://github.com/appleboy/ssh-action)
- [Docker Compose Docs](https://docs.docker.com/compose/)

---

## 🆘 PRECISA DE AJUDA?

### Ver Logs do GitHub Actions
```
GitHub > Actions > Selecionar run > Ver steps
```

### Ver Logs do Servidor
```bash
ssh root@SEU-IP
cd /opt/whatsapp-bot
docker logs -f whatsapp-bot
```

### Testar Conexão SSH
```bash
ssh -i ~/.ssh/github_deploy root@SEU-IP
# Deve conectar sem senha
```

---

**Bom deploy! 🚀**
