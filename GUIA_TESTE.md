# 🚀 Guia Completo de Teste - WhatsApp Bot

## 📋 Pré-requisitos Verificados

✅ FastAPI instalado
✅ ngrok instalado
✅ Evolution API configurada: `https://evolution.centrooestedrywalldry.com.br`
✅ Instância WhatsApp: `Centro Oeste Drywall`
✅ Bot Phone: `556292745972`
✅ OpenAI API Key configurada
✅ Supabase configurado

---

## 🔧 Passo 1: Iniciar o Servidor FastAPI

### Opção A: Modo Desenvolvimento (com reload)

```bash
cd "C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Langcham. fluxo atendimento"
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Opção B: Modo Produção

```bash
cd "C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Langcham. fluxo atendimento"
uvicorn src.main:app --host 0.0.0.0 --port 8000 --workers 1
```

**Aguarde a mensagem:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**Teste se está funcionando:**
- Abra navegador: http://localhost:8000
- Deve retornar: `{"status": "running", ...}`

---

## 🌐 Passo 2: Configurar ngrok Tunnel

Em um **NOVO terminal/prompt**, execute:

```bash
ngrok http 8000
```

**Você verá algo assim:**
```
Session Status                online
Account                       seu-email@gmail.com
Version                       3.x.x
Region                        United States (us)
Latency                       -
Web Interface                 http://127.0.0.1:4040
Forwarding                    https://xxxx-xxx-xxx-xxx.ngrok-free.app -> http://localhost:8000
```

**📝 COPIE A URL DO FORWARDING!**

Exemplo: `https://a1b2-123-456-789-012.ngrok-free.app`

**IMPORTANTE:** Mantenha este terminal aberto!

---

## 🔗 Passo 3: Configurar Webhook na Evolution API

### Opção A: Via Interface Web da Evolution API

1. Acesse: https://evolution.centrooestedrywalldry.com.br/manager
2. Login com suas credenciais
3. Vá para a instância: **Centro Oeste Drywall**
4. Configurações → Webhooks
5. Configure:
   - **URL do Webhook:** `https://SUA-URL-NGROK.ngrok-free.app/webhook/whatsapp`
   - **Eventos:** Marque `messages.upsert`
   - **Ativo:** SIM

### Opção B: Via API (cURL)

```bash
curl -X POST "https://evolution.centrooestedrywalldry.com.br/webhook/set/Centro Oeste Drywall" \
  -H "Content-Type: application/json" \
  -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9" \
  -d '{
    "enabled": true,
    "url": "https://SUA-URL-NGROK.ngrok-free.app/webhook/whatsapp",
    "webhook_by_events": false,
    "events": [
      "MESSAGES_UPSERT"
    ]
  }'
```

**Substitua:** `SUA-URL-NGROK.ngrok-free.app` pela URL do ngrok do Passo 2

### Verificar Webhook Configurado

```bash
curl -X GET "https://evolution.centrooestedrywalldry.com.br/webhook/find/Centro Oeste Drywall" \
  -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9"
```

---

## 📱 Passo 4: Enviar Mensagem de Teste

### Método 1: Via WhatsApp (Recomendado)

1. No seu celular, abra o WhatsApp
2. Envie mensagem para o número do bot: **+55 62 92745972**
3. Digite: `Olá, preciso de informações sobre instalação de drywall`

### Método 2: Via Evolution API (Simulação)

```bash
curl -X POST "https://evolution.centrooestedrywalldry.com.br/message/sendText/Centro Oeste Drywall" \
  -H "Content-Type: application/json" \
  -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9" \
  -d '{
    "number": "556299999999",
    "text": "Olá, preciso de informações sobre instalação de drywall"
  }'
```

**OBS:** O número acima é exemplo. Use um número WhatsApp real para teste.

---

## 🔍 Passo 5: Monitorar Logs

### Terminal 1 (FastAPI)

Você verá logs como:

```
INFO: 📨 Webhook recebido!
INFO: Event: messages.upsert
INFO: Instance: Centro Oeste Drywall
INFO: ============================================================
INFO: Iniciando validação do webhook
INFO: ============================================================
INFO: Webhook recebido:
INFO:   Remote JID: 5562999999999@s.whatsapp.net
INFO:   From Me: False
INFO:   Message Type: conversation
INFO:   Push Name: Cliente Teste
INFO: ============================================================
INFO: Verificando cliente no banco de dados
INFO: ============================================================
...
```

### Terminal 2 (ngrok)

Acesse: http://localhost:4040

Você verá todas as requisições HTTP recebidas!

---

## 🧪 Passo 6: Testar Endpoints Manualmente

### Health Check

```bash
curl http://localhost:8000/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-21T...",
  "environment": "development",
  "whatsapp_instance": "Centro Oeste Drywall",
  "services": {
    "fastapi": "✅ Running",
    "whatsapp_api": "✅ Configured",
    "openai": "✅ Configured",
    "supabase": "✅ Configured"
  }
}
```

### Status do Bot

```bash
curl http://localhost:8000/status
```

### Test Message (Endpoint Direto)

```bash
curl -X POST "http://localhost:8000/test/message?telefone=5562999999999&mensagem=Teste%20de%20mensagem"
```

---

## 🐛 Troubleshooting

### Problema 1: "Connection refused" no webhook

**Causa:** FastAPI não está rodando ou ngrok não está configurado

**Solução:**
1. Verifique se FastAPI está rodando: `curl http://localhost:8000`
2. Verifique se ngrok está rodando: acesse http://localhost:4040

### Problema 2: Webhook não recebe mensagens

**Causa:** Webhook não configurado corretamente na Evolution API

**Solução:**
```bash
# Verificar webhook atual
curl -X GET "https://evolution.centrooestedrywalldry.com.br/webhook/find/Centro Oeste Drywall" \
  -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9"
```

### Problema 3: Erro "OpenAI API key invalid"

**Causa:** OpenAI API Key expirada ou inválida

**Solução:**
1. Gere nova API key em: https://platform.openai.com/api-keys
2. Atualize no `.env`: `OPENAI_API_KEY=sk-proj-...`
3. Reinicie o FastAPI

### Problema 4: Erro no Supabase

**Causa:** Credenciais inválidas ou tabela não existe

**Solução:**
1. Verifique se a tabela `clientes` existe no Supabase
2. Execute o SQL de criação de tabelas (se necessário)

---

## 📊 Monitorar via ngrok Web Interface

Acesse: **http://localhost:4040**

Você verá:
- ✅ Todas as requisições HTTP recebidas
- ✅ Body das requisições
- ✅ Headers
- ✅ Respostas
- ✅ Tempo de processamento

Muito útil para debug!

---

## 🎯 Fluxo Esperado (Happy Path)

```
1. Cliente envia mensagem via WhatsApp
   ↓
2. Evolution API recebe a mensagem
   ↓
3. Evolution API envia webhook para ngrok
   ↓
4. ngrok encaminha para FastAPI (localhost:8000)
   ↓
5. FastAPI valida webhook
   ↓
6. Verifica/cadastra cliente no Supabase
   ↓
7. Processa mídia (texto/áudio/imagem)
   ↓
8. Invoca agente OpenAI com RAG
   ↓
9. Fragmenta resposta
   ↓
10. Envia resposta via Evolution API
    ↓
11. Cliente recebe resposta no WhatsApp ✅
```

---

## 📝 Comandos Úteis em Resumo

```bash
# Terminal 1: FastAPI
cd "C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Langcham. fluxo atendimento"
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: ngrok
ngrok http 8000

# Terminal 3: Testar health
curl http://localhost:8000/health

# Configurar webhook (substitua URL_NGROK)
curl -X POST "https://evolution.centrooestedrywalldry.com.br/webhook/set/Centro Oeste Drywall" \
  -H "Content-Type: application/json" \
  -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9" \
  -d '{
    "enabled": true,
    "url": "https://URL_NGROK.ngrok-free.app/webhook/whatsapp",
    "events": ["MESSAGES_UPSERT"]
  }'
```

---

## ✅ Checklist de Teste

- [ ] FastAPI rodando (http://localhost:8000)
- [ ] ngrok tunnel ativo (https://....ngrok-free.app)
- [ ] Webhook configurado na Evolution API
- [ ] Health check OK (200)
- [ ] Mensagem enviada via WhatsApp
- [ ] Logs aparecem no terminal FastAPI
- [ ] Requisição aparece no ngrok (http://localhost:4040)
- [ ] Cliente cadastrado no Supabase
- [ ] Resposta enviada de volta
- [ ] Cliente recebe resposta no WhatsApp

---

## 🎉 Pronto para Testar!

Agora execute os passos 1-5 na ordem e monitore os logs! 🚀
