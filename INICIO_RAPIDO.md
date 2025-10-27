# 🚀 Início Rápido - 3 Passos

## ⚡ Comandos Essenciais

### 1️⃣ Iniciar Servidor FastAPI

**Windows (duplo clique):**
```
start_server.bat
```

**Ou via comando:**
```bash
cd "C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Langcham. fluxo atendimento"
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

✅ **Verificar:** Acesse http://localhost:8000/health

---

### 2️⃣ Iniciar ngrok (NOVO TERMINAL)

```bash
ngrok http 8000
```

📝 **COPIE a URL:** `https://xxxx-xxx-xxx.ngrok-free.app`

✅ **Verificar:** Acesse http://localhost:4040

---

### 3️⃣ Configurar Webhook (NOVO TERMINAL)

```bash
python configure_webhook.py
```

Cole a URL do ngrok quando solicitado!

---

## 📱 Enviar Mensagem de Teste

### Opção 1: Via WhatsApp (Real)

No seu celular, envie mensagem para:
**+55 62 92745972**

Exemplo: `Olá, preciso de orçamento de drywall`

### Opção 2: Via Script

```bash
python test_mensagem.py
```

---

## 🔍 Monitorar

1. **FastAPI Logs:** Terminal onde rodou `uvicorn`
2. **ngrok Web:** http://localhost:4040
3. **Supabase:** Dashboard do Supabase para ver clientes cadastrados

---

## 📊 Estrutura dos Terminais

```
Terminal 1: FastAPI Server
> uvicorn src.main:app --reload

Terminal 2: ngrok Tunnel
> ngrok http 8000

Terminal 3: Scripts de Teste
> python configure_webhook.py
> python test_mensagem.py
```

---

## ✅ Checklist Rápido

- [ ] FastAPI rodando → http://localhost:8000/health
- [ ] ngrok rodando → http://localhost:4040
- [ ] Webhook configurado → `python configure_webhook.py`
- [ ] Mensagem enviada → Via WhatsApp ou script
- [ ] Logs aparecem → Verificar terminal FastAPI
- [ ] Resposta recebida → WhatsApp do cliente

---

## 🆘 Problemas Comuns

**FastAPI não inicia:**
```bash
pip install fastapi uvicorn
```

**ngrok não funciona:**
- Baixe em: https://ngrok.com/download
- Ou via choco: `choco install ngrok`

**Webhook não recebe:**
- Verifique se ngrok está rodando
- Verifique URL no script configure_webhook.py
- Veja logs no http://localhost:4040

---

## 📖 Documentação Completa

Para guia detalhado, veja: **GUIA_TESTE.md**

---

**Pronto! Agora é só testar! 🎉**
