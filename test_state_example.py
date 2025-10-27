"""
Exemplo de uso do módulo de estado.

Este arquivo demonstra como usar AgentState, enums e funções auxiliares.
Execute com: python test_state_example.py
"""

from src.models import (
    AgentState,
    TipoMensagem,
    AcaoFluxo,
    IntencaoAgendamento,
    criar_estado_inicial,
    validar_estado,
    extrair_numero_whatsapp,
    formatar_jid_whatsapp,
    tipo_mensagem_from_string,
)


def exemplo_1_criar_estado():
    """Exemplo 1: Criar e validar estado inicial"""
    print("\n" + "=" * 60)
    print("EXEMPLO 1: Criar Estado Inicial")
    print("=" * 60)

    # Criar estado inicial
    state = criar_estado_inicial()

    print(f"Estado criado com {len(state)} campos")
    print(f"Cliente existe: {state['cliente_existe']}")
    print(f"Deve processar: {state['deve_processar']}")
    print(f"Next action: '{state['next_action']}'")

    # Validar estado
    if validar_estado(state):
        print("Estado válido!")
    else:
        print("Estado inválido!")


def exemplo_2_usar_enums():
    """Exemplo 2: Usar enums"""
    print("\n" + "=" * 60)
    print("EXEMPLO 2: Usar Enums")
    print("=" * 60)

    # TipoMensagem
    print("\nTipos de Mensagem:")
    print(f"  - Áudio: {TipoMensagem.AUDIO}")
    print(f"  - Imagem: {TipoMensagem.IMAGEM}")
    print(f"  - Texto: {TipoMensagem.TEXTO}")
    print(f"  - Outros: {TipoMensagem.OUTROS}")

    # AcaoFluxo
    print("\nAções de Fluxo:")
    print(f"  - Verificar cliente: {AcaoFluxo.VERIFICAR_CLIENTE}")
    print(f"  - Processar áudio: {AcaoFluxo.PROCESSAR_AUDIO}")
    print(f"  - Processar agente: {AcaoFluxo.PROCESSAR_AGENTE}")
    print(f"  - End: {AcaoFluxo.END}")

    # IntencaoAgendamento
    print("\nIntenções de Agendamento:")
    print(f"  - Consultar: {IntencaoAgendamento.CONSULTAR}")
    print(f"  - Agendar: {IntencaoAgendamento.AGENDAR}")
    print(f"  - Cancelar: {IntencaoAgendamento.CANCELAR}")


def exemplo_3_funcoes_auxiliares():
    """Exemplo 3: Funções auxiliares"""
    print("\n" + "=" * 60)
    print("EXEMPLO 3: Funções Auxiliares")
    print("=" * 60)

    # Extrair número
    jid = "5562999999999@s.whatsapp.net"
    numero = extrair_numero_whatsapp(jid)
    print(f"\nExtrair número:")
    print(f"  JID: {jid}")
    print(f"  Número: {numero}")

    # Formatar JID
    numero_limpo = "5562888888888"
    jid_formatado = formatar_jid_whatsapp(numero_limpo)
    print(f"\nFormatar JID:")
    print(f"  Número: {numero_limpo}")
    print(f"  JID: {jid_formatado}")

    # Converter tipo de mensagem
    tipo_str = "audioMessage"
    tipo_enum = tipo_mensagem_from_string(tipo_str)
    print(f"\nConverter tipo de mensagem:")
    print(f"  String: {tipo_str}")
    print(f"  Enum: {tipo_enum}")
    print(f"  É áudio? {tipo_enum == TipoMensagem.AUDIO}")


def exemplo_4_preencher_estado():
    """Exemplo 4: Preencher estado com dados de webhook simulado"""
    print("\n" + "=" * 60)
    print("EXEMPLO 4: Preencher Estado com Webhook Simulado")
    print("=" * 60)

    # Criar estado inicial
    state = criar_estado_inicial()

    # Simular dados de webhook
    webhook_data = {
        "body": {
            "event": "messages.upsert",
            "instance": "minha-instancia",
            "data": {
                "key": {
                    "remoteJid": "5562999999999@s.whatsapp.net",
                    "id": "MSG123456",
                    "fromMe": False
                },
                "pushName": "João Silva",
                "message": {
                    "conversation": "Olá, quero agendar uma consulta"
                },
                "messageType": "conversation"
            }
        }
    }

    # Preencher estado
    state["raw_webhook_data"] = webhook_data
    state["cliente_numero"] = extrair_numero_whatsapp(
        webhook_data["body"]["data"]["key"]["remoteJid"]
    )
    state["cliente_nome"] = webhook_data["body"]["data"]["pushName"]
    state["mensagem_tipo"] = webhook_data["body"]["data"]["messageType"]
    state["mensagem_conteudo"] = webhook_data["body"]["data"]["message"]["conversation"]
    state["mensagem_id"] = webhook_data["body"]["data"]["key"]["id"]
    state["next_action"] = AcaoFluxo.VERIFICAR_CLIENTE.value

    # Exibir estado preenchido
    print(f"\nEstado preenchido:")
    print(f"  Cliente número: {state['cliente_numero']}")
    print(f"  Cliente nome: {state['cliente_nome']}")
    print(f"  Mensagem tipo: {state['mensagem_tipo']}")
    print(f"  Mensagem conteúdo: {state['mensagem_conteudo']}")
    print(f"  Mensagem ID: {state['mensagem_id']}")
    print(f"  Next action: {state['next_action']}")


def exemplo_5_fluxo_completo():
    """Exemplo 5: Simular fluxo de estados"""
    print("\n" + "=" * 60)
    print("EXEMPLO 5: Simular Fluxo de Estados")
    print("=" * 60)

    state = criar_estado_inicial()

    # 1. Receber webhook
    print("\n1. Receber webhook")
    state["next_action"] = AcaoFluxo.VERIFICAR_CLIENTE.value
    print(f"   Next action: {state['next_action']}")

    # 2. Verificar cliente (não existe)
    print("\n2. Verificar cliente")
    state["cliente_existe"] = False
    state["next_action"] = AcaoFluxo.CADASTRAR_CLIENTE.value
    print(f"   Cliente existe: {state['cliente_existe']}")
    print(f"   Next action: {state['next_action']}")

    # 3. Cadastrar cliente
    print("\n3. Cadastrar cliente")
    state["cliente_id"] = "123"
    state["cliente_existe"] = True
    state["next_action"] = AcaoFluxo.PROCESSAR_MIDIA.value
    print(f"   Cliente ID: {state['cliente_id']}")
    print(f"   Next action: {state['next_action']}")

    # 4. Processar mensagem de texto
    print("\n4. Processar mensagem")
    state["mensagem_tipo"] = TipoMensagem.TEXTO.value
    state["next_action"] = AcaoFluxo.GERENCIAR_FILA.value
    print(f"   Tipo: {state['mensagem_tipo']}")
    print(f"   Next action: {state['next_action']}")

    # 5. Gerenciar fila
    print("\n5. Gerenciar fila")
    state["fila_mensagens"] = [{"conteudo": "Olá", "timestamp": "2025-10-21T10:00:00"}]
    state["deve_processar"] = True
    state["next_action"] = AcaoFluxo.AGUARDAR_MENSAGENS.value
    print(f"   Mensagens na fila: {len(state['fila_mensagens'])}")
    print(f"   Deve processar: {state['deve_processar']}")
    print(f"   Next action: {state['next_action']}")

    # 6. Processar agente
    print("\n6. Processar agente")
    state["next_action"] = AcaoFluxo.PROCESSAR_AGENTE.value
    print(f"   Next action: {state['next_action']}")

    # 7. Fragmentar resposta
    print("\n7. Fragmentar resposta")
    state["resposta_agente"] = "Olá! Posso ajudar com o agendamento."
    state["next_action"] = AcaoFluxo.FRAGMENTAR_RESPOSTA.value
    print(f"   Resposta: {state['resposta_agente']}")
    print(f"   Next action: {state['next_action']}")

    # 8. Enviar respostas
    print("\n8. Enviar respostas")
    state["respostas_fragmentadas"] = ["Olá! Posso ajudar com o agendamento."]
    state["next_action"] = AcaoFluxo.ENVIAR_RESPOSTAS.value
    print(f"   Fragmentos: {len(state['respostas_fragmentadas'])}")
    print(f"   Next action: {state['next_action']}")

    # 9. Finalizar
    print("\n9. Finalizar")
    state["next_action"] = AcaoFluxo.END.value
    print(f"   Next action: {state['next_action']}")

    print("\nFluxo completo simulado com sucesso!")


if __name__ == "__main__":
    print("=" * 60)
    print("DEMONSTRAÇÃO DO MÓDULO DE ESTADO")
    print("=" * 60)

    exemplo_1_criar_estado()
    exemplo_2_usar_enums()
    exemplo_3_funcoes_auxiliares()
    exemplo_4_preencher_estado()
    exemplo_5_fluxo_completo()

    print("\n" + "=" * 60)
    print("TODOS OS EXEMPLOS EXECUTADOS COM SUCESSO!")
    print("=" * 60)
    print("\nPróximo passo: Implementar Fase 2 - Clientes Externos")
    print("Consulte AGENTE LANGGRAPH.txt para detalhes.\n")
