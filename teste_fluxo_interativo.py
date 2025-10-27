"""
Teste Interativo dos Nós - Modo Script Python

Alternativa ao Jupyter Notebook para testar nós individualmente.
Similar ao fluxo do n8n, mas em Python puro.

USO:
    python teste_fluxo_interativo.py

REQUISITOS:
    - pip install -r requirements.txt
    - Configurar .env com credenciais
"""

import asyncio
import sys
from pprint import pprint
from datetime import datetime


def print_header(title: str):
    """Imprime cabeçalho formatado"""
    print("\n" + "=" * 60)
    print(f"🔍 {title}")
    print("=" * 60)


def print_output(data: dict, title: str = "OUTPUT"):
    """Imprime saída formatada"""
    print(f"\n📤 {title}:")
    print("-" * 60)
    for key, value in data.items():
        if isinstance(value, str) and len(value) > 60:
            print(f"✓ {key}: {value[:60]}...")
        else:
            print(f"✓ {key}: {value}")
    print("=" * 60)


async def testar_fluxo_completo():
    """
    Testa o fluxo completo nó por nó.
    """
    print("\n" + "=" * 60)
    print("🧪 TESTE INTERATIVO DOS NÓS - WhatsApp Bot")
    print("=" * 60)
    print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # ========== INPUT: Webhook Simulado ==========
    print_header("INPUT - Webhook Recebido")

    webhook_data = {
        "body": {
            "event": "messages.upsert",
            "instance": "test-instance",
            "data": {
                "key": {
                    "remoteJid": "5562999999999@s.whatsapp.net",
                    "id": "MSG123456ABC",
                    "fromMe": False
                },
                "pushName": "João Silva",
                "message": {
                    "conversation": "Olá, quero saber sobre os serviços de drywall e gesso. Vocês fazem orçamento?"
                },
                "messageType": "conversation",
                "messageTimestamp": 1729522800
            }
        }
    }

    print(f"\n📱 Webhook de: {webhook_data['body']['data']['pushName']}")
    print(f"📞 Número: {webhook_data['body']['data']['key']['remoteJid']}")
    print(f"💬 Mensagem: {webhook_data['body']['data']['message']['conversation']}")
    print(f"📧 Tipo: {webhook_data['body']['data']['messageType']}")

    # Estado inicial
    state = {
        "raw_webhook_data": webhook_data,
        "next_action": ""
    }

    input("\\n➡️  Pressione ENTER para continuar para o NÓ 1...")

    # ========== NÓ 1: validar_webhook ==========
    print_header("NÓ 1: validar_webhook")

    # Importar e executar (comentado até instalar dependências)
    # from src.nodes.webhook import validar_webhook
    # state = await validar_webhook(state)

    # Simulação do resultado
    state.update({
        "cliente_numero": "5562999999999",
        "cliente_nome": "João Silva",
        "mensagem_tipo": "conversation",
        "mensagem_id": "MSG123456ABC",
        "mensagem_base64": webhook_data['body']['data']['message']['conversation'],
        "mensagem_from_me": False,
        "next_action": "verificar_cliente"
    })

    print_output({
        "cliente_numero": state["cliente_numero"],
        "cliente_nome": state["cliente_nome"],
        "mensagem_tipo": state["mensagem_tipo"],
        "next_action": state["next_action"]
    }, "OUTPUT do validar_webhook")

    input("\\n➡️  Pressione ENTER para continuar para o NÓ 2...")

    # ========== NÓ 2: verificar_cliente ==========
    print_header("NÓ 2: verificar_cliente")

    print(f"\n📥 INPUT: Buscando cliente {state['cliente_numero']}")

    # Importar e executar (comentado até instalar dependências)
    # from src.nodes.webhook import verificar_cliente
    # state = await verificar_cliente(state)

    # Simulação: Cliente NÃO encontrado
    state.update({
        "cliente_existe": False,
        "cliente_id": None,
        "next_action": "cadastrar_cliente"
    })

    print_output({
        "cliente_existe": state["cliente_existe"],
        "cliente_id": state["cliente_id"],
        "next_action": state["next_action"]
    }, "OUTPUT do verificar_cliente")

    # ========== NÓ 3: cadastrar_cliente (se necessário) ==========
    if not state["cliente_existe"]:
        input("\\n➡️  Cliente não existe. Pressione ENTER para cadastrar...")

        print_header("NÓ 3: cadastrar_cliente")

        print(f"\n📥 INPUT: Cadastrando {state['cliente_nome']}")

        # Importar e executar (comentado até instalar dependências)
        # from src.nodes.webhook import cadastrar_cliente
        # state = await cadastrar_cliente(state)

        # Simulação
        state.update({
            "cliente_id": "novo_cliente_xyz789",
            "cliente_existe": True,
            "next_action": "processar_midia"
        })

        print_output({
            "cliente_id": state["cliente_id"],
            "cliente_existe": state["cliente_existe"],
            "next_action": state["next_action"]
        }, "OUTPUT do cadastrar_cliente")

    input("\\n➡️  Pressione ENTER para continuar para o NÓ 4...")

    # ========== NÓ 4: processar_texto ==========
    print_header("NÓ 4: processar_texto")

    print(f"\n📥 INPUT: {state['mensagem_base64'][:50]}...")

    # Importar e executar (comentado até instalar dependências)
    # from src.nodes.media import processar_texto
    # state = processar_texto(state)

    # Simulação
    state.update({
        "mensagem_conteudo": state["mensagem_base64"],
        "mensagem_transcrita": state["mensagem_base64"],
        "next_action": "gerenciar_fila"
    })

    print_output({
        "mensagem_conteudo": state["mensagem_conteudo"][:50] + "...",
        "next_action": state["next_action"]
    }, "OUTPUT do processar_texto")

    input("\\n➡️  Pressione ENTER para continuar para o NÓ 5...")

    # ========== NÓ 5: gerenciar_fila ==========
    print_header("NÓ 5: gerenciar_fila")

    print(f"\n📥 INPUT: Cliente {state['cliente_numero']}")

    # Importar e executar (comentado até instalar dependências)
    # from src.nodes.queue import gerenciar_fila
    # state = await gerenciar_fila(state)

    # Simulação
    state.update({
        "fila_mensagens": [
            {
                "conteudo": state["mensagem_conteudo"],
                "timestamp": "2025-10-21T10:00:00",
                "tipo": state["mensagem_tipo"]
            }
        ],
        "deve_processar": True,
        "next_action": "aguardar_mensagens"
    })

    print_output({
        "mensagens_na_fila": len(state["fila_mensagens"]),
        "deve_processar": state["deve_processar"],
        "next_action": state["next_action"]
    }, "OUTPUT do gerenciar_fila")

    input("\\n➡️  Pressione ENTER para ver estado final...")

    # ========== ESTADO FINAL ==========
    print_header("ESTADO COMPLETO FINAL")

    print("\n🔍 Informações do Cliente:")
    print(f"  - Número: {state.get('cliente_numero')}")
    print(f"  - Nome: {state.get('cliente_nome')}")
    print(f"  - Existe: {state.get('cliente_existe')}")
    print(f"  - ID: {state.get('cliente_id')}")

    print("\n💬 Informações da Mensagem:")
    print(f"  - Tipo: {state.get('mensagem_tipo')}")
    print(f"  - Conteúdo: {state.get('mensagem_conteudo', '')[:60]}...")
    print(f"  - ID: {state.get('mensagem_id')}")

    print("\n📋 Fila:")
    print(f"  - Mensagens: {len(state.get('fila_mensagens', []))}")
    print(f"  - Deve processar: {state.get('deve_processar')}")

    print("\n➡️  Fluxo:")
    print(f"  - Próxima ação: {state.get('next_action')}")

    if state.get('erro'):
        print("\n❌ Erro:")
        print(f"  - Mensagem: {state.get('erro')}")

    print("\n" + "=" * 60)
    print("✅ Teste concluído com sucesso!")
    print("=" * 60)

    # Resumo do fluxo
    print("\n📊 RESUMO DO FLUXO EXECUTADO:")
    print("\n1. ✅ validar_webhook")
    print("   └─ Extraiu dados do webhook")
    print("\n2. ✅ verificar_cliente")
    print("   └─ Cliente não encontrado")
    print("\n3. ✅ cadastrar_cliente")
    print(f"   └─ Cliente cadastrado: ID {state.get('cliente_id')}")
    print("\n4. ✅ processar_texto")
    print("   └─ Mensagem processada")
    print("\n5. ✅ gerenciar_fila")
    print("   └─ Adicionado à fila Redis")
    print("\n➡️  Próximo: aguardar_mensagens (13 segundos)")
    print("=" * 60)


async def testar_cenario_cliente_existente():
    """
    Testa cenário onde cliente já existe.
    """
    print("\n" + "=" * 60)
    print("🧪 CENÁRIO 2: Cliente Existente")
    print("=" * 60)

    # Webhook
    webhook_data = {
        "body": {
            "data": {
                "key": {
                    "remoteJid": "5562888888888@s.whatsapp.net",
                    "id": "MSG999",
                    "fromMe": False
                },
                "pushName": "Maria Santos",
                "message": {"conversation": "Olá novamente!"},
                "messageType": "conversation"
            }
        }
    }

    state = {
        "raw_webhook_data": webhook_data,
        "cliente_numero": "5562888888888",
        "cliente_nome": "Maria Santos",
        "mensagem_tipo": "conversation",
        "next_action": "verificar_cliente"
    }

    print("\n➡️  Cliente: Maria Santos (já cadastrada)")

    # verificar_cliente
    state.update({
        "cliente_existe": True,
        "cliente_id": "cliente_existente_abc",
        "next_action": "processar_midia"
    })

    print(f"\n✅ Cliente encontrado: ID {state['cliente_id']}")
    print(f"➡️  Próxima ação: {state['next_action']}")
    print("\n⏭️  Pula cadastro, vai direto para processar_midia")
    print("=" * 60)


def menu():
    """Menu interativo"""
    print("\n" + "=" * 60)
    print("🧪 TESTE INTERATIVO DOS NÓS")
    print("=" * 60)
    print("\nEscolha uma opção:")
    print("\n1. Testar fluxo completo (cliente novo)")
    print("2. Testar cenário: cliente existente")
    print("3. Sair")
    print("\n" + "=" * 60)

    escolha = input("\nEscolha (1-3): ").strip()

    if escolha == "1":
        asyncio.run(testar_fluxo_completo())
        menu()
    elif escolha == "2":
        asyncio.run(testar_cenario_cliente_existente())
        menu()
    elif escolha == "3":
        print("\n👋 Até logo!")
        sys.exit(0)
    else:
        print("\n❌ Opção inválida!")
        menu()


if __name__ == "__main__":
    print("""
    ===========================================================

         TESTE INTERATIVO DOS NOS - WhatsApp Bot

      Teste cada no individualmente, similar ao n8n

    ===========================================================
    """)

    print("\n📝 NOTA:")
    print("  Este script simula o comportamento dos nós.")
    print("  Para usar os nós reais, descomente os imports e")
    print("  instale as dependências: pip install -r requirements.txt")
    print("\n" + "=" * 60)

    menu()
