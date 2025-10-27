"""
Script de teste para autenticação e funcionalidades do Google Calendar.

Este script testa:
1. Autenticação OAuth 2.0
2. Consulta de horários disponíveis
3. Criação de evento de teste (opcional)

Execute: python test_google_calendar.py
"""

import asyncio
import sys
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

# Adiciona o diretório src ao path
sys.path.insert(0, 'src')

from tools.scheduling import agendamento_tool


async def teste_autenticacao():
    """Testa a autenticação com Google Calendar."""
    print("\n" + "="*60)
    print("TESTE 1: AUTENTICAÇÃO GOOGLE CALENDAR")
    print("="*60)

    try:
        # Data de amanhã
        amanha = datetime.now(ZoneInfo('America/Sao_Paulo')) + timedelta(days=1)
        data_teste = amanha.strftime('%Y-%m-%d')

        print(f"\n📅 Consultando horários disponíveis para: {data_teste}")
        print("⏳ Aguarde... (uma janela do navegador pode abrir para autenticação)\n")

        resultado = await agendamento_tool(
            nome_cliente="Teste Sistema",
            telefone_cliente="11999999999",
            email_cliente="teste@teste.com",
            data_consulta_reuniao=data_teste,
            intencao="consultar",
            informacao_extra=""
        )

        if resultado['sucesso']:
            print("✅ AUTENTICAÇÃO BEM-SUCEDIDA!\n")
            print(f"📊 {resultado['mensagem']}")

            if resultado['dados'].get('horarios'):
                print(f"\n🕒 Horários disponíveis em {resultado['dados']['data_referencia']}:")
                for i, horario in enumerate(resultado['dados']['horarios'][:5], 1):
                    inicio = datetime.fromisoformat(horario['inicio'])
                    fim = datetime.fromisoformat(horario['fim'])
                    print(f"   {i}. {inicio.strftime('%H:%M')} - {fim.strftime('%H:%M')}")

                if len(resultado['dados']['horarios']) > 5:
                    print(f"   ... e mais {len(resultado['dados']['horarios']) - 5} horários")

            return True
        else:
            print(f"❌ ERRO: {resultado['mensagem']}")
            return False

    except Exception as e:
        print(f"❌ ERRO NA AUTENTICAÇÃO: {str(e)}")
        return False


async def teste_agendar():
    """Testa a criação de um evento de teste."""
    print("\n" + "="*60)
    print("TESTE 2: CRIAR EVENTO DE TESTE")
    print("="*60)

    try:
        # Amanhã às 14h
        amanha = datetime.now(ZoneInfo('America/Sao_Paulo')) + timedelta(days=1)
        data_hora = amanha.replace(hour=14, minute=0, second=0, microsecond=0)

        print(f"\n📅 Tentando agendar evento de teste para: {data_hora.strftime('%d/%m/%Y às %H:%M')}")
        print("⏳ Aguarde...\n")

        resultado = await agendamento_tool(
            nome_cliente="TESTE - Deletar",
            telefone_cliente="11999999999",
            email_cliente="sememail@gmail.com",
            data_consulta_reuniao=data_hora.isoformat(),
            intencao="agendar",
            informacao_extra="Este é um evento de teste do sistema de agendamento."
        )

        if resultado['sucesso']:
            print("✅ EVENTO CRIADO COM SUCESSO!\n")
            print(f"📊 {resultado['mensagem']}")
            print(f"\n🆔 ID do evento: {resultado['dados']['evento_id']}")
            print(f"🔗 Link: {resultado['dados']['link']}")
            print("\n⚠️  IMPORTANTE: Lembre-se de deletar este evento de teste no Google Calendar!")
            return True
        else:
            print(f"❌ ERRO: {resultado['mensagem']}")
            return False

    except Exception as e:
        print(f"❌ ERRO AO AGENDAR: {str(e)}")
        return False


async def teste_consultar_periodo():
    """Testa consulta com filtro de período."""
    print("\n" + "="*60)
    print("TESTE 3: CONSULTAR HORÁRIOS DA TARDE")
    print("="*60)

    try:
        # Depois de amanhã
        daqui_2_dias = datetime.now(ZoneInfo('America/Sao_Paulo')) + timedelta(days=2)
        data_teste = daqui_2_dias.strftime('%Y-%m-%d')

        print(f"\n📅 Consultando horários da TARDE para: {data_teste}")
        print("⏳ Aguarde...\n")

        resultado = await agendamento_tool(
            nome_cliente="Teste",
            telefone_cliente="11999999999",
            email_cliente="teste@teste.com",
            data_consulta_reuniao=data_teste,
            intencao="consultar",
            informacao_extra="período da tarde"
        )

        if resultado['sucesso']:
            print("✅ CONSULTA BEM-SUCEDIDA!\n")
            print(f"📊 {resultado['mensagem']}")

            if resultado['dados'].get('horarios'):
                print(f"\n🕒 Horários da tarde disponíveis:")
                for i, horario in enumerate(resultado['dados']['horarios'], 1):
                    inicio = datetime.fromisoformat(horario['inicio'])
                    fim = datetime.fromisoformat(horario['fim'])
                    print(f"   {i}. {inicio.strftime('%H:%M')} - {fim.strftime('%H:%M')}")

            return True
        else:
            print(f"❌ ERRO: {resultado['mensagem']}")
            return False

    except Exception as e:
        print(f"❌ ERRO NA CONSULTA: {str(e)}")
        return False


async def main():
    """Executa todos os testes."""
    print("\n")
    print("╔" + "="*58 + "╗")
    print("║" + " "*15 + "TESTE GOOGLE CALENDAR API" + " "*18 + "║")
    print("╚" + "="*58 + "╝")

    resultados = {
        'autenticacao': False,
        'agendar': False,
        'consultar_periodo': False
    }

    # Teste 1: Autenticação e consulta básica
    resultados['autenticacao'] = await teste_autenticacao()

    if not resultados['autenticacao']:
        print("\n⚠️  Testes interrompidos - falha na autenticação.")
        print("\nVerifique:")
        print("  1. Arquivo credentials.json está na raiz do projeto")
        print("  2. Google Calendar API está ativada no Google Cloud Console")
        print("  3. Dependências instaladas: pip install google-auth-oauthlib google-api-python-client")
        return

    # Pergunta se quer criar evento de teste
    print("\n" + "-"*60)
    resposta = input("\n❓ Deseja criar um evento de TESTE no calendário? (s/N): ").lower()

    if resposta == 's':
        resultados['agendar'] = await teste_agendar()
    else:
        print("⏭️  Pulando teste de agendamento.")

    # Teste 3: Consulta com filtro
    resultados['consultar_periodo'] = await teste_consultar_periodo()

    # Resumo final
    print("\n" + "="*60)
    print("RESUMO DOS TESTES")
    print("="*60)

    total = len(resultados)
    passou = sum(1 for r in resultados.values() if r)

    print(f"\n✅ Testes bem-sucedidos: {passou}/{total}")
    print(f"❌ Testes com erro: {total - passou}/{total}")

    print("\n📋 Detalhes:")
    for teste, resultado in resultados.items():
        status = "✅ PASSOU" if resultado else "❌ FALHOU"
        print(f"  • {teste.replace('_', ' ').title()}: {status}")

    print("\n" + "="*60)

    if passou == total:
        print("\n🎉 TODOS OS TESTES PASSARAM! Sistema pronto para uso.")
    else:
        print("\n⚠️  Alguns testes falharam. Verifique os erros acima.")

    print()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Testes interrompidos pelo usuário.")
    except Exception as e:
        print(f"\n\n❌ ERRO CRÍTICO: {str(e)}")
        import traceback
        traceback.print_exc()
