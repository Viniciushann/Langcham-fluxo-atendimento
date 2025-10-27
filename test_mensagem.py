"""
Script para enviar mensagem de teste via Evolution API.

Simula o cliente enviando mensagem para o bot.
"""

import requests
from dotenv import load_dotenv
import os
import sys

# Carregar variáveis de ambiente
load_dotenv()

EVOLUTION_API_URL = os.getenv("WHATSAPP_API_URL")
API_KEY = os.getenv("WHATSAPP_API_KEY")
INSTANCE = os.getenv("WHATSAPP_INSTANCE")


def enviar_mensagem(numero, mensagem):
    """Envia mensagem via Evolution API."""

    url = f"{EVOLUTION_API_URL}/message/sendText/{INSTANCE}"

    headers = {
        "Content-Type": "application/json",
        "apikey": API_KEY
    }

    payload = {
        "number": numero,
        "text": mensagem
    }

    try:
        print(f"Enviando mensagem para {numero}...")
        response = requests.post(url, json=payload, headers=headers)

        if response.status_code in [200, 201]:
            print("\n✓ Mensagem enviada com sucesso!")
            print(f"\nResposta da API:")
            print(response.json())
            return True
        else:
            print(f"\n✗ Erro ao enviar mensagem!")
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
    print("║  Script de Teste - Enviar Mensagem via Evolution API    ║")
    print("╚" + "=" * 58 + "╝")
    print()

    # Verificar variáveis de ambiente
    if not all([EVOLUTION_API_URL, API_KEY, INSTANCE]):
        print("✗ ERRO: Variáveis de ambiente não configuradas!")
        sys.exit(1)

    print("Exemplos de mensagens:")
    print("  1. Olá, preciso de informações sobre instalação de drywall")
    print("  2. Qual o preço do m² de drywall?")
    print("  3. Gostaria de agendar uma visita técnica")
    print()

    # Solicitar dados
    numero = input("Número WhatsApp (ex: 5562999999999): ").strip()

    if not numero:
        print("✗ Número não pode estar vazio!")
        sys.exit(1)

    # Adicionar código do país se necessário
    if not numero.startswith("55"):
        numero = f"55{numero}"

    print()
    mensagem = input("Mensagem: ").strip()

    if not mensagem:
        print("✗ Mensagem não pode estar vazia!")
        sys.exit(1)

    # Confirmar
    print()
    print("=" * 60)
    print("Enviando:")
    print(f"  Para: {numero}")
    print(f"  Mensagem: {mensagem}")
    print("=" * 60)

    # Enviar
    success = enviar_mensagem(numero, mensagem)

    print()
    if success:
        print("✓ Mensagem enviada!")
        print()
        print("Agora:")
        print("  1. Verifique os logs do FastAPI")
        print("  2. Verifique o ngrok interface (http://localhost:4040)")
        print("  3. Aguarde a resposta do bot no WhatsApp")
    else:
        print("✗ Falha ao enviar mensagem")

    print()


if __name__ == "__main__":
    main()
