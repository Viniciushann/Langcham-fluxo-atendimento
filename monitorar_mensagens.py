"""
Script para monitorar mensagens chegando no sistema.

Mostra em tempo real:
- Mensagens recebidas via webhook
- Logs do sistema
- Processamento do bot
"""

import asyncio
import logging
from datetime import datetime
from src.clients.supabase_client import criar_supabase_client
from src.config.settings import get_settings

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def verificar_ultimas_mensagens():
    """Verifica as últimas mensagens recebidas."""

    settings = get_settings()
    supabase = criar_supabase_client(settings.supabase_url, settings.supabase_key)

    print("\n" + "="*70)
    print("MONITORAMENTO DE MENSAGENS - CENTRO OESTE DRYWALL")
    print("="*70 + "\n")

    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print(f"Instancia WhatsApp: {settings.whatsapp_instance}")
    print(f"Numero do Bot: {settings.bot_phone_number}\n")

    print("-"*70)
    print("ULTIMAS MENSAGENS RECEBIDAS (LEADS)")
    print("-"*70 + "\n")

    try:
        # Buscar últimos 10 leads (mensagens)
        response = supabase.client.table("leads").select(
            "id, nome_Leed, phone_numero, message, created_at"
        ).order("created_at", desc=True).limit(10).execute()

        leads = response.data

        if not leads:
            print("Nenhuma mensagem encontrada ainda.")
            print("\nAGUARDANDO MENSAGENS...")
            print("- Configure o webhook da Evolution API")
            print("- Envie uma mensagem de teste no WhatsApp")
            return

        print(f"Total de leads no sistema: {len(leads)} (mostrando ultimos 10)\n")

        for i, lead in enumerate(leads, 1):
            nome = lead.get('nome_Leed', 'N/A')
            telefone = lead.get('phone_numero', 'N/A')
            mensagem = lead.get('message', 'N/A')
            created = lead.get('created_at', 'N/A')

            # Formatar data
            try:
                dt = datetime.fromisoformat(created.replace('Z', '+00:00'))
                data_formatada = dt.strftime('%d/%m/%Y %H:%M:%S')
            except:
                data_formatada = created[:19] if created != 'N/A' else 'N/A'

            print(f"[{i}] {data_formatada}")
            print(f"    Nome: {nome}")
            print(f"    Telefone: {telefone}")
            print(f"    Mensagem: {mensagem[:80]}{'...' if len(mensagem) > 80 else ''}")
            print()

    except Exception as e:
        print(f"ERRO ao buscar mensagens: {e}")
        logger.error(f"Erro: {e}", exc_info=True)


async def verificar_logs():
    """Verifica os logs do bot."""

    print("-"*70)
    print("LOGS DO SISTEMA")
    print("-"*70 + "\n")

    try:
        # Ler últimas linhas do log
        with open('bot.log', 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            ultimas = lines[-20:] if len(lines) > 20 else lines

            if ultimas:
                print("Ultimas 20 linhas do log:\n")
                for line in ultimas:
                    print(line.strip())
            else:
                print("Arquivo de log vazio.")
    except FileNotFoundError:
        print("Arquivo bot.log nao encontrado.")
        print("O bot ainda nao foi executado ou nao gerou logs.")
    except Exception as e:
        print(f"Erro ao ler logs: {e}")


async def verificar_webhook_config():
    """Verifica configuração do webhook."""

    settings = get_settings()

    print("\n" + "-"*70)
    print("CONFIGURACAO DO WEBHOOK")
    print("-"*70 + "\n")

    print("Para receber mensagens, configure o webhook na Evolution API:\n")
    print(f"URL do Webhook: http://SEU-SERVIDOR:8000/webhook/whatsapp")
    print(f"Instancia: {settings.whatsapp_instance}")
    print(f"Evento: messages.upsert\n")

    print("Passos para configurar:")
    print("1. Acesse: {settings.whatsapp_api_url}")
    print("2. Va em: Webhooks")
    print("3. Configure:")
    print("   - URL: http://SEU-IP:8000/webhook/whatsapp")
    print("   - Eventos: messages.upsert")
    print("   - Habilite o webhook")
    print()


async def modo_monitoramento_continuo():
    """Monitora mensagens continuamente."""

    print("\n" + "="*70)
    print("MODO MONITORAMENTO CONTINUO")
    print("="*70 + "\n")
    print("Atualizando a cada 5 segundos...")
    print("Pressione Ctrl+C para parar\n")

    settings = get_settings()
    supabase = criar_supabase_client(settings.supabase_url, settings.supabase_key)

    ultimo_id = None

    try:
        while True:
            # Buscar última mensagem
            response = supabase.client.table("leads").select(
                "id, nome_Leed, phone_numero, message, created_at"
            ).order("created_at", desc=True).limit(1).execute()

            if response.data:
                lead = response.data[0]
                lead_id = lead.get('id')

                # Nova mensagem?
                if lead_id != ultimo_id:
                    ultimo_id = lead_id

                    nome = lead.get('nome_Leed', 'N/A')
                    telefone = lead.get('phone_numero', 'N/A')
                    mensagem = lead.get('message', 'N/A')

                    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] NOVA MENSAGEM!")
                    print(f"  De: {nome} ({telefone})")
                    print(f"  Mensagem: {mensagem[:100]}")
                else:
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] Aguardando... (ultima: {ultimo_id[:8]}...)")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] Nenhuma mensagem ainda...")

            await asyncio.sleep(5)

    except KeyboardInterrupt:
        print("\n\nMonitoramento interrompido.")


async def main():
    """Menu principal."""

    print("\n" + "="*70)
    print("MONITOR DE MENSAGENS - WHATSAPP BOT")
    print("="*70 + "\n")
    print("Escolha uma opcao:\n")
    print("1. Ver ultimas mensagens recebidas")
    print("2. Ver logs do sistema")
    print("3. Ver configuracao do webhook")
    print("4. Modo monitoramento continuo (atualiza a cada 5s)")
    print("5. Ver tudo (opcoes 1, 2 e 3)")
    print("0. Sair\n")

    try:
        opcao = input("Digite o numero da opcao: ").strip()

        if opcao == "1":
            await verificar_ultimas_mensagens()
        elif opcao == "2":
            await verificar_logs()
        elif opcao == "3":
            await verificar_webhook_config()
        elif opcao == "4":
            await modo_monitoramento_continuo()
        elif opcao == "5":
            await verificar_ultimas_mensagens()
            await verificar_logs()
            await verificar_webhook_config()
        elif opcao == "0":
            print("\nAte logo!")
            return
        else:
            print("\nOpcao invalida!")

        print("\n" + "="*70 + "\n")

    except KeyboardInterrupt:
        print("\n\nOperacao cancelada.")
    except Exception as e:
        print(f"\nErro: {e}")
        logger.error(f"Erro no menu: {e}", exc_info=True)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\nPrograma encerrado.")
    except Exception as e:
        print(f"\nErro critico: {e}")
        logger.error(f"Erro critico: {e}", exc_info=True)
