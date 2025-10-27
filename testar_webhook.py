"""
Script para testar se o webhook do bot esta funcionando.

Execute: python testar_webhook.py
"""

import requests
import json
from datetime import datetime

def testar_health():
    """Testa se o bot esta rodando."""
    print("\n" + "="*70)
    print("TESTE 1: Bot esta rodando?")
    print("="*70 + "\n")

    try:
        response = requests.get("http://localhost:8001/health", timeout=5)

        if response.status_code == 200:
            data = response.json()
            print("[OK] Bot esta RODANDO!")
            print(f"  Status: {data.get('status')}")
            print(f"  Instancia: {data.get('whatsapp_instance')}")
            print(f"  Numero: {data.get('bot_number')}")
            return True
        else:
            print(f"[ERRO] Bot respondeu com status {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("[ERRO] Bot NAO esta rodando!")
        print("  Execute: python -m uvicorn src.main:app --host 0.0.0.0 --port 8001")
        return False
    except Exception as e:
        print(f"[ERRO] Erro ao conectar: {e}")
        return False


def testar_webhook():
    """Testa o endpoint de webhook enviando uma mensagem simulada."""
    print("\n" + "="*70)
    print("TESTE 2: Webhook esta funcionando?")
    print("="*70 + "\n")

    # Dados simulados de uma mensagem do WhatsApp
    payload = {
        "event": "messages.upsert",
        "instance": "Centro_oeste_draywal",
        "data": {
            "key": {
                "remoteJid": "5562999999999@s.whatsapp.net",
                "fromMe": False,
                "id": f"TEST_{datetime.now().timestamp()}"
            },
            "message": {
                "conversation": "Ola! Quanto custa a instalacao de drywall? Este e um TESTE do webhook."
            },
            "messageType": "conversation",
            "pushName": "Teste Automatico",
            "messageTimestamp": int(datetime.now().timestamp())
        }
    }

    print("Enviando mensagem de teste para o webhook...")
    print(f"URL: http://localhost:8001/webhook/whatsapp")
    print(f"Payload: {json.dumps(payload, indent=2)}\n")

    try:
        response = requests.post(
            "http://localhost:8001/webhook/whatsapp",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}\n")

        if response.status_code == 200:
            print("[OK] Webhook funcionou!")
            print("\nAgora verifique:")
            print("1. Os logs do bot (deve mostrar 'Webhook recebido!')")
            print("2. O Supabase (deve ter a mensagem de teste)")
            print("3. O WhatsApp (deve enviar resposta para 5562999999999)")
            return True
        else:
            print(f"[ERRO] Webhook retornou status {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("[ERRO] Nao conseguiu conectar ao webhook!")
        print("  Verifique se o bot esta rodando na porta 8001")
        return False
    except Exception as e:
        print(f"[ERRO] Erro ao testar webhook: {e}")
        return False


def verificar_porta():
    """Verifica qual porta o bot esta usando."""
    print("\n" + "="*70)
    print("TESTE 3: Em qual porta o bot esta?")
    print("="*70 + "\n")

    portas = [8000, 8001, 8080]

    for porta in portas:
        try:
            response = requests.get(f"http://localhost:{porta}/health", timeout=2)
            if response.status_code == 200:
                print(f"[OK] Bot encontrado na porta {porta}!")
                return porta
        except:
            print(f"[ ] Porta {porta}: Nao encontrado")

    print("\n[ERRO] Bot nao encontrado em nenhuma porta comum!")
    return None


def main():
    """Executa todos os testes."""
    print("\n" + "="*70)
    print("TESTADOR DE WEBHOOK - BOT WHATSAPP")
    print("="*70)
    print(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

    # Teste 1: Bot rodando?
    bot_ok = testar_health()

    if not bot_ok:
        print("\n" + "="*70)
        print("DIAGNOSTICO: Bot nao esta rodando")
        print("="*70)
        verificar_porta()
        print("\nPara iniciar o bot, execute:")
        print("  python -m uvicorn src.main:app --host 0.0.0.0 --port 8001")
        return

    # Teste 2: Webhook funciona?
    webhook_ok = testar_webhook()

    # Resumo final
    print("\n" + "="*70)
    print("RESUMO DOS TESTES")
    print("="*70)
    print(f"Bot rodando: {'[OK]' if bot_ok else '[ERRO]'}")
    print(f"Webhook funcionando: {'[OK]' if webhook_ok else '[ERRO]'}")

    if bot_ok and webhook_ok:
        print("\n[SUCESSO] Tudo esta funcionando!")
        print("\nProximo passo:")
        print("1. Configure o webhook na Evolution API para apontar para:")
        print("   http://SEU-IP-PUBLICO:8001/webhook/whatsapp")
        print("2. Ou use ngrok para expor localmente:")
        print("   ngrok http 8001")
    else:
        print("\n[ATENCAO] Alguns testes falharam. Verifique os erros acima.")

    print("\n" + "="*70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTeste interrompido pelo usuario.")
    except Exception as e:
        print(f"\n\nErro critico: {e}")
