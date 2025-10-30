#!/usr/bin/env python3
"""
🧪 TESTE DE NÚMERO DO TÉCNICO
=============================

Script para testar se um número de WhatsApp está funcionando corretamente
antes de atualizar a configuração de produção.

Uso: python teste_numero_tecnico.py

Autor: Sistema WhatsApp Bot
Data: 30/10/2025
"""

import os
import sys
import asyncio
import logging
from datetime import datetime

# Adicionar src ao path
sys.path.append('src')

from src.clients.whatsapp_client import WhatsAppClient
from src.config.settings import get_settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# CONFIGURAÇÃO DO TESTE
NOVO_NUMERO_TECNICO = "14372591659"  # Novo número para testar
NUMEROS_ATUAIS = [
    "556281091167",  # Backup válido atual
]

async def testar_numero_whatsapp(numero: str, descricao: str) -> dict:
    """
    Testa se um número específico está ativo no WhatsApp.
    
    Args:
        numero: Número de telefone para testar
        descricao: Descrição do número (ex: "Novo técnico")
    
    Returns:
        dict: Resultado do teste
    """
    print(f"\n📱 Testando {descricao}: {numero}")
    print("─" * 50)
    
    try:
        settings = get_settings()
        
        # Criar cliente WhatsApp
        whatsapp = WhatsAppClient(
            base_url=settings.whatsapp_api_url,
            api_key=settings.whatsapp_api_key,
            instance=settings.whatsapp_instance
        )
        
        # Preparar mensagem de teste
        agora = datetime.now()
        data_hora = agora.strftime('%d/%m/%Y às %H:%M:%S')
        
        mensagem_teste = f"""🧪 TESTE DO SISTEMA

⏰ Data/Hora: {data_hora}
🔧 Testando novo número do técnico
📞 Número testado: {numero}

✅ Se você recebeu esta mensagem, o número está funcionando corretamente!

⚠️ Esta é apenas uma mensagem de teste do sistema.
Não é necessário responder."""

        print(f"📤 Enviando mensagem de teste...")
        
        # Tentar enviar mensagem
        resultado = await whatsapp.enviar_mensagem(
            telefone=numero,
            texto=mensagem_teste
        )
        
        if resultado:
            print(f"✅ SUCESSO: Mensagem enviada com sucesso")
            print(f"📊 Resposta da API: {resultado}")
            return {
                "sucesso": True,
                "numero": numero,
                "descricao": descricao,
                "resposta": resultado,
                "erro": None
            }
        else:
            print(f"⚠️ AVISO: API retornou resposta vazia")
            return {
                "sucesso": False,
                "numero": numero,
                "descricao": descricao,
                "resposta": None,
                "erro": "Resposta vazia da API"
            }
            
    except Exception as e:
        error_msg = str(e).lower()
        
        # Diagnóstico específico
        if "exists" in error_msg and "false" in error_msg:
            print(f"❌ ERRO: Número não existe no WhatsApp")
            erro_diagnostico = "Número não cadastrado no WhatsApp"
        elif "400" in error_msg or "bad request" in error_msg:
            print(f"❌ ERRO: Requisição inválida")
            erro_diagnostico = "Formato de número inválido ou outro erro de requisição"
        elif "401" in error_msg or "unauthorized" in error_msg:
            print(f"❌ ERRO: Não autorizado")
            erro_diagnostico = "Problema de autenticação da API"
        elif "timeout" in error_msg:
            print(f"❌ ERRO: Timeout")
            erro_diagnostico = "Timeout de conexão"
        else:
            print(f"❌ ERRO: {e}")
            erro_diagnostico = str(e)
            
        return {
            "sucesso": False,
            "numero": numero,
            "descricao": descricao,
            "resposta": None,
            "erro": erro_diagnostico
        }

async def main():
    """Função principal do teste."""
    print("=" * 70)
    print("🧪 TESTE DE NÚMERO DO TÉCNICO - SISTEMA WHATSAPP BOT")
    print("=" * 70)
    print(f"📅 Data: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"🎯 Objetivo: Testar novo número antes de atualizar produção")
    print(f"📱 Novo número: {NOVO_NUMERO_TECNICO}")
    print("=" * 70)
    
    resultados = []
    
    # 1. Testar número novo
    print(f"\n🔍 FASE 1: Testando NOVO número")
    resultado_novo = await testar_numero_whatsapp(
        NOVO_NUMERO_TECNICO, 
        "NOVO TÉCNICO"
    )
    resultados.append(resultado_novo)
    
    # 2. Testar números atuais (para comparação)
    print(f"\n🔍 FASE 2: Testando número ATUAL (para comparação)")
    
    for i, numero in enumerate(NUMEROS_ATUAIS, 1):
        resultado_atual = await testar_numero_whatsapp(
            numero, 
            f"TÉCNICO ATUAL #{i}"
        )
        resultados.append(resultado_atual)
        
        # Pequena pausa entre testes
        await asyncio.sleep(2)
    
    # 3. Relatório final
    print("\n" + "=" * 70)
    print("📊 RELATÓRIO FINAL DOS TESTES")
    print("=" * 70)
    
    sucesso_total = 0
    falha_total = 0
    
    for resultado in resultados:
        numero = resultado['numero']
        descricao = resultado['descricao']
        sucesso = resultado['sucesso']
        erro = resultado['erro']
        
        if sucesso:
            print(f"✅ {descricao} ({numero}): FUNCIONANDO")
            sucesso_total += 1
        else:
            print(f"❌ {descricao} ({numero}): FALHOU - {erro}")
            falha_total += 1
    
    print("─" * 70)
    print(f"📈 Resumo: {sucesso_total} sucessos, {falha_total} falhas")
    
    # 4. Recomendação
    print("\n🎯 RECOMENDAÇÃO:")
    print("─" * 70)
    
    novo_funcionando = resultados[0]['sucesso'] if resultados else False
    
    if novo_funcionando:
        print("✅ APROVADO: O novo número está funcionando!")
        print("📝 Próximos passos:")
        print("   1. Você pode atualizar a variável de ambiente no servidor")
        print("   2. Reiniciar o serviço para aplicar a mudança")
        print("   3. Monitorar logs após a mudança")
        print("")
        print("🔧 Comandos para aplicar a mudança:")
        print(f"   export TELEFONE_TECNICO='{NOVO_NUMERO_TECNICO}'")
        print("   docker service update --force whatsapp-bot_whatsapp-bot")
        
    else:
        print("❌ REPROVADO: O novo número NÃO está funcionando!")
        print("⚠️ NÃO atualize a configuração de produção ainda.")
        print("🔧 Verifique:")
        print("   1. Se o número tem WhatsApp ativo")
        print("   2. Se o formato está correto")
        print("   3. Se a API Evolution está funcionando")
        print("   4. Teste manualmente enviando mensagem")
    
    print("\n" + "=" * 70)
    print("🏁 TESTE CONCLUÍDO")
    print("=" * 70)

if __name__ == "__main__":
    # Verificar se está no ambiente correto
    if not os.path.exists('src'):
        print("❌ ERRO: Execute este script na raiz do projeto")
        print("   Exemplo: python teste_numero_tecnico.py")
        sys.exit(1)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n❌ Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()