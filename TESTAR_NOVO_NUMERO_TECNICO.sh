# 🧪 COMANDOS PARA TESTAR NOVO NÚMERO DO TÉCNICO
# Execute estes comandos no servidor Hetzner via SSH

echo "🔧 INICIANDO TESTE DO NOVO NÚMERO DO TÉCNICO"
echo "=============================================="
echo "📅 Data: $(date)"
echo "📱 Novo número: +14372591659"
echo "🖥️ Servidor: 46.62.155.254"
echo ""

# 1. SSH no servidor
ssh root@46.62.155.254 << 'EOF'

# Navegar para o projeto
cd /root/Langcham-fluxo-atendimento

echo "📍 Localização: $(pwd)"

# 2. Fazer backup do arquivo atual (por segurança)
echo "💾 Fazendo backup do arquivo scheduling.py..."
cp src/tools/scheduling.py src/tools/scheduling.py.backup.$(date +%Y%m%d_%H%M%S)

# 3. Baixar o script de teste
echo "📥 Baixando script de teste..."
wget -q https://raw.githubusercontent.com/Viniciushann/Langcham-fluxo-atendimento/main/teste_numero_tecnico.py -O teste_numero_tecnico.py

# Se não conseguir baixar, criar o script manualmente
if [ ! -f "teste_numero_tecnico.py" ]; then
    echo "📝 Criando script de teste manualmente..."
    cat > teste_numero_tecnico.py << 'SCRIPT'
#!/usr/bin/env python3
import os
import sys
import asyncio
import logging
from datetime import datetime

sys.path.append('src')

from src.clients.whatsapp_client import WhatsAppClient
from src.config.settings import get_settings

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

NOVO_NUMERO_TECNICO = "14372591659"

async def testar_numero_whatsapp(numero: str, descricao: str) -> dict:
    print(f"\n📱 Testando {descricao}: {numero}")
    print("─" * 50)
    
    try:
        settings = get_settings()
        
        whatsapp = WhatsAppClient(
            base_url=settings.whatsapp_api_url,
            api_key=settings.whatsapp_api_key,
            instance=settings.whatsapp_instance
        )
        
        agora = datetime.now()
        data_hora = agora.strftime('%d/%m/%Y às %H:%M:%S')
        
        mensagem_teste = f"""🧪 TESTE DO SISTEMA

⏰ Data/Hora: {data_hora}
🔧 Testando novo número do técnico
📞 Número testado: {numero}

✅ Se você recebeu esta mensagem, o número está funcionando corretamente!

⚠️ Esta é apenas uma mensagem de teste do sistema."""

        print(f"📤 Enviando mensagem de teste...")
        
        resultado = await whatsapp.enviar_mensagem(
            telefone=numero,
            texto=mensagem_teste
        )
        
        if resultado:
            print(f"✅ SUCESSO: Mensagem enviada com sucesso")
            return {"sucesso": True, "numero": numero, "descricao": descricao, "erro": None}
        else:
            print(f"⚠️ AVISO: API retornou resposta vazia")
            return {"sucesso": False, "numero": numero, "descricao": descricao, "erro": "Resposta vazia"}
            
    except Exception as e:
        error_msg = str(e).lower()
        
        if "exists" in error_msg and "false" in error_msg:
            print(f"❌ ERRO: Número não existe no WhatsApp")
            erro_diagnostico = "Número não cadastrado no WhatsApp"
        elif "400" in error_msg:
            print(f"❌ ERRO: Requisição inválida")
            erro_diagnostico = "Formato de número inválido"
        else:
            print(f"❌ ERRO: {e}")
            erro_diagnostico = str(e)
            
        return {"sucesso": False, "numero": numero, "descricao": descricao, "erro": erro_diagnostico}

async def main():
    print("=" * 70)
    print("🧪 TESTE DE NÚMERO DO TÉCNICO")
    print("=" * 70)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"📱 Novo número: {NOVO_NUMERO_TECNICO}")
    print("=" * 70)
    
    resultado = await testar_numero_whatsapp(NOVO_NUMERO_TECNICO, "NOVO TÉCNICO")
    
    print("\n" + "=" * 70)
    print("📊 RESULTADO DO TESTE")
    print("=" * 70)
    
    if resultado['sucesso']:
        print("✅ APROVADO: O novo número está funcionando!")
        print("📝 Você pode atualizar a configuração de produção.")
    else:
        print("❌ REPROVADO: O novo número NÃO está funcionando!")
        print(f"💡 Erro: {resultado['erro']}")
        print("⚠️ NÃO atualize a configuração ainda.")
    
    return resultado['sucesso']

if __name__ == "__main__":
    try:
        sucesso = asyncio.run(main())
        sys.exit(0 if sucesso else 1)
    except Exception as e:
        print(f"❌ Erro durante o teste: {e}")
        sys.exit(1)
SCRIPT

    chmod +x teste_numero_tecnico.py
fi

# 4. Executar o teste
echo "🧪 Executando teste do novo número..."
python3 teste_numero_tecnico.py

RESULTADO=$?

# 5. Interpretar resultado
echo ""
echo "📊 RESULTADO DO TESTE:"
echo "======================"

if [ $RESULTADO -eq 0 ]; then
    echo "✅ TESTE PASSOU! O número +14372591659 está funcionando."
    echo ""
    echo "🔧 PRÓXIMOS PASSOS PARA ATUALIZAR:"
    echo "================================="
    echo "1. Parar o serviço:"
    echo "   docker service scale whatsapp-bot_whatsapp-bot=0"
    echo ""
    echo "2. Atualizar variável de ambiente:"
    echo "   export TELEFONE_TECNICO='14372591659'"
    echo "   export TELEFONE_TECNICO_BACKUP='556292935358'"
    echo ""
    echo "3. Restartar o serviço:"
    echo "   docker service scale whatsapp-bot_whatsapp-bot=1"
    echo ""
    echo "4. Verificar logs:"
    echo "   docker service logs whatsapp-bot_whatsapp-bot --follow"
    echo ""
    echo "⚠️ OU execute o script de atualização automática:"
    echo "   ./atualizar_numero_tecnico.sh"
    
else
    echo "❌ TESTE FALHOU! O número +14372591659 NÃO está funcionando."
    echo ""
    echo "🔧 VERIFICAÇÕES NECESSÁRIAS:"
    echo "============================"
    echo "1. Confirme se o número tem WhatsApp ativo"
    echo "2. Verifique se o formato está correto: 14372591659"
    echo "3. Teste manualmente enviando uma mensagem"
    echo "4. Verifique se a Evolution API está funcionando"
    echo ""
    echo "⚠️ NÃO ATUALIZE a configuração de produção até resolver!"
fi

EOF

echo ""
echo "🏁 TESTE CONCLUÍDO!"
echo "==================="
echo "📋 Verifique o resultado acima para decidir se pode atualizar."
echo "🖥️ Se aprovado, execute os comandos sugeridos no servidor."