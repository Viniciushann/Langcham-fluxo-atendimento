"""
Script para corrigir a URL do webhook na Evolution API.

Este script atualiza a URL do webhook de:
  https://bot.automacaovn.shop/webhook
Para:
  https://bot.automacaovn.shop/webhook/whatsapp
"""

import requests
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

EVOLUTION_API_URL = os.getenv("WHATSAPP_API_URL")
API_KEY = os.getenv("WHATSAPP_API_KEY")
INSTANCE = os.getenv("WHATSAPP_INSTANCE")

# URL correta do webhook
WEBHOOK_URL = "https://bot.automacaovn.shop/webhook/whatsapp"

def fix_webhook():
    """Atualiza a URL do webhook na Evolution API."""

    print("=" * 70)
    print("CORRIGINDO URL DO WEBHOOK NA EVOLUTION API")
    print("=" * 70)
    print()
    print(f"Evolution API: {EVOLUTION_API_URL}")
    print(f"Instância: {INSTANCE}")
    print(f"Nova URL do webhook: {WEBHOOK_URL}")
    print()

    # Endpoint para configurar webhook
    url = f"{EVOLUTION_API_URL}/webhook/set/{INSTANCE}"

    headers = {
        "Content-Type": "application/json",
        "apikey": API_KEY
    }

    payload = {
        "enabled": True,
        "url": WEBHOOK_URL,
        "webhookByEvents": False,
        "webhookBase64": True,
        "events": [
            "MESSAGES_UPSERT",
            "MESSAGES_UPDATE",
            "SEND_MESSAGE"
        ]
    }

    try:
        print(">> Enviando nova configuracao...")
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code in [200, 201]:
            print()
            print("=" * 70)
            print("[OK] WEBHOOK ATUALIZADO COM SUCESSO!")
            print("=" * 70)
            print()
            print("Resposta da API:")
            print(response.json())
            print()

            # Verificar configuração
            print("=" * 70)
            print("Verificando nova configuracao...")
            print("=" * 70)
            verify_url = f"{EVOLUTION_API_URL}/webhook/find/{INSTANCE}"
            verify_response = requests.get(verify_url, headers=headers)

            if verify_response.status_code == 200:
                config = verify_response.json()
                print()
                print(f"[OK] URL configurada: {config.get('url')}")
                print(f"[OK] Webhook ativo: {config.get('enabled')}")
                print(f"[OK] Base64 ativo: {config.get('webhookBase64')}")
                print(f"[OK] Eventos: {', '.join(config.get('events', []))}")
                print()

            print("=" * 70)
            print("CONFIGURACAO CONCLUIDA!")
            print("=" * 70)
            print()
            print("Próximos passos:")
            print("  1. Envie uma mensagem de teste para o WhatsApp")
            print(f"     Número do bot: {os.getenv('BOT_PHONE_NUMBER')}")
            print("  2. Verifique os logs do bot para confirmar recebimento")
            print()

            return True

        else:
            print()
            print("=" * 70)
            print("❌ ERRO AO ATUALIZAR WEBHOOK")
            print("=" * 70)
            print(f"Status Code: {response.status_code}")
            print(f"Resposta: {response.text}")
            print()
            return False

    except Exception as e:
        print()
        print("=" * 70)
        print("❌ ERRO DE CONEXÃO")
        print("=" * 70)
        print(f"Erro: {str(e)}")
        print()
        print("Verifique:")
        print("  1. URL da Evolution API está correta no .env")
        print("  2. API Key é válida")
        print("  3. Nome da instância está correto")
        print()
        return False


if __name__ == "__main__":
    fix_webhook()
