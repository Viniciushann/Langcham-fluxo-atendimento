#!/bin/bash
# Script para corrigir webhook - Execute no servidor Hetzner

echo "======================================================================"
echo "CORRIGINDO URL DO WEBHOOK"
echo "======================================================================"
echo ""

# Corrigir webhook
echo "1. Atualizando webhook..."
curl -X POST "https://evolution.centrooestedrywalldry.com.br/webhook/set/Centro_oeste_draywal" \
  -H "Content-Type: application/json" \
  -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9" \
  -d '{"enabled":true,"url":"https://bot.automacaovn.shop/webhook/whatsapp","webhookByEvents":false,"webhookBase64":true,"events":["MESSAGES_UPSERT","MESSAGES_UPDATE","SEND_MESSAGE"]}'

echo ""
echo ""
echo "======================================================================"
echo "VERIFICANDO CONFIGURACAO"
echo "======================================================================"
echo ""

# Verificar
echo "2. Verificando webhook..."
curl -X GET "https://evolution.centrooestedrywalldry.com.br/webhook/find/Centro_oeste_draywal" \
  -H "apikey: 8773E1C40430-4626-B896-1302789BA4D9"

echo ""
echo ""
echo "======================================================================"
echo "PRONTO! Agora envie uma mensagem de teste para +55 62 9274-5972"
echo "======================================================================"
