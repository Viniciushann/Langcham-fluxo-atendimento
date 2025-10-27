"""
Teste dos nós de webhook.

NOTA: Para executar, é necessário:
1. Instalar dependências: pip install -r requirements.txt
2. Configurar .env com credenciais do Supabase
"""

import asyncio
import sys

# Comentado até instalar dependências
# from src.nodes.webhook import validar_webhook, verificar_cliente, cadastrar_cliente
# from src.models import criar_estado_inicial, AcaoFluxo


# ========== EXEMPLOS DE USO ==========

def exemplo_webhook_data():
    """
    Exemplo de estrutura de webhook da Evolution API.
    """
    print("\n" + "=" * 60)
    print("EXEMPLO: Estrutura de Webhook")
    print("=" * 60)

    webhook_exemplo = {
        "body": {
            "event": "messages.upsert",
            "instance": "minha-instancia",
            "data": {
                "key": {
                    "remoteJid": "5562999999999@s.whatsapp.net",
                    "id": "MSG123456ABC",
                    "fromMe": False
                },
                "pushName": "João Silva",
                "message": {
                    "conversation": "Olá, quero agendar uma consulta"
                },
                "messageType": "conversation",
                "messageTimestamp": 1729522800
            }
        }
    }

    print("\nWebhook recebido:")
    print(f"  Remote JID: {webhook_exemplo['body']['data']['key']['remoteJid']}")
    print(f"  Push Name: {webhook_exemplo['body']['data']['pushName']}")
    print(f"  Message Type: {webhook_exemplo['body']['data']['messageType']}")
    print(f"  Message: {webhook_exemplo['body']['data']['message']['conversation']}")

    return webhook_exemplo


def exemplo_fluxo_completo():
    """
    Exemplo do fluxo completo: validar → verificar → cadastrar.
    """
    print("\n" + "=" * 60)
    print("EXEMPLO: Fluxo Completo")
    print("=" * 60)

    codigo_exemplo = '''
async def processar_webhook_completo():
    """Fluxo completo de processamento de webhook"""

    from src.nodes.webhook import (
        validar_webhook,
        verificar_cliente,
        cadastrar_cliente
    )
    from src.models import criar_estado_inicial, AcaoFluxo

    # 1. Criar estado inicial
    state = criar_estado_inicial()

    # 2. Webhook simulado
    state["raw_webhook_data"] = {
        "body": {
            "event": "messages.upsert",
            "instance": "minha-instancia",
            "data": {
                "key": {
                    "remoteJid": "5562999999999@s.whatsapp.net",
                    "id": "MSG123",
                    "fromMe": False
                },
                "pushName": "João Silva",
                "message": {
                    "conversation": "Olá, preciso de ajuda"
                },
                "messageType": "conversation",
                "messageTimestamp": 1729522800
            }
        }
    }

    # 3. ETAPA 1: Validar webhook
    print("\\n[1] Validando webhook...")
    state = await validar_webhook(state)

    if state["next_action"] == AcaoFluxo.END.value:
        print("Webhook filtrado ou inválido")
        return

    print(f"✓ Webhook validado")
    print(f"  Cliente: {state['cliente_nome']}")
    print(f"  Número: {state['cliente_numero']}")
    print(f"  Tipo: {state['mensagem_tipo']}")
    print(f"  Próxima ação: {state['next_action']}")

    # 4. ETAPA 2: Verificar cliente
    print("\\n[2] Verificando cliente no banco...")
    state = await verificar_cliente(state)

    if state.get("erro"):
        print(f"✗ Erro: {state['erro']}")
        return

    if state["cliente_existe"]:
        print(f"✓ Cliente encontrado!")
        print(f"  ID: {state['cliente_id']}")
        print(f"  Próxima ação: {state['next_action']}")
    else:
        print(f"✓ Cliente não encontrado")
        print(f"  Próxima ação: {state['next_action']}")

        # 5. ETAPA 3: Cadastrar cliente (se necessário)
        if state["next_action"] == AcaoFluxo.CADASTRAR_CLIENTE.value:
            print("\\n[3] Cadastrando novo cliente...")
            state = await cadastrar_cliente(state)

            if state.get("erro"):
                print(f"✗ Erro: {state['erro']}")
                return

            print(f"✓ Cliente cadastrado!")
            print(f"  ID: {state['cliente_id']}")
            print(f"  Próxima ação: {state['next_action']}")

    print("\\n" + "=" * 60)
    print("Fluxo concluído com sucesso!")
    print("=" * 60)
    print(f"\\nEstado final:")
    print(f"  Cliente existe: {state['cliente_existe']}")
    print(f"  Cliente ID: {state['cliente_id']}")
    print(f"  Cliente nome: {state['cliente_nome']}")
    print(f"  Cliente número: {state['cliente_numero']}")
    print(f"  Próxima ação: {state['next_action']}")

# Executar
asyncio.run(processar_webhook_completo())
    '''

    print(codigo_exemplo)


def exemplo_validar_webhook():
    """
    Exemplo da função validar_webhook.
    """
    print("\n" + "=" * 60)
    print("EXEMPLO: validar_webhook()")
    print("=" * 60)

    codigo_exemplo = '''
from src.nodes.webhook import validar_webhook
from src.models import criar_estado_inicial

# Criar estado inicial
state = criar_estado_inicial()

# Adicionar webhook
state["raw_webhook_data"] = {
    "body": {
        "data": {
            "key": {
                "remoteJid": "5562999999999@s.whatsapp.net",
                "id": "MSG123",
                "fromMe": False
            },
            "pushName": "João Silva",
            "message": {"conversation": "Olá"},
            "messageType": "conversation"
        }
    }
}

# Validar
state = await validar_webhook(state)

# Verificar resultado
print(f"Cliente número: {state['cliente_numero']}")
print(f"Cliente nome: {state['cliente_nome']}")
print(f"Tipo mensagem: {state['mensagem_tipo']}")
print(f"Próxima ação: {state['next_action']}")

# Saída esperada:
# Cliente número: 5562999999999
# Cliente nome: João Silva
# Tipo mensagem: conversation
# Próxima ação: verificar_cliente
    '''

    print(codigo_exemplo)


def exemplo_verificar_cliente():
    """
    Exemplo da função verificar_cliente.
    """
    print("\n" + "=" * 60)
    print("EXEMPLO: verificar_cliente()")
    print("=" * 60)

    codigo_exemplo = '''
from src.nodes.webhook import verificar_cliente

# Estado após validar_webhook
state = {
    "cliente_numero": "5562999999999",
    "cliente_nome": "João Silva",
    # ... outros campos
}

# Verificar se cliente existe no Supabase
state = await verificar_cliente(state)

# Verificar resultado
if state["cliente_existe"]:
    print(f"Cliente encontrado: ID {state['cliente_id']}")
    print(f"Próxima ação: {state['next_action']}")  # processar_midia
else:
    print("Cliente não encontrado")
    print(f"Próxima ação: {state['next_action']}")  # cadastrar_cliente
    '''

    print(codigo_exemplo)


def exemplo_cadastrar_cliente():
    """
    Exemplo da função cadastrar_cliente.
    """
    print("\n" + "=" * 60)
    print("EXEMPLO: cadastrar_cliente()")
    print("=" * 60)

    codigo_exemplo = '''
from src.nodes.webhook import cadastrar_cliente

# Estado com dados do novo cliente
state = {
    "cliente_nome": "João Silva",
    "cliente_numero": "5562999999999",
    "mensagem_base64": "Olá, preciso de ajuda",
    "mensagem_tipo": "conversation",
    # ... outros campos
}

# Cadastrar cliente
state = await cadastrar_cliente(state)

# Verificar resultado
if state.get("erro"):
    print(f"Erro: {state['erro']}")
else:
    print(f"Cliente cadastrado: ID {state['cliente_id']}")
    print(f"Cliente existe: {state['cliente_existe']}")  # True
    print(f"Próxima ação: {state['next_action']}")  # processar_midia
    '''

    print(codigo_exemplo)


def exemplo_filtro_bot():
    """
    Exemplo de filtro de mensagens do próprio bot.
    """
    print("\n" + "=" * 60)
    print("EXEMPLO: Filtro de Mensagens do Bot")
    print("=" * 60)

    codigo_exemplo = '''
# Webhook com mensagem do próprio bot
state["raw_webhook_data"] = {
    "body": {
        "data": {
            "key": {
                "remoteJid": "555195877046@s.whatsapp.net",  # Número do bot
                "fromMe": True
            }
        }
    }
}

# Validar
state = await validar_webhook(state)

# Resultado: mensagem filtrada
print(f"Próxima ação: {state['next_action']}")  # END

# A mensagem é ignorada porque é do próprio bot
    '''

    print(codigo_exemplo)


def exemplo_tratamento_erros():
    """
    Exemplo de tratamento de erros.
    """
    print("\n" + "=" * 60)
    print("EXEMPLO: Tratamento de Erros")
    print("=" * 60)

    codigo_exemplo = '''
# Webhook inválido
state = {
    "raw_webhook_data": {}  # Vazio
}

state = await validar_webhook(state)

if state.get("erro"):
    print(f"Erro detectado: {state['erro']}")
    print(f"Próxima ação: {state['next_action']}")  # END

# Erro ao buscar cliente (ex: Supabase offline)
state = {
    "cliente_numero": "5562999999999"
}

state = await verificar_cliente(state)

if state.get("erro"):
    print(f"Erro: {state['erro']}")
    print(f"Detalhes: {state.get('erro_detalhes')}")
    print(f"Próxima ação: {state['next_action']}")  # END
    '''

    print(codigo_exemplo)


# ========== MAIN ==========

if __name__ == "__main__":
    print("=" * 60)
    print("EXEMPLOS DE USO DOS NÓS DE WEBHOOK")
    print("=" * 60)
    print("\nNOTA: Para executar estes exemplos:")
    print("  1. pip install -r requirements.txt")
    print("  2. Configure .env com credenciais Supabase")
    print("\n" + "=" * 60)

    exemplo_webhook_data()
    exemplo_validar_webhook()
    exemplo_verificar_cliente()
    exemplo_cadastrar_cliente()
    exemplo_filtro_bot()
    exemplo_tratamento_erros()
    exemplo_fluxo_completo()

    print("\n" + "=" * 60)
    print("DOCUMENTAÇÃO COMPLETA")
    print("=" * 60)
    print("\nConsulte o arquivo:")
    print("  src/nodes/webhook.py")
    print("\nPara ver docstrings completas de cada função.")
    print("\n" + "=" * 60)
