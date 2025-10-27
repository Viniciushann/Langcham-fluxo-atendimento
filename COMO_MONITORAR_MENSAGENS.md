# 📱 Como Monitorar Mensagens do WhatsApp Bot

Guia completo para verificar se as mensagens estão chegando e sendo processadas.

---

## 🎯 Locais para Verificar Mensagens

### 1️⃣ **Supabase (Banco de Dados)**

Aqui ficam TODAS as mensagens recebidas:

**Acesso:**
```
https://znyypdwnqdlvqwwvffzk.supabase.co
```

**Passos:**
1. Faça login no Supabase
2. Vá em: **Table Editor**
3. Selecione: **leads**
4. Você verá todas as mensagens recebidas

**Colunas importantes:**
- `nome_Leed`: Nome do cliente
- `phone_numero`: Telefone do cliente
- `message`: Conteúdo da mensagem
- `created_at`: Data/hora que chegou
- `wpp.TipoDeMensagem`: Tipo (texto, áudio, imagem)

---

### 2️⃣ **Script de Monitoramento (Python)**

Criei um script para você monitorar facilmente!

**Execute:**
```bash
python monitorar_mensagens.py
```

**Menu de opções:**
```
1. Ver ultimas mensagens recebidas
2. Ver logs do sistema
3. Ver configuracao do webhook
4. Modo monitoramento continuo (atualiza a cada 5s)
5. Ver tudo (opcoes 1, 2 e 3)
```

**Exemplo de saída:**
```
[1] 27/10/2025 10:15:34
    Nome: Cliente Teste
    Telefone: 556299999999
    Mensagem: Ola! Quanto custa drywall?

[2] 22/10/2025 12:55:01
    Nome: Wladmyr Cintra
    Telefone: 14372591659
    Mensagem: Olá! Gostaria de solicitar um orçamento.
```

---

### 3️⃣ **Logs do Sistema (bot.log)**

O bot gera logs automáticos de tudo que acontece.

**Ver logs:**
```bash
# Últimas 20 linhas
tail -20 bot.log

# No Windows (PowerShell)
Get-Content bot.log -Tail 20

# Acompanhar em tempo real
tail -f bot.log
```

**Ou use o monitor:**
```bash
python monitorar_mensagens.py
# Escolha opção 2
```

**O que aparece nos logs:**
- ✅ Webhook recebido
- ✅ Cliente verificado/cadastrado
- ✅ Mensagem processada
- ✅ Resposta enviada
- ❌ Erros (se houver)

---

### 4️⃣ **API FastAPI (Endpoints)**

Se o bot estiver rodando, você pode verificar via API:

**Iniciar o bot:**
```bash
python src/main.py
```

**Endpoints disponíveis:**

#### Health Check
```bash
curl http://localhost:8000/health
```

Resposta:
```json
{
  "status": "healthy",
  "timestamp": "2025-10-27T10:15:34",
  "whatsapp_instance": "Centro_oeste_draywal",
  "bot_number": "556292745972"
}
```

#### Status do Bot
```bash
curl http://localhost:8000/status
```

#### Documentação da API
```
http://localhost:8000/docs
```

---

## 🔍 Verificar se Mensagens Estão Chegando

### Método 1: Rápido (Script Python)

```bash
python monitorar_mensagens.py
# Escolha: 1 (Ver ultimas mensagens)
```

### Método 2: Supabase Web

1. Acesse: https://znyypdwnqdlvqwwvffzk.supabase.co
2. Table Editor → `leads`
3. Ordene por `created_at` (mais recente primeiro)
4. Veja as últimas mensagens

### Método 3: SQL Query no Supabase

```sql
-- Últimas 10 mensagens
SELECT
    nome_Leed,
    phone_numero,
    message,
    created_at
FROM leads
ORDER BY created_at DESC
LIMIT 10;
```

---

## 📊 Status Atual das Mensagens

Baseado no último check:

```
✅ Total de mensagens no sistema: 10+
✅ Última mensagem: 22/10/2025 12:55:01
✅ Sistema está recebendo mensagens
✅ Banco de dados funcionando
```

**Últimas mensagens detectadas:**
1. **Cliente Teste** (5562999999999) - "Teste"
2. **Cliente Teste** (556299999999) - "Ola! Quanto custa drywall?"
3. **Wladmyr Cintra** (14372591659) - "Olá! Gostaria de solicitar um orçamento."

---

## 🚀 Monitoramento em Tempo Real

Para ver mensagens chegando ao vivo:

```bash
python monitorar_mensagens.py
# Escolha: 4 (Modo monitoramento continuo)
```

**O que vai aparecer:**
```
[10:15:34] Aguardando... (ultima: 607bc40a...)
[10:15:39] Aguardando... (ultima: 607bc40a...)
[10:15:44] NOVA MENSAGEM!
  De: João Silva (5562988887777)
  Mensagem: Quero um orçamento de drywall
[10:15:49] Aguardando... (ultima: 8f3a2b1c...)
```

Pressione `Ctrl+C` para parar.

---

## 🔧 Configuração do Webhook

Para que as mensagens cheguem, o webhook precisa estar configurado na Evolution API.

### Verificar Configuração Atual

```bash
python monitorar_mensagens.py
# Escolha: 3 (Ver configuracao do webhook)
```

### Configurar Webhook na Evolution API

**URL do Webhook:**
```
http://SEU-IP:8000/webhook/whatsapp
```

**Passos:**
1. Acesse seu painel da Evolution API
2. Vá em: **Webhooks** ou **Configurações**
3. Configure:
   - **URL**: `http://SEU-IP-PUBLICO:8000/webhook/whatsapp`
   - **Eventos**: `messages.upsert`
   - **Método**: `POST`
4. Salve e habilite

**Testar Webhook:**
```bash
curl -X POST http://localhost:8000/webhook/whatsapp \
  -H "Content-Type: application/json" \
  -d '{
    "event": "messages.upsert",
    "data": {
      "key": {
        "remoteJid": "5562999999999@s.whatsapp.net",
        "fromMe": false
      },
      "message": {
        "conversation": "Teste de mensagem"
      },
      "messageType": "conversation",
      "pushName": "Teste"
    }
  }'
```

---

## 📝 Logs Importantes

### Quando uma mensagem chega:

```
INFO - 📨 Webhook recebido!
INFO - Event: messages.upsert
INFO - 🚀 Mensagem adicionada à fila de processamento
INFO - Buscando cliente com telefone: 5562999999999
INFO - Cliente encontrado: 607bc40a-49c2-4a9a-8734-a706dd212c29
INFO - Processando mensagem via GRAFO
```

### Se tiver erro:

```
WARNING - ⚠️ Webhook sem dados
ERROR - ❌ Erro no webhook: [detalhes do erro]
```

---

## 🐛 Problemas Comuns

### Mensagens não aparecem no Supabase

**Possíveis causas:**
1. Webhook não configurado na Evolution API
2. Bot não está rodando (`python src/main.py`)
3. Firewall bloqueando requisições
4. URL do webhook incorreta

**Solução:**
```bash
# 1. Verificar se bot está rodando
curl http://localhost:8000/health

# 2. Ver logs de erro
tail -50 bot.log | grep ERROR

# 3. Testar webhook manualmente (ver comando acima)
```

### Mensagens aparecem mas bot não responde

**Verificar:**
1. OpenAI API Key configurada
2. Redis rodando
3. Logs de erro: `tail -50 bot.log`

---

## ✅ Checklist de Monitoramento

Use isso para verificar se tudo está funcionando:

- [ ] Bot rodando: `curl http://localhost:8000/health`
- [ ] Webhook configurado na Evolution API
- [ ] Redis rodando: `redis-cli ping`
- [ ] Mensagens chegando no Supabase
- [ ] Logs sem erros: `tail bot.log`
- [ ] Script monitor funcionando: `python monitorar_mensagens.py`

---

## 📱 Testar Agora

### Teste rápido:

1. Execute o monitor:
   ```bash
   python monitorar_mensagens.py
   # Escolha: 1
   ```

2. Veja se aparecem mensagens

3. Se SIM → ✅ Sistema funcionando!

4. Se NÃO → Configure o webhook da Evolution API

---

## 🆘 Suporte

Se nenhuma mensagem aparecer:

1. Verifique configuração do webhook
2. Veja os logs: `tail -50 bot.log`
3. Teste o endpoint: `curl http://localhost:8000/health`
4. Execute: `python monitorar_mensagens.py` (opção 5 - ver tudo)

---

**Criado:** 2025-10-27
**Versão:** 1.0
