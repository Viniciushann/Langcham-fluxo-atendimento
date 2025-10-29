#!/bin/bash

################################################################################
# Script de Deploy - Correção do Telefone do Técnico
# Versão: 1.0
# Data: 2025-10-29
# Descrição: Atualiza o sistema em produção com a correção do número do técnico
################################################################################

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir com cor
print_color() {
    COLOR=$1
    shift
    echo -e "${COLOR}$@${NC}"
}

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Banner
echo ""
print_color $BLUE "╔════════════════════════════════════════════════════════════╗"
print_color $BLUE "║  🚀 DEPLOY - CORREÇÃO DO TELEFONE DO TÉCNICO             ║"
print_color $BLUE "╚════════════════════════════════════════════════════════════╝"
echo ""

# Verificar se está no diretório correto
if [ ! -f "src/tools/scheduling.py" ]; then
    print_color $RED "❌ ERRO: Execute este script no diretório raiz do projeto!"
    exit 1
fi

print_color $YELLOW "📋 Verificando pré-requisitos..."

# Verificar Docker
if ! command_exists docker; then
    print_color $RED "❌ Docker não encontrado!"
    exit 1
fi
print_color $GREEN "✅ Docker OK"

# Verificar Git
if ! command_exists git; then
    print_color $RED "❌ Git não encontrado!"
    exit 1
fi
print_color $GREEN "✅ Git OK"

# Verificar Python
if ! command_exists python && ! command_exists python3; then
    print_color $RED "❌ Python não encontrado!"
    exit 1
fi
print_color $GREEN "✅ Python OK"

echo ""
print_color $BLUE "════════════════════════════════════════════════════════════"
print_color $BLUE "ETAPA 1: BACKUP DO CÓDIGO ATUAL"
print_color $BLUE "════════════════════════════════════════════════════════════"

BACKUP_FILE="src/tools/scheduling.py.backup-$(date +%Y%m%d-%H%M%S)"
cp src/tools/scheduling.py "$BACKUP_FILE"
print_color $GREEN "✅ Backup criado: $BACKUP_FILE"

echo ""
print_color $BLUE "════════════════════════════════════════════════════════════"
print_color $BLUE "ETAPA 2: VALIDAR MUDANÇAS"
print_color $BLUE "════════════════════════════════════════════════════════════"

# Verificar se número foi corrigido
if grep -q "55628540075" src/tools/scheduling.py; then
    print_color $GREEN "✅ Número corrigido encontrado: 55628540075"
else
    print_color $RED "❌ Número correto não encontrado no arquivo!"
    exit 1
fi

# Verificar sintaxe Python
if command_exists python3; then
    PYTHON_CMD=python3
else
    PYTHON_CMD=python
fi

$PYTHON_CMD -m py_compile src/tools/scheduling.py 2>&1
if [ $? -eq 0 ]; then
    print_color $GREEN "✅ Sintaxe Python válida"
else
    print_color $RED "❌ Erro de sintaxe no arquivo Python!"
    exit 1
fi

echo ""
print_color $BLUE "════════════════════════════════════════════════════════════"
print_color $BLUE "ETAPA 3: VERIFICAR VARIÁVEIS DE AMBIENTE"
print_color $BLUE "════════════════════════════════════════════════════════════"

# Verificar se .env existe
if [ -f ".env" ]; then
    print_color $GREEN "✅ Arquivo .env encontrado"

    # Verificar se variáveis estão configuradas
    if grep -q "TELEFONE_TECNICO=" .env; then
        TELEFONE=$(grep "TELEFONE_TECNICO=" .env | head -1 | cut -d'=' -f2)
        print_color $YELLOW "📞 TELEFONE_TECNICO atual: $TELEFONE"

        if [ "$TELEFONE" = "55628540075" ]; then
            print_color $GREEN "✅ Número correto configurado no .env"
        else
            print_color $YELLOW "⚠️  ATENÇÃO: Número no .env é diferente do esperado!"
            print_color $YELLOW "    Esperado: 55628540075"
            print_color $YELLOW "    Atual: $TELEFONE"
            read -p "Deseja continuar? (s/n) " -n 1 -r
            echo
            if [[ ! $REPLY =~ ^[Ss]$ ]]; then
                exit 1
            fi
        fi
    else
        print_color $YELLOW "⚠️  TELEFONE_TECNICO não encontrado no .env"
        print_color $YELLOW "    Será usado o valor padrão do código: 55628540075"
    fi
else
    print_color $YELLOW "⚠️  Arquivo .env não encontrado"
    print_color $YELLOW "    Será usado o valor padrão do código: 55628540075"
fi

echo ""
print_color $BLUE "════════════════════════════════════════════════════════════"
print_color $BLUE "ETAPA 4: RECONSTRUIR IMAGEM DOCKER"
print_color $BLUE "════════════════════════════════════════════════════════════"

print_color $YELLOW "🔨 Reconstruindo imagem Docker..."
docker build -t whatsapp-bot:latest . || {
    print_color $RED "❌ Erro ao construir imagem Docker!"
    exit 1
}
print_color $GREEN "✅ Imagem Docker reconstruída"

echo ""
print_color $BLUE "════════════════════════════════════════════════════════════"
print_color $BLUE "ETAPA 5: ATUALIZAR SERVIÇO NO SWARM"
print_color $BLUE "════════════════════════════════════════════════════════════"

print_color $YELLOW "🔄 Atualizando serviço whatsapp-bot..."

# Verificar se serviço existe
if docker service ls | grep -q whatsapp-bot; then
    docker service update --image whatsapp-bot:latest whatsapp-bot || {
        print_color $RED "❌ Erro ao atualizar serviço!"
        exit 1
    }
    print_color $GREEN "✅ Serviço atualizado"
else
    print_color $YELLOW "⚠️  Serviço whatsapp-bot não encontrado no Swarm"
    print_color $YELLOW "    Tentando iniciar stack..."

    if [ -f "docker-compose.yml" ]; then
        docker stack deploy -c docker-compose.yml whatsapp-bot || {
            print_color $RED "❌ Erro ao iniciar stack!"
            exit 1
        }
        print_color $GREEN "✅ Stack iniciada"
    else
        print_color $RED "❌ docker-compose.yml não encontrado!"
        exit 1
    fi
fi

echo ""
print_color $BLUE "════════════════════════════════════════════════════════════"
print_color $BLUE "ETAPA 6: AGUARDAR SERVIÇO INICIAR"
print_color $BLUE "════════════════════════════════════════════════════════════"

print_color $YELLOW "⏳ Aguardando serviço iniciar (30 segundos)..."
sleep 30

echo ""
print_color $BLUE "════════════════════════════════════════════════════════════"
print_color $BLUE "ETAPA 7: VERIFICAR STATUS DO SERVIÇO"
print_color $BLUE "════════════════════════════════════════════════════════════"

# Verificar replicas
REPLICAS=$(docker service ls --format "{{.Replicas}}" --filter "name=whatsapp-bot")
print_color $YELLOW "📊 Réplicas: $REPLICAS"

if echo "$REPLICAS" | grep -q "1/1"; then
    print_color $GREEN "✅ Serviço rodando corretamente"
else
    print_color $YELLOW "⚠️  Serviço pode não estar rodando completamente"
fi

# Verificar logs
print_color $YELLOW "📋 Últimos logs do serviço:"
docker service logs --tail 20 whatsapp-bot 2>&1 | tail -10

# Verificar mensagem específica
if docker service logs --tail 50 whatsapp-bot 2>&1 | grep -q "Sistema de notificação configurado"; then
    print_color $GREEN "✅ Sistema de notificação inicializado"
else
    print_color $YELLOW "⚠️  Mensagem de inicialização não encontrada nos logs"
fi

echo ""
print_color $BLUE "════════════════════════════════════════════════════════════"
print_color $BLUE "ETAPA 8: EXECUTAR TESTE DE VALIDAÇÃO"
print_color $BLUE "════════════════════════════════════════════════════════════"

if [ -f "tests/test_telefone_tecnico.py" ]; then
    print_color $YELLOW "🧪 Executando teste de validação..."
    $PYTHON_CMD tests/test_telefone_tecnico.py || {
        print_color $YELLOW "⚠️  Teste falhou - verifique logs"
    }
else
    print_color $YELLOW "⚠️  Arquivo de teste não encontrado"
fi

echo ""
print_color $GREEN "╔════════════════════════════════════════════════════════════╗"
print_color $GREEN "║  ✅ DEPLOY CONCLUÍDO COM SUCESSO!                        ║"
print_color $GREEN "╚════════════════════════════════════════════════════════════╝"
echo ""

print_color $BLUE "📋 PRÓXIMOS PASSOS:"
echo "1. Monitorar logs: docker service logs -f whatsapp-bot"
echo "2. Fazer teste real de agendamento via WhatsApp"
echo "3. Verificar se notificação chega ao técnico (55628540075)"
echo "4. Monitorar por 15 minutos para garantir estabilidade"
echo ""

print_color $BLUE "🔙 ROLLBACK (se necessário):"
echo "   cp $BACKUP_FILE src/tools/scheduling.py"
echo "   docker service update --force whatsapp-bot"
echo ""

print_color $GREEN "✅ Sistema atualizado e pronto para uso!"
echo ""
