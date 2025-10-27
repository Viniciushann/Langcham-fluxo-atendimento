"""
Script para configurar webhook na Evolution API.

Execute após iniciar ngrok.
"""

import requests
import sys
from dotenv import load_dotenv
import os

# Carregar variáveis de ambiente
load_dotenv()

EVOLUTION_API_URL = os.getenv("WHATSAPP_API_URL")
API_KEY = os.getenv("WHATSAPP_API_KEY")
INSTANCE = os.getenv("WHATSAPP_INSTANCE")

def configurar_webhook(ngrok_url):
    """Configura webhook na Evolution API."""

    # Remover trailing slash se houver
    ngrok_url = ngrok_url.rstrip('/')

    # URL completa do webhook
    webhook_url = f"{ngrok_url}/webhook/whatsapp"

    print("=" * 60)
    print("Configurando Webhook na Evolution API")
    print("=" * 60)
    print(f"\nEvolution API: {EVOLUTION_API_URL}")
    print(f"Instância: {INSTANCE}")
    print(f"Webhook URL: {webhook_url}")
    print()

    # Endpoint para configurar webhook
    url = f"{EVOLUTION_API_URL}/webhook/set/{INSTANCE}"

    headers = {
        "Content-Type": "application/json",
        "apikey": API_KEY
    }

    payload = {
        "enabled": True,
        "url": webhook_url,
        "webhook_by_events": False,
        "events": [
            "MESSAGES_UPSERT"
        ]
    }

    try:
        print("Enviando configuração...")
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code in [200, 201]:
            print("\n✓ Webhook configurado com sucesso!")
            print(f"\nResposta da API:")
            print(response.json())

            # Verificar configuração
            print("\n" + "=" * 60)
            print("Verificando configuração...")
            verify_url = f"{EVOLUTION_API_URL}/webhook/find/{INSTANCE}"
            verify_response = requests.get(verify_url, headers=headers)

            if verify_response.status_code == 200:
                print("\n✓ Verificação concluída:")
                print(verify_response.json())

            return True
        else:
            print(f"\n✗ Erro ao configurar webhook!")
            print(f"Status Code: {response.status_code}")
            print(f"Resposta: {response.text}")
            return False

    except requests.exceptions.RequestException as e:
        print(f"\n✗ Erro de conexão: {e}")
        return False


def main():
    """Função principal."""
    print()
    print("╔" + "=" * 58 + "╗")
    print("║  Script de Configuração de Webhook - Evolution API      ║")
    print("╚" + "=" * 58 + "╝")
    print()

    # Verificar variáveis de ambiente
    if not all([EVOLUTION_API_URL, API_KEY, INSTANCE]):
        print("✗ ERRO: Variáveis de ambiente não configuradas!")
        print("\nVerifique se o arquivo .env contém:")
        print("  - WHATSAPP_API_URL")
        print("  - WHATSAPP_API_KEY")
        print("  - WHATSAPP_INSTANCE")
        sys.exit(1)

    # Solicitar URL do ngrok
    print("Primeiro, inicie o ngrok em outro terminal:")
    print("  > ngrok http 8000")
    print()
    print("Depois, copie a URL de Forwarding (exemplo: https://xxxx.ngrok-free.app)")
    print()

    ngrok_url = input("Cole a URL do ngrok aqui: ").strip()

    if not ngrok_url:
        print("\n✗ URL não pode estar vazia!")
        sys.exit(1)

    if not ngrok_url.startswith("http"):
        ngrok_url = f"https://{ngrok_url}"

    # Confirmar
    print()
    print("=" * 60)
    print("ATENÇÃO: Você vai configurar o webhook com:")
    print(f"  URL: {ngrok_url}/webhook/whatsapp")
    print("=" * 60)
    confirm = input("\nConfirmar? (s/n): ").lower()

    if confirm != 's':
        print("Operação cancelada.")
        sys.exit(0)

    # Configurar
    success = configurar_webhook(ngrok_url)

    print()
    print("=" * 60)
    if success:
        print("✓ CONFIGURAÇÃO CONCLUÍDA!")
        print()
        print("Próximos passos:")
        print("  1. Certifique-se que o FastAPI está rodando")
        print("  2. Certifique-se que o ngrok está rodando")
        print("  3. Envie uma mensagem de teste para o WhatsApp")
        print(f"     Número do bot: {os.getenv('BOT_PHONE_NUMBER', 'não configurado')}")
    else:
        print("✗ FALHA NA CONFIGURAÇÃO")
        print()
        print("Verifique:")
        print("  1. URL da Evolution API está correta")
        print("  2. API Key é válida")
        print("  3. Nome da instância está correto")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
