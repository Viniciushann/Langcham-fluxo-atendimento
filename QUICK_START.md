# ⚡ QUICK START - Deploy Rápido no Hetzner

## 🚀 Deploy em 5 Minutos

### 1️⃣ Preparar Localmente (2 min)

```bash
# Clonar/baixar projeto
cd "caminho-do-projeto"

# Copiar e configurar .env
cp .env.production .env
# Editar .env com suas credenciais

# Garantir que credentials.json existe
ls credentials.json
```

### 2️⃣ Enviar para Servidor (1 min)

**Opção A - Via Git:**
```bash
git init
git add .
git commit -m "Deploy WhatsApp Bot"
git push origin main
```

**Opção B - Via SCP:**
```bash
tar -czf bot.tar.gz .
scp bot.tar.gz root@SEU-IP-HETZNER:/opt/
```

### 3️⃣ No Servidor Hetzner (1 min)

```bash
ssh root@SEU-IP-HETZNER
cd /opt/whatsapp-bot  # ou descompactar bot.tar.gz
```

### 4️⃣ Portainer (1 min)

1. Abra Portainer
2. **Stacks** → **Add stack**
3. Nome: `whatsapp-bot`
4. Cole o conteúdo de `docker-compose.yml`
5. **Environment variables** → Cole conteúdo de `.env`
6. **Deploy!**

---

## ✅ Verificações

```bash
# 1. Health Check
curl https://bot.seu-dominio.com/health

# 2. Logs
docker logs -f whatsapp-bot

# 3. Testar
# Envie mensagem WhatsApp para o bot
```

---

## 📝 Credenciais Necessárias

- [ ] WHATSAPP_API_KEY
- [ ] OPENAI_API_KEY
- [ ] SUPABASE_KEY
- [ ] POSTGRES_CONNECTION_STRING
- [ ] SECRET_KEY
- [ ] credentials.json
- [ ] DNS configurado

---

**Total: ~5 minutos! 🎉**
