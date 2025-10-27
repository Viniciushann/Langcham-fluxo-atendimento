# PROBLEMA IDENTIFICADO: Bot NAO esta rodando!

## Por que o bot nao responde?

**DIAGNOSTICO:**
- Mensagens ESTAO chegando no banco de dados (confirmado)
- Webhook da Evolution API esta funcionando
- **MAS o bot (servidor FastAPI) NAO esta rodando**
- Por isso as mensagens nao sao processadas e nao ha respostas

---

## SOLUCAO: Iniciar o Bot

### Passo 1: Verificar Redis (Opcional mas recomendado)

O bot usa Redis para fila de mensagens. Se nao tiver Redis instalado, o bot ainda funciona mas sem fila.

**Verificar se Redis esta instalado:**
```bash
redis-cli ping
```

**Se retornar "PONG":** Redis esta OK!
**Se der erro:** Redis nao esta instalado (pode instalar depois se quiser)

**Instalar Redis no Windows:**
1. Baixe: https://github.com/microsoftarchive/redis/releases
2. Ou use Docker: `docker run -d -p 6379:6379 redis`

---

### Passo 2: INICIAR O BOT

**Comando para iniciar:**
```bash
python src/main.py
```

**Ou com auto-reload (desenvolvimento):**
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

---

### Passo 3: Verificar se o Bot Iniciou

**Teste 1: Health Check**
```bash
curl http://localhost:8000/health
```

**Resposta esperada:**
```json
{
  "status": "healthy",
  "timestamp": "2025-10-27T10:30:00",
  "whatsapp_instance": "Centro_oeste_draywal",
  "bot_number": "556292745972"
}
```

**Teste 2: Ver Documentacao**

Abra no navegador:
```
http://localhost:8000/docs
```

---

### Passo 4: Testar com Mensagem Real

Agora sim! Com o bot rodando:

1. Envie uma mensagem no WhatsApp para o numero do bot
2. O bot deve processar e responder automaticamente
3. Veja os logs em tempo real no terminal

---

## O Que Acontece Quando o Bot Roda

```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000

Quando chegar mensagem:
INFO - Webhook recebido!
INFO - Mensagem adicionada a fila
INFO - Processando mensagem via GRAFO
INFO - Cliente: 5562999999999
INFO - Resposta enviada com sucesso
```

---

## Checklist Completo

- [ ] Bot rodando: `python src/main.py`
- [ ] Health check OK: `curl http://localhost:8000/health`
- [ ] Webhook configurado na Evolution API apontando para seu servidor
- [ ] Enviar mensagem de teste no WhatsApp
- [ ] Ver logs do bot processando
- [ ] Receber resposta automatica!

---

## Se Der Erro ao Iniciar

### Erro: "Address already in use"
```bash
# Porta 8000 ja esta em uso
# Mate o processo:
# Windows:
netstat -ano | findstr :8000
taskkill /PID [numero] /F

# Ou use outra porta:
uvicorn src.main:app --port 8001
```

### Erro: "Module not found"
```bash
# Instalar dependencias:
pip install -r requirements.txt
```

### Erro: "OpenAI API Key not found"
```bash
# Verificar .env existe e tem:
# OPENAI_API_KEY=sk-...
```

---

## Dica: Rodar em Background

**Windows (PowerShell):**
```powershell
Start-Process python -ArgumentList "src/main.py" -WindowStyle Hidden
```

**Linux/Mac:**
```bash
nohup python src/main.py > bot_output.log 2>&1 &
```

---

## Proximos Passos

1. **AGORA:** Execute `python src/main.py` para iniciar o bot
2. Deixe o terminal aberto rodando o bot
3. Envie uma mensagem de teste no WhatsApp
4. Veja a magica acontecer!

---

**Criado:** 2025-10-27
**Status:** Bot NAO esta rodando - precisa iniciar!
