# 🔧 CORRIGIR WEBHOOK - PROBLEMA IDENTIFICADO

## ❌ PROBLEMA

O webhook está configurado com URL incorreta:
```
ERRADO: https://bot.automacaovn.shop/webhook
CERTO:  https://bot.automacaovn.shop/webhook/whatsapp
```

Por isso o bot recebe a mensagem mas não processa (Event: unknown).

---

## ✅ SOLUÇÃO RÁPIDA (2 minutos)

### OPÇÃO 1: Via Curl (Mais Rápido)

Conecte no servidor e execute:

```bash
# Conectar no servidor
ssh root@46.62.155.254

# Executar o comando de correção
curl -X POST "https://evolution.centrooestedrywalldry.com.br/webhook/set/Centro_oeste_draywal" \
  -H "Content-Type: application/json" \
  -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9" \
  -d '{
    "enabled": true,
    "url": "https://bot.automacaovn.shop/webhook/whatsapp",
    "webhookByEvents": false,
    "webhookBase64": true,
    "events": [
      "MESSAGES_UPSERT",
      "MESSAGES_UPDATE",
      "SEND_MESSAGE"
    ]
  }'

# Verificar se aplicou
curl -X GET "https://evolution.centrooestedrywalldry.com.br/webhook/find/Centro_oeste_draywal" \
  -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9"
```

**Deve retornar:**
```json
{
  "url": "https://bot.automacaovn.shop/webhook/whatsapp",
  "enabled": true,
  "webhookBase64": true
}
```

---

### OPÇÃO 2: Via Script Python (no servidor)

```bash
# Conectar no servidor
ssh root@46.62.155.254

# Navegar para o projeto
cd /opt/whatsapp-bot

# Criar script temporário
cat > fix_webhook.py << 'EOF'
import requests

EVOLUTION_URL = "https://evolution.centrooestedrywalldry.com.br"
API_KEY = "8773E1C40430-4626-B896-1302789BA4D9"
INSTANCE = "Centro_oeste_draywal"
WEBHOOK_URL = "https://bot.automacaovn.shop/webhook/whatsapp"

headers = {
    "Content-Type": "application/json",
    "apikey": API_KEY
}

payload = {
    "enabled": True,
    "url": WEBHOOK_URL,
    "webhookByEvents": False,
    "webhookBase64": True,
    "events": ["MESSAGES_UPSERT", "MESSAGES_UPDATE", "SEND_MESSAGE"]
}

url = f"{EVOLUTION_URL}/webhook/set/{INSTANCE}"
response = requests.post(url, json=payload, headers=headers)

print(f"Status: {response.status_code}")
print(f"Resposta: {response.json()}")
EOF

# Executar
python3 fix_webhook.py

# Remover script temporário
rm fix_webhook.py
```

---

## 🔍 VERIFICAR SE FUNCIONOU

Após executar uma das opções acima:

### 1. Verificar configuração no Evolution

```bash
curl -X GET "https://evolution.centrooestedrywalldry.com.br/webhook/find/Centro_oeste_draywal" \
  -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9"
```

Deve mostrar: `"url": "https://bot.automacaovn.shop/webhook/whatsapp"`

### 2. Ver logs do bot

```bash
ssh root@46.62.155.254
docker logs -f whatsapp-bot --tail 50
```

### 3. Enviar mensagem de teste

Envie para **+55 62 9274-5972**:
```
Oi, teste
```

### 4. Verificar logs (deve aparecer)

```
📨 Webhook recebido!
Event: messages.upsert
Instance: Centro_oeste_draywal
✅ Processando mensagem...
```

Se aparecer `Event: unknown` ainda, é problema diferente.

---

## ⚠️ PROBLEMA ADICIONAL: CERTIFICADO SSL

Você também tem erro de certificado auto-assinado:
```
ERROR: self-signed certificate; DEPTH_ZERO_SELF_SIGNED_CERT
```

### Solução Temporária (para testar):

No servidor, edite a Evolution API para aceitar certificados auto-assinados:

```bash
# Se estiver usando Docker da Evolution
ssh root@46.62.155.254

# Adicionar variável de ambiente
docker exec -it evolution-api sh -c 'export NODE_TLS_REJECT_UNAUTHORIZED=0'
```

**OU**

Configure certificado válido do Let's Encrypt no Traefik para `bot.automacaovn.shop`.

---

## 🎯 COMANDOS PRONTOS (COPIE E COLE)

```bash
# 1. Conectar no servidor
ssh root@46.62.155.254

# 2. Corrigir webhook
curl -X POST "https://evolution.centrooestedrywalldry.com.br/webhook/set/Centro_oeste_draywal" -H "Content-Type: application/json" -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9" -d '{"enabled": true, "url": "https://bot.automacaovn.shop/webhook/whatsapp", "webhookByEvents": false, "webhookBase64": true, "events": ["MESSAGES_UPSERT", "MESSAGES_UPDATE", "SEND_MESSAGE"]}'

# 3. Verificar
curl -X GET "https://evolution.centrooestedrywalldry.com.br/webhook/find/Centro_oeste_draywal" -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9"

# 4. Ver logs do bot
docker logs -f whatsapp-bot --tail 50

# 5. Enviar mensagem de teste para +55 62 9274-5972
```

---

## ✅ PRONTO!

Após executar os comandos acima, o bot deve começar a responder mensagens corretamente.

Se ainda não funcionar, verifique:
1. Container está rodando: `docker ps | grep whatsapp-bot`
2. Logs do bot: `docker logs whatsapp-bot`
3. Certificado SSL: configure Let's Encrypt ou desabilite validação
