# Configuração do Ngrok - Instruções Passo a Passo

## ✅ Status Atual

- **Servidor FastAPI**: ✅ Rodando em http://0.0.0.0:8000
- **Bot Number**: 556292745972
- **Próximo Passo**: Configurar ngrok para expor publicamente

## 🔧 Instalação do Ngrok

### Opção 1: Microsoft Store (Recomendado)

1. Pressione `Win + S` e pesquise "Microsoft Store"
2. Na Microsoft Store, pesquise por "ngrok"
3. Instale o ngrok da Microsoft Store
4. Após instalar, reinicie o PowerShell

### Opção 2: Download Manual

1. Vá para: https://ngrok.com/download
2. Baixe a versão Windows (64-bit)
3. Extraia o arquivo `ngrok.exe` para uma pasta (ex: `C:\ngrok`)
4. Adicione essa pasta ao PATH ou execute direto da pasta

## 🚀 Configuração e Uso

### 1. Criar Conta Ngrok (Gratuita)

```bash
# Vá para: https://dashboard.ngrok.com/signup
# Crie uma conta gratuita
# Copie seu authtoken
```

### 2. Configurar Authtoken

```bash
ngrok config add-authtoken SEU_AUTHTOKEN_AQUI
```

### 3. Criar Túnel (MANTER SERVIDOR RODANDO!)

```bash
# Em um NOVO terminal (não feche o servidor!)
ngrok http 8000
```

### 4. Configurar Webhook na Evolution API

1. Acesse: https://evolution.centrooestedrywalldry.com.br
2. Vá em **Webhooks** ou **Configurações**
3. Configure o webhook URL como:
   ```
   https://SEU_SUBDOMINIO.ngrok.io/webhook/whatsapp
   ```
   **Exemplo**: `https://abc123.ngrok.io/webhook/whatsapp`

## 📱 Teste Final

### 1. Enviar Mensagem de Teste

- Mande uma mensagem para: **+55 62 9274-5972**
- Tipos de teste:
  - **Texto**: "Olá, bot!"
  - **Áudio**: Envie um áudio de voz
  - **Imagem**: Envie uma foto

### 2. Verificar Logs

- No terminal do servidor, você verá:

```
INFO: Webhook recebido de [número]
INFO: Processando mensagem tipo: text/audio/image
INFO: Resposta enviada com sucesso
```

## 🔍 Troubleshooting

### Problema: "ngrok não encontrado"

- Verifique se instalou corretamente
- Reinicie o PowerShell após instalação
- Tente executar com caminho completo

### Problema: "Tunnel não funciona"

- Verifique se o servidor está rodando na porta 8000
- Confirme se o authtoken está configurado
- Teste: `curl http://localhost:8000/health`

### Problema: "Webhook não chega"

- Verifique a URL do webhook na Evolution API
- Confirme se termina com `/webhook/whatsapp`
- Teste POST manual: `curl -X POST https://SEU_NGROK.ngrok.io/webhook/whatsapp`

## 📋 Checklist Final

- [ ] Servidor rodando em http://0.0.0.0:8000
- [ ] Ngrok instalado e configurado
- [ ] Túnel ngrok ativo
- [ ] Webhook configurado na Evolution API
- [ ] Teste de mensagem enviado
- [ ] Logs mostram processamento correto

## 🎯 URLs Importantes

- **Servidor Local**: http://localhost:8000
- **Health Check**: http://localhost:8000/health
- **Webhook Endpoint**: `/webhook/whatsapp`
- **Evolution API**: https://evolution.centrooestedrywalldry.com.br
- **Ngrok Dashboard**: https://dashboard.ngrok.com

---

**Nota**: Mantenha o servidor rodando SEMPRE que estiver testando o bot!
