#!/bin/bash

# 🔄 SCRIPT DE ATUALIZAÇÃO DO NÚMERO DO TÉCNICO
# =============================================
# 
# Este script atualiza o número do técnico em produção
# APENAS execute após o teste ter passado com sucesso!
#
# Novo número: +14372591659
# Data: 30/10/2025

echo "🔄 ATUALIZANDO NÚMERO DO TÉCNICO EM PRODUÇÃO"
echo "=============================================="
echo "📅 Data: $(date)"
echo "📱 Novo número: +14372591659"
echo "📱 Backup: 556292935358 (número atual vira backup)"
echo ""

# Confirmação de segurança
read -p "⚠️ TEM CERTEZA que o teste passou? Digite 'SIM' para continuar: " confirmacao

if [ "$confirmacao" != "SIM" ]; then
    echo "❌ Operação cancelada pelo usuário."
    exit 1
fi

echo ""
echo "🔧 Iniciando atualização..."

# 1. Backup da configuração atual
echo "💾 1. Fazendo backup da configuração atual..."
cp src/tools/scheduling.py src/tools/scheduling.py.backup.$(date +%Y%m%d_%H%M%S)

# 2. Parar o serviço para atualização
echo "⏸️ 2. Parando serviço para atualização segura..."
docker service scale whatsapp-bot_whatsapp-bot=0

# Aguardar alguns segundos
sleep 5

# 3. Atualizar o arquivo de configuração
echo "📝 3. Atualizando arquivo de configuração..."

# Criar arquivo temporário com nova configuração
cat > temp_scheduling_update.py << 'EOF'
import re

# Ler o arquivo atual
with open('src/tools/scheduling.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Atualizar as configurações
# Trocar número principal
content = re.sub(
    r"TELEFONE_TECNICO_PRINCIPAL = os\.getenv\('TELEFONE_TECNICO', '[^']+'\)",
    "TELEFONE_TECNICO_PRINCIPAL = os.getenv('TELEFONE_TECNICO', '14372591659')",
    content
)

# Atualizar sistema de fallback
content = re.sub(
    r"os\.getenv\('TELEFONE_TECNICO_BACKUP', '[^']+'\)",
    "os.getenv('TELEFONE_TECNICO_BACKUP', '556292935358')",
    content
)

content = re.sub(
    r"os\.getenv\('TELEFONE_TECNICO_BACKUP_2', '[^']+'\)",
    "os.getenv('TELEFONE_TECNICO_BACKUP_2', '556281091167')",
    content
)

# Escrever arquivo atualizado
with open('src/tools/scheduling.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Arquivo scheduling.py atualizado com sucesso!")
EOF

python3 temp_scheduling_update.py
rm temp_scheduling_update.py

# 4. Atualizar variáveis de ambiente
echo "🔧 4. Atualizando variáveis de ambiente..."

# Se existir arquivo .env, atualizar
if [ -f ".env.production" ]; then
    echo "📝 Atualizando .env.production..."
    
    # Remover linha antiga se existir
    sed -i '/^TELEFONE_TECNICO=/d' .env.production
    sed -i '/^TELEFONE_TECNICO_BACKUP=/d' .env.production
    sed -i '/^TELEFONE_TECNICO_BACKUP_2=/d' .env.production
    
    # Adicionar novas configurações
    echo "TELEFONE_TECNICO=14372591659" >> .env.production
    echo "TELEFONE_TECNICO_BACKUP=556292935358" >> .env.production
    echo "TELEFONE_TECNICO_BACKUP_2=556281091167" >> .env.production
fi

# Exportar para sessão atual
export TELEFONE_TECNICO='14372591659'
export TELEFONE_TECNICO_BACKUP='556292935358'
export TELEFONE_TECNICO_BACKUP_2='556281091167'

echo "✅ Variáveis de ambiente atualizadas!"

# 5. Rebuild da imagem Docker
echo "🐳 5. Fazendo rebuild da imagem Docker..."
docker build -t whatsapp-bot-langchain:latest . --no-cache

if [ $? -ne 0 ]; then
    echo "❌ ERRO: Falha no build da imagem Docker!"
    echo "🔄 Tentando restaurar serviço com configuração anterior..."
    docker service scale whatsapp-bot_whatsapp-bot=1
    exit 1
fi

echo "✅ Imagem Docker atualizada!"

# 6. Restartar o serviço
echo "🚀 6. Reiniciando serviço com nova configuração..."
docker service scale whatsapp-bot_whatsapp-bot=1

# Aguardar o serviço subir
echo "⏳ Aguardando serviço estabilizar..."
sleep 15

# 7. Verificar se o serviço está rodando
echo "🔍 7. Verificando status do serviço..."
SERVICE_STATUS=$(docker service ps whatsapp-bot_whatsapp-bot --filter "desired-state=running" --format "table {{.CurrentState}}" | grep -c "Running")

if [ $SERVICE_STATUS -gt 0 ]; then
    echo "✅ Serviço está rodando!"
else
    echo "⚠️ AVISO: Serviço pode não estar rodando corretamente"
    echo "📋 Verifique os logs:"
    docker service logs whatsapp-bot_whatsapp-bot --tail 20
fi

# 8. Teste rápido de health check
echo "🩺 8. Testando health check..."
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" https://bot.automacaovn.shop/health)

if [ "$HEALTH_CHECK" = "200" ]; then
    echo "✅ Health check OK (200)"
else
    echo "⚠️ Health check retornou: $HEALTH_CHECK"
fi

# 9. Mostrar logs recentes
echo "📜 9. Logs recentes do serviço:"
echo "─────────────────────────────────"
docker service logs whatsapp-bot_whatsapp-bot --tail 10

echo ""
echo "🎉 ATUALIZAÇÃO CONCLUÍDA!"
echo "========================="
echo "✅ Número do técnico atualizado para: +14372591659"
echo "📱 Números de backup configurados:"
echo "   - Backup 1: 556292935358"
echo "   - Backup 2: 556281091167"
echo ""
echo "📋 PRÓXIMOS PASSOS:"
echo "1. 🧪 Teste fazendo um agendamento pelo WhatsApp"
echo "2. 📊 Monitore os logs para verificar se a notificação chega"
echo "3. 📱 Confirme se você recebe a mensagem no novo número"
echo ""
echo "🖥️ Comandos úteis:"
echo "   - Ver logs: docker service logs whatsapp-bot_whatsapp-bot --follow"
echo "   - Status: docker service ps whatsapp-bot_whatsapp-bot"
echo "   - Health: curl https://bot.automacaovn.shop/health"
echo ""
echo "⚠️ Se algo der errado, os backups estão em:"
echo "   src/tools/scheduling.py.backup.*"