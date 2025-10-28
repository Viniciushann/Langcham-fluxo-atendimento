# 🤖 GitHub Actions - Deploy Automático

## ✅ O que já está configurado

O workflow do GitHub Actions já está criado em `.github/workflows/deploy.yml`.

Ele faz deploy automático quando você:
- Faz push na branch `main` ou `production`
- Clica em "Run workflow" manualmente no GitHub

---

## 🔐 Passo 1: Configurar Secrets no GitHub

Você precisa adicionar as credenciais SSH no GitHub para que ele consiga acessar seu servidor Hetzner.

### 1.1 Gerar chave SSH (se ainda não tem)

No seu computador local (Windows), abra o PowerShell:

```powershell
# Gerar chave SSH
ssh-keygen -t ed25519 -C "github-actions-deploy"

# Salvar em: C:\Users\Vinicius Soutenio\.ssh\id_ed25519_github
# Deixe a senha em branco (apenas Enter)
```

### 1.2 Copiar chave pública para o servidor Hetzner

```powershell
# Ver a chave pública
cat C:\Users\Vinicius Soutenio\.ssh\id_ed25519_github.pub

# Copiar o conteúdo (começa com "ssh-ed25519...")
```

No servidor Hetzner via SSH:

```bash
ssh root@46.62.155.254

# Adicionar a chave pública
echo "ssh-ed25519 AAA... github-actions-deploy" >> ~/.ssh/authorized_keys

# Ajustar permissões
chmod 600 ~/.ssh/authorized_keys
```

### 1.3 Adicionar Secrets no GitHub

1. Acesse seu repositório: https://github.com/Viniciushann/Langcham-fluxo-atendimento
2. Vá em **Settings** → **Secrets and variables** → **Actions**
3. Clique em **New repository secret**

Adicione estes 4 secrets:

#### Secret 1: `SERVER_HOST`
```
Valor: 46.62.155.254
```

#### Secret 2: `SERVER_USER`
```
Valor: root
```

#### Secret 3: `SSH_PRIVATE_KEY`
```powershell
# No PowerShell do Windows, copie o conteúdo:
cat C:\Users\Vinicius Soutenio\.ssh\id_ed25519_github
```
Cole TODO o conteúdo (incluindo as linhas `-----BEGIN` e `-----END`)

#### Secret 4: `SERVER_PORT` (opcional)
```
Valor: 22
```

#### Secret 5: `DOMAIN` (opcional)
```
Valor: automacaovn.shop
```

---

## 🚀 Passo 2: Testar o Deploy Automático

### Opção A: Fazer um push qualquer

```bash
cd "C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Langcham. fluxo atendimento"

# Fazer uma mudança simples
echo "# Deploy automático configurado" >> README.md

# Commit e push
git add README.md
git commit -m "Test: GitHub Actions deploy"
git push
```

### Opção B: Executar manualmente

1. Vá em: https://github.com/Viniciushann/Langcham-fluxo-atendimento/actions
2. Clique em "Deploy to Hetzner"
3. Clique em "Run workflow"
4. Selecione a branch `main`
5. Clique em "Run workflow"

---

## 📊 Passo 3: Acompanhar o Deploy

1. Acesse: https://github.com/Viniciushann/Langcham-fluxo-atendimento/actions
2. Clique no workflow que está rodando
3. Veja os logs em tempo real

O deploy deve:
1. ✅ Fazer checkout do código
2. ✅ Validar sintaxe Python
3. ✅ Conectar via SSH no servidor
4. ✅ Fazer git pull
5. ✅ Rebuild da imagem Docker
6. ✅ Restart do container
7. ✅ Verificar health check
8. ✅ Limpar imagens antigas

---

## 🎯 Como funciona

```
┌─────────────────────────────────────────────────┐
│  Você faz:                                       │
│  git push                                        │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  GitHub Actions detecta push na branch main     │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  GitHub Actions conecta no servidor via SSH     │
│  usando as credenciais dos Secrets              │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Servidor Hetzner (46.62.155.254)               │
│  1. cd /opt/whatsapp-bot                        │
│  2. git pull origin main                         │
│  3. docker-compose build                         │
│  4. docker-compose up -d                         │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│  Bot reiniciado com novo código! 🎉              │
└─────────────────────────────────────────────────┘
```

---

## 🔧 Troubleshooting

### Erro: "Permission denied (publickey)"

**Causa:** A chave SSH não foi adicionada corretamente ao servidor.

**Solução:**
```bash
ssh root@46.62.155.254
cat ~/.ssh/authorized_keys
# Verificar se a chave do GitHub Actions está lá
```

### Erro: "Container failed to start"

**Causa:** Erro no código ou falta de variáveis de ambiente.

**Solução:**
```bash
ssh root@46.62.155.254
cd /opt/whatsapp-bot
docker-compose logs --tail 50
```

### Erro: "git pull failed"

**Causa:** O repositório no servidor está desatualizado ou tem conflitos.

**Solução:**
```bash
ssh root@46.62.155.254
cd /opt/whatsapp-bot
git status
git reset --hard origin/main
```

---

## ✅ Checklist de Configuração

- [ ] Chave SSH gerada
- [ ] Chave pública adicionada ao servidor Hetzner
- [ ] Secret `SERVER_HOST` adicionado no GitHub (46.62.155.254)
- [ ] Secret `SERVER_USER` adicionado no GitHub (root)
- [ ] Secret `SSH_PRIVATE_KEY` adicionado no GitHub
- [ ] Secret `SERVER_PORT` adicionado no GitHub (22)
- [ ] Secret `DOMAIN` adicionado no GitHub
- [ ] Workflow testado com sucesso
- [ ] Bot funcionando após deploy

---

## 🎉 Resultado Final

Agora sempre que você fizer:

```bash
git add .
git commit -m "Sua mensagem"
git push
```

O GitHub Actions vai automaticamente:
1. Detectar o push
2. Conectar no servidor Hetzner
3. Atualizar o código
4. Rebuild do Docker
5. Reiniciar o bot

**Tudo automático! Sem precisar fazer SSH manualmente!**

---

## 📞 Próximos Passos

1. Configure os secrets seguindo as instruções acima
2. Faça um commit de teste
3. Acompanhe o deploy no GitHub Actions
4. Se der erro, verifique a seção de Troubleshooting

Dúvidas? Consulte: https://docs.github.com/actions
