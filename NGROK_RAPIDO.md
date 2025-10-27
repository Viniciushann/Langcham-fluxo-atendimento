# 🚀 INSTRUÇÕES RÁPIDAS - NGROK SETUP

## ✅ SITUAÇÃO ATUAL

- **Servidor Rodando**: ✅ http://0.0.0.0:8000
- **Bot Number**: 556292745972
- **Próximo**: Configurar ngrok

## 📥 OPÇÃO MAIS FÁCIL - DOWNLOAD MANUAL

### 1. Baixar Ngrok

1. **Abra seu navegador**
2. **Vá para**: https://ngrok.com/download
3. **Clique em "Windows (64-bit)"**
4. **Salve** o arquivo `ngrok.exe` na pasta do projeto

### 2. Mover para a Pasta do Projeto

```bash
# No Windows Explorer:
# 1. Vá para Downloads
# 2. Encontre o ngrok.exe
# 3. Copie para: C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Langcham. fluxo atendimento
```

## 🔑 CONFIGURAR NGROK

### 1. Criar Conta (Gratuita)

1. **Vá para**: https://dashboard.ngrok.com/signup
2. **Crie conta** (email + senha)
3. **Copie seu authtoken** da página inicial

### 2. Configurar Token

```bash
# No terminal (onde está o ngrok.exe):
.\ngrok.exe config add-authtoken SEU_TOKEN_AQUI
```

### 3. Criar Túnel

```bash
# IMPORTANTE: Servidor deve estar rodando!
# Em um NOVO terminal:
.\ngrok.exe http 8000
```

## 📋 RESULTADO ESPERADO

O ngrok vai mostrar algo assim:

```
Session Status    online
Account           Seu Nome (Plan: Free)
Version           3.x.x
Region            United States (us)
Latency           ~150ms
Web Interface     http://127.0.0.1:4040
Forwarding        https://abc123.ngrok.io -> http://localhost:8000
Forwarding        http://abc123.ngrok.io -> http://localhost:8000

Connections       ttl     opn     rt1     rt5     p50     p90
                  0       0       0.00    0.00    0.00    0.00
```

**URL PÚBLICA**: `https://abc123.ngrok.io`

## 🔗 CONFIGURAR WEBHOOK

1. **Copie a URL**: `https://abc123.ngrok.io`
2. **Acesse Evolution API**: https://evolution.centrooestedrywalldry.com.br
3. **Configure webhook**: `https://abc123.ngrok.io/webhook/whatsapp`

## 📱 TESTE FINAL

Envie mensagem para: **+55 62 9274-5972**

- Texto: "Olá bot!"
- Áudio: Grave uma mensagem
- Imagem: Envie uma foto

## ⚠️ IMPORTANTE

- **NÃO FECHE** o terminal do servidor
- **NÃO FECHE** o terminal do ngrok
- **URL muda** cada vez que reiniciar o ngrok (conta gratuita)

---

## 🆘 SE ALGO DER ERRADO

### Problema: ngrok.exe não funciona

```bash
# Teste se funciona:
.\ngrok.exe version
```

### Problema: Servidor não responde

```bash
# Teste se servidor está ativo:
curl http://localhost:8000/health
```

### Problema: Webhook não funciona

- Verifique se a URL termina com `/webhook/whatsapp`
- Teste com: `curl -X POST https://SEU_NGROK.ngrok.io/webhook/whatsapp`

---

**PRÓXIMO PASSO**: Baixe o ngrok.exe e execute os comandos acima! 🎯
