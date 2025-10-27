"""
Script helper para iniciar o bot do WhatsApp com verificacoes previas.

Execute: python iniciar_bot.py
"""

import sys
import os
import subprocess
from pathlib import Path

def verificar_arquivo(caminho: str) -> bool:
    """Verifica se arquivo existe."""
    return Path(caminho).exists()

def verificar_env():
    """Verifica se .env existe e tem as variaveis necessarias."""
    if not verificar_arquivo('.env'):
        print("ERRO: Arquivo .env nao encontrado!")
        print("Crie um arquivo .env com as configuracoes necessarias.")
        return False

    # Ler .env e verificar variaveis criticas
    with open('.env', 'r') as f:
        conteudo = f.read()

    variaveis_obrigatorias = [
        'OPENAI_API_KEY',
        'SUPABASE_URL',
        'SUPABASE_KEY',
        'WHATSAPP_API_KEY'
    ]

    faltando = []
    for var in variaveis_obrigatorias:
        if var not in conteudo:
            faltando.append(var)

    if faltando:
        print("ERRO: Variaveis faltando no .env:")
        for var in faltando:
            print(f"  - {var}")
        return False

    return True

def verificar_redis():
    """Verifica se Redis esta rodando (opcional)."""
    try:
        result = subprocess.run(['redis-cli', 'ping'],
                              capture_output=True,
                              text=True,
                              timeout=2)
        if 'PONG' in result.stdout:
            print("Redis: RODANDO")
            return True
    except:
        pass

    print("Redis: NAO DETECTADO (opcional - bot funciona sem Redis)")
    return False

def verificar_porta_8000():
    """Verifica se porta 8000 esta livre."""
    try:
        import socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        result = s.connect_ex(('localhost', 8000))
        s.close()

        if result == 0:
            print("AVISO: Porta 8000 ja esta em uso!")
            print("O bot pode ja estar rodando, ou outra aplicacao esta usando a porta.")
            resposta = input("Deseja continuar mesmo assim? (s/n): ").strip().lower()
            return resposta == 's'
        else:
            print("Porta 8000: LIVRE")
            return True
    except:
        print("Porta 8000: VERIFICACAO FALHOU (continuando...)")
        return True

def verificar_dependencias():
    """Verifica se requirements estao instalados."""
    try:
        import fastapi
        import langgraph
        import langchain
        import supabase
        print("Dependencias: OK")
        return True
    except ImportError as e:
        print(f"ERRO: Dependencias faltando - {e}")
        print("Execute: pip install -r requirements.txt")
        return False

def main():
    print("=" * 70)
    print("INICIALIZADOR DO BOT - CENTRO OESTE DRYWALL")
    print("=" * 70)
    print()

    print("Verificando pre-requisitos...\n")

    # Verificacoes
    checks = [
        ("Arquivo .env", verificar_env),
        ("Dependencias Python", verificar_dependencias),
        ("Porta 8000", verificar_porta_8000),
    ]

    tudo_ok = True
    for nome, funcao in checks:
        print(f"Verificando {nome}...")
        if not funcao():
            tudo_ok = False
            print(f"  FALHOU!\n")
        else:
            print()

    # Verificacao opcional
    print("Verificando Redis (opcional)...")
    verificar_redis()
    print()

    if not tudo_ok:
        print("=" * 70)
        print("ERRO: Pre-requisitos nao atendidos!")
        print("=" * 70)
        sys.exit(1)

    print("=" * 70)
    print("Tudo certo! Iniciando o bot...")
    print("=" * 70)
    print()
    print("Logs aparecera abaixo. Pressione Ctrl+C para parar o bot.\n")
    print("-" * 70)
    print()

    try:
        # Iniciar o bot
        subprocess.run([sys.executable, 'src/main.py'])
    except KeyboardInterrupt:
        print("\n\nBot encerrado pelo usuario.")
    except Exception as e:
        print(f"\n\nErro ao iniciar bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
