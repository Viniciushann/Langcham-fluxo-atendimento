# CONFIGURAR WEBHOOK DA EVOLUTION API

Data: 2025-10-27
IMPORTANTE: O bot esta rodando mas o webhook NAO esta configurado!

---

## PROBLEMA ATUAL

As mensagens que voce envia no WhatsApp:
- NAO estao chegando no bot (nenhuma requisicao nos logs)
- Estao chegando no Supabase (provavelmente por outro webhook antigo)
- MAS o bot nao processa porque nao recebe via webhook

---

## SOLUCAO: Configurar Webhook na Evolution API

### Passo 1: Descobrir sua URL publica

O bot esta rodando em:
- **Servidor local:** http://localhost:8001
- **Rede local:** http://SEU-IP-LOCAL:8001

Para o webhook funcionar, voce precisa de uma URL PUBLICA. Opcoes:

#### Opcao A: ngrok (RECOMENDADO para teste rapido)

1. Baixe ngrok: https://ngrok.com/download
2. Execute:
   ```bash
   ngrok http 8001
   ```
3. Copie a URL que aparece (ex: https://abc123.ngrok.io)
4. Sua URL do webhook sera: `https://abc123.ngrok.io/webhook/whatsapp`

#### Opcao B: Servidor com IP publico

Se o bot esta rodando em um servidor com IP publico:
- URL: `http://SEU-IP-PUBLICO:8001/webhook/whatsapp`

#### Opcao C: Localtunnel (alternativa gratuita)

```bash
npm install -g localtunnel
lt --port 8001
```

---

### Passo 2: Configurar na Evolution API

Voce precisa acessar o painel da Evolution API e configurar o webhook.

**URL da Evolution API:**
Verifique no .env a variavel `WHATSAPP_API_URL`

**Passos:**

1. Acesse o painel da Evolution API
2. Va em: **Webhooks** ou **Configuracoes** ou **Settings**
3. Encontre a instancia: **Centro_oeste_draywal**
4. Configure:

   **URL do Webhook:**
   ```
   https://SUA-URL-PUBLICA/webhook/whatsapp
   ```

   **Eventos (Events):**
   - `messages.upsert` (OBRIGATORIO)
   - Ou marque todos relacionados a mensagens

   **Metodo:**
   - POST

   **Headers (opcional):**
   - Content-Type: application/json

5. **Salve e HABILITE o webhook**

---

### Passo 3: Testar Webhook Manualmente

Execute este comando para simular uma mensagem chegando:

```bash
curl -X POST http://localhost:8001/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "instance": "Centro_oeste_draywal",
    "data": {
      "key": {
        "remoteJid": "5562999999999@s.whatsapp.net",
        "fromMe": false,
        "id": "TEST123"
      },
      "message": {
        "conversation": "Teste de webhook - quanto custa drywall?"
      },
      "messageType": "conversation",
      "pushName": "Teste Manual",
      "messageTimestamp": 1234567890
    }
  }'
```

**Resposta esperada:**
```json
{
  "status": "received",
  "message": "Webhook processado com sucesso"
}
```

Se isso funcionar, o problema e APENAS a configuracao do webhook na Evolution API.

---

### Passo 4: Verificar se Webhook Esta Chegando

Deixe o bot rodando e envie uma mensagem de teste no WhatsApp. Depois veja os logs:

```bash
tail -f bot.log
```

**Deve aparecer:**
```
INFO - Webhook recebido!
INFO - Event: messages.upsert
INFO - Mensagem adicionada a fila de processamento
INFO - Buscando cliente com telefone: 5562...
INFO - Processando mensagem via GRAFO
```

Se nao aparecer NADA, o webhook nao esta chegando.

---

## VERIFICAR CONFIGURACAO ATUAL DO WEBHOOK

### Via API da Evolution (se tiver acesso)

```bash
curl -X GET "https://SUA-EVOLUTION-API/webhook/Centro_oeste_draywal" \
  -H "apikey: SUA-API-KEY"
```

### Via Painel Web

1. Acesse o painel da Evolution API
2. Va em Webhooks
3. Veja se a URL esta configurada
4. Veja se esta HABILITADO (enabled/ativo)

---

## PROBLEMAS COMUNS

### 1. Webhook desabilitado
**Solucao:** Habilitar no painel da Evolution API

### 2. URL incorreta
**Solucao:** Verificar se a URL aponta para o bot rodando (porta 8001)

### 3. Firewall bloqueando
**Solucao:**
- Verificar firewall do Windows
- Verificar firewall do servidor
- Verificar regras de rede

### 4. Bot nao esta rodando
**Solucao:**
```bash
curl http://localhost:8001/health
```
Deve retornar: `{"status":"healthy",...}`

### 5. Porta errada
**Solucao:** Bot esta na porta 8001, nao 8000!

---

## SCRIPT PARA TESTAR CONEXAO

Criei um script Python para testar tudo:

```bash
python testar_webhook.py
```

Ele vai:
1. Verificar se o bot esta rodando
2. Testar endpoint de webhook
3. Simular mensagem chegando
4. Mostrar se funcionou

---

## FLUXO COMPLETO (Como Deve Funcionar)

1. **Usuario envia mensagem no WhatsApp**
   - Para o numero: +55 62 9274-5972

2. **Evolution API recebe a mensagem**
   - Via API do WhatsApp Business

3. **Evolution API envia webhook para o bot**
   - POST para: http://SUA-URL:8001/webhook/whatsapp
   - Com dados da mensagem

4. **Bot recebe o webhook**
   - Valida a mensagem
   - Verifica/cadastra cliente no Supabase
   - Processa com o agente de IA
   - Gera resposta

5. **Bot envia resposta**
   - Via Evolution API
   - De volta para o WhatsApp do usuario

**ATUALMENTE:** O passo 3 NAO esta acontecendo!

---

## PROXIMOS PASSOS IMEDIATOS

1. **Configure o ngrok:**
   ```bash
   ngrok http 8001
   ```

2. **Copie a URL do ngrok:**
   ```
   https://abc123.ngrok.io
   ```

3. **Configure na Evolution API:**
   ```
   https://abc123.ngrok.io/webhook/whatsapp
   ```

4. **Envie mensagem de teste no WhatsApp**

5. **Veja se bot responde!**

---

**IMPORTANTE:** Sem o webhook configurado corretamente, o bot NUNCA vai receber as mensagens e NUNCA vai responder!

---

Criado: 2025-10-27
Versao: 1.0
