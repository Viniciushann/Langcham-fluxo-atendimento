#!/bin/bash

# 🚀 DEPLOY CRÍTICO: Correção de Agendamento em Produção
# Data: 29/10/2025
# Problema: Dados genéricos no Google Calendar
# Solução: Injeção de dados reais no system prompt

echo "🔧 INICIANDO DEPLOY CRÍTICO: Correção de Agendamento"
echo "======================================================="
echo "📅 Data: $(date)"
echo "🎯 Objetivo: Corrigir dados do cliente no agendamento"
echo "🖥️  Servidor: 46.62.155.254 (bot.automacaovn.shop)"
echo ""

# 1. Conectar via SSH ao servidor
echo "1️⃣ Conectando ao servidor de produção..."
ssh root@46.62.155.254 << 'EOF'

# Navegar para o diretório do projeto
cd /root/Langcham-fluxo-atendimento

echo "📍 Localização atual: $(pwd)"

# 2. Fazer backup do estado atual
echo "2️⃣ Fazendo backup do código atual..."
cp src/nodes/agent.py src/nodes/agent.py.backup.$(date +%Y%m%d_%H%M%S)

# 3. Atualizar código do GitHub
echo "3️⃣ Atualizando código do repositório..."
git pull origin main

# 4. Verificar se as mudanças foram aplicadas
echo "4️⃣ Verificando mudanças aplicadas..."
if grep -q "contexto_cliente_atual" src/nodes/agent.py; then
    echo "✅ Correção aplicada: contexto_cliente_atual encontrado"
else
    echo "❌ ERRO: Correção não encontrada no código"
    exit 1
fi

if grep -q "cliente_nome: str = \"Cliente\", telefone_cliente: str = \"\"" src/nodes/agent.py; then
    echo "✅ Parâmetros corretos: função _get_system_prompt modificada"
else
    echo "❌ ERRO: Parâmetros não encontrados"
    exit 1
fi

# 5. Rebuild da imagem Docker
echo "5️⃣ Fazendo rebuild da imagem Docker..."
docker build -t whatsapp-bot-langchain:latest . --no-cache

if [ $? -eq 0 ]; then
    echo "✅ Imagem Docker construída com sucesso"
else
    echo "❌ ERRO: Falha na construção da imagem Docker"
    exit 1
fi

# 6. Update do serviço em produção (zero downtime)
echo "6️⃣ Atualizando serviço em produção..."
docker service update --force whatsapp-bot_whatsapp-bot

if [ $? -eq 0 ]; then
    echo "✅ Serviço atualizado com sucesso"
else
    echo "❌ ERRO: Falha na atualização do serviço"
    exit 1
fi

# 7. Aguardar alguns segundos para o serviço estabilizar
echo "7️⃣ Aguardando serviço estabilizar..."
sleep 10

# 8. Verificar se o serviço está rodando
echo "8️⃣ Verificando status do serviço..."
SERVICE_STATUS=$(docker service ps whatsapp-bot_whatsapp-bot --filter "desired-state=running" --format "table {{.CurrentState}}" | grep -c "Running")

if [ $SERVICE_STATUS -gt 0 ]; then
    echo "✅ Serviço está rodando corretamente"
else
    echo "❌ AVISO: Serviço pode não estar rodando"
fi

# 9. Testar health check
echo "9️⃣ Testando health check..."
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" https://bot.automacaovn.shop/health)

if [ "$HEALTH_CHECK" = "200" ]; then
    echo "✅ Health check OK (200)"
else
    echo "⚠️ Health check retornou: $HEALTH_CHECK"
fi

# 10. Verificar logs recentes
echo "🔟 Verificando logs recentes..."
echo "Últimas 5 linhas dos logs:"
docker service logs whatsapp-bot_whatsapp-bot --tail 5

EOF

echo ""
echo "🎉 DEPLOY CONCLUÍDO!"
echo "==================="
echo "✅ Correção aplicada em produção"
echo "📅 Agendamentos agora usarão dados REAIS dos clientes"
echo "🔍 Monitor os logs para verificar a mensagem de debug:"
echo "   '🔍 DEBUG: Dados injetados no system prompt'"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. Teste fazer um agendamento via WhatsApp"
echo "2. Verifique os logs para ver os dados corretos"
echo "3. Confirme no Google Calendar se o nome/telefone estão corretos"
echo ""
echo "🖥️ URLs de monitoramento:"
echo "- Health: https://bot.automacaovn.shop/health"
echo "- Docs: https://bot.automacaovn.shop/docs"
echo ""
echo "📞 Se tudo estiver funcionando, remova os logs de debug!"