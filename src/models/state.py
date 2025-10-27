"""
Modelos e tipos para o estado do agente LangGraph.

Este módulo define o estado compartilhado entre todos os nós do grafo,
além de enums auxiliares para controle de fluxo.
"""

from __future__ import annotations

from typing import TypedDict, Annotated, Sequence, Optional, List, Dict, Any
from langchain_core.messages import BaseMessage
from enum import Enum
import operator


# ========== ENUMS ==========

class TipoMensagem(str, Enum):
    """
    Tipos de mensagens suportadas pelo bot.

    Os valores correspondem aos tipos de mensagem da Evolution API.
    """
    AUDIO = "audioMessage"
    IMAGEM = "imageMessage"
    TEXTO = "conversation"
    VIDEO = "videoMessage"
    DOCUMENTO = "documentMessage"
    STICKER = "stickerMessage"
    OUTROS = "outros"

    def __str__(self) -> str:
        """Retorna o valor do enum como string"""
        return self.value


class AcaoFluxo(str, Enum):
    """
    Ações possíveis no fluxo do grafo.

    Define os próximos passos que o grafo deve executar.
    """
    # Fase de recepção
    VERIFICAR_CLIENTE = "verificar_cliente"
    CADASTRAR_CLIENTE = "cadastrar_cliente"

    # Fase de processamento de mídia
    PROCESSAR_MIDIA = "processar_midia"
    PROCESSAR_AUDIO = "processar_audio"
    PROCESSAR_IMAGEM = "processar_imagem"
    PROCESSAR_TEXTO = "processar_texto"
    PROCESSAR_VIDEO = "processar_video"

    # Fase de fila
    GERENCIAR_FILA = "gerenciar_fila"
    AGUARDAR_MENSAGENS = "aguardar_mensagens"

    # Fase de agente
    PROCESSAR_AGENTE = "processar_agente"

    # Fase de resposta
    FRAGMENTAR_RESPOSTA = "fragmentar_resposta"
    ENVIAR_RESPOSTAS = "enviar_respostas"

    # Controle
    END = "END"
    ERRO = "erro"

    def __str__(self) -> str:
        """Retorna o valor do enum como string"""
        return self.value


class IntencaoAgendamento(str, Enum):
    """
    Intenções possíveis para o agendamento.

    Usadas pela ferramenta de agendamento para determinar a ação.
    """
    CONSULTAR = "consultar"
    AGENDAR = "agendar"
    CANCELAR = "cancelar"
    ATUALIZAR = "atualizar"
    REAGENDAR = "reagendar"
    LISTAR = "listar"

    def __str__(self) -> str:
        """Retorna o valor do enum como string"""
        return self.value


# ========== ESTADO DO AGENTE ==========

class AgentState(TypedDict, total=False):
    """
    Estado compartilhado entre todos os nós do grafo LangGraph.

    Este estado é passado e modificado por cada nó do grafo,
    permitindo comunicação e persistência de dados entre as etapas.

    Attributes:
        # Dados do webhook
        raw_webhook_data: Dados brutos recebidos do webhook Evolution API

        # Dados do cliente
        cliente_numero: Número do cliente (sem @s.whatsapp.net)
        cliente_nome: Nome do cliente (pushName)
        cliente_id: ID do cliente no banco Supabase
        cliente_existe: Se o cliente já está cadastrado
        cliente_ultima_mensagem: Timestamp da última mensagem

        # Dados da mensagem
        mensagem_tipo: Tipo da mensagem (audio, imagem, texto, etc)
        mensagem_conteudo: Conteúdo processado da mensagem
        mensagem_base64: Dados em base64 (para mídia)
        mensagem_transcrita: Texto transcrito de áudio ou descrição de imagem
        texto_processado: Texto final pronto para o agente (vindo de qualquer mídia)
        mensagem_id: ID único da mensagem
        mensagem_timestamp: Timestamp da mensagem
        mensagem_from_me: Se a mensagem foi enviada pelo bot

        # Fila de mensagens
        fila_mensagens: Lista de mensagens agrupadas para processamento
        deve_processar: Se deve processar as mensagens agora ou aguardar

        # Processamento do agente (LangChain)
        messages: Histórico de mensagens do agente (com reducer operator.add)

        # Resposta
        resposta_agente: Resposta completa gerada pelo agente
        respostas_fragmentadas: Lista de fragmentos da resposta para envio

        # Agendamento
        agendamento_intencao: Intenção detectada (consultar, agendar, etc)
        agendamento_dados: Dados do agendamento (nome, telefone, data, etc)
        agendamento_resultado: Resultado da operação de agendamento

        # Controle de fluxo
        next_action: Próxima ação a ser executada pelo grafo
        erro: Mensagem de erro (se houver)
        erro_detalhes: Detalhes adicionais do erro
    """

    # ========== DADOS DO WEBHOOK ==========
    raw_webhook_data: Dict[str, Any]

    # ========== DADOS DO CLIENTE ==========
    cliente_numero: str
    cliente_nome: str
    cliente_id: Optional[str]
    cliente_existe: bool
    cliente_ultima_mensagem: Optional[str]

    # ========== DADOS DA MENSAGEM ==========
    mensagem_tipo: str
    mensagem_conteudo: str
    mensagem_base64: Optional[str]
    mensagem_transcrita: Optional[str]
    texto_processado: str  # Texto pronto para o agente (de texto/áudio/imagem)
    mensagem_id: str
    mensagem_timestamp: Optional[int]
    mensagem_from_me: bool

    # ========== FILA DE MENSAGENS ==========
    fila_mensagens: List[Dict[str, Any]]
    deve_processar: bool

    # ========== PROCESSAMENTO DO AGENTE ==========
    # Annotated com operator.add permite acumular mensagens
    messages: Annotated[Sequence[BaseMessage], operator.add]

    # ========== RESPOSTA ==========
    resposta_agente: str
    respostas_fragmentadas: List[str]

    # ========== AGENDAMENTO ==========
    agendamento_intencao: Optional[str]
    agendamento_dados: Optional[Dict[str, Any]]
    agendamento_resultado: Optional[Dict[str, Any]]

    # ========== CONTROLE DE FLUXO ==========
    next_action: str
    erro: Optional[str]
    erro_detalhes: Optional[Dict[str, Any]]


# ========== FUNÇÕES AUXILIARES ==========

def criar_estado_inicial() -> AgentState:
    """
    Cria um estado inicial vazio com valores padrão.

    Útil para testes e inicialização do grafo.

    Returns:
        AgentState: Estado inicial com valores padrão

    Example:
        >>> state = criar_estado_inicial()
        >>> state["cliente_existe"] = False
        >>> state["next_action"] = AcaoFluxo.VERIFICAR_CLIENTE
    """
    return AgentState(
        raw_webhook_data={},
        cliente_numero="",
        cliente_nome="",
        cliente_id=None,
        cliente_existe=False,
        cliente_ultima_mensagem=None,
        mensagem_tipo=TipoMensagem.OUTROS.value,
        mensagem_conteudo="",
        mensagem_base64=None,
        mensagem_transcrita=None,
        texto_processado="",
        mensagem_id="",
        mensagem_timestamp=None,
        mensagem_from_me=False,
        fila_mensagens=[],
        deve_processar=False,
        messages=[],
        resposta_agente="",
        respostas_fragmentadas=[],
        agendamento_intencao=None,
        agendamento_dados=None,
        agendamento_resultado=None,
        next_action="",
        erro=None,
        erro_detalhes=None
    )


def validar_estado(state: AgentState) -> bool:
    """
    Valida se o estado contém os campos mínimos necessários.

    Args:
        state: Estado a ser validado

    Returns:
        bool: True se o estado é válido, False caso contrário

    Example:
        >>> state = criar_estado_inicial()
        >>> validar_estado(state)
        True
    """
    campos_obrigatorios = [
        "raw_webhook_data",
        "next_action"
    ]

    for campo in campos_obrigatorios:
        if campo not in state:
            return False

    return True


def extrair_numero_whatsapp(jid: str) -> str:
    """
    Extrai o número de telefone de um JID do WhatsApp.

    Remove o sufixo @s.whatsapp.net ou @g.us (grupos).

    Args:
        jid: JID completo do WhatsApp (ex: 5562999999999@s.whatsapp.net)

    Returns:
        str: Número sem o sufixo (ex: 5562999999999)

    Example:
        >>> extrair_numero_whatsapp("5562999999999@s.whatsapp.net")
        '5562999999999'
        >>> extrair_numero_whatsapp("5562999999999@g.us")
        '5562999999999'
    """
    if "@" in jid:
        return jid.split("@")[0]
    return jid


def formatar_jid_whatsapp(numero: str) -> str:
    """
    Formata um número de telefone para o formato JID do WhatsApp.

    Args:
        numero: Número de telefone (ex: 5562999999999)

    Returns:
        str: JID formatado (ex: 5562999999999@s.whatsapp.net)

    Example:
        >>> formatar_jid_whatsapp("5562999999999")
        '5562999999999@s.whatsapp.net'
    """
    if "@" not in numero:
        return f"{numero}@s.whatsapp.net"
    return numero


def tipo_mensagem_from_string(tipo: str) -> TipoMensagem:
    """
    Converte uma string para o enum TipoMensagem.

    Args:
        tipo: String com o tipo da mensagem

    Returns:
        TipoMensagem: Enum correspondente ou OUTROS se não encontrado

    Example:
        >>> tipo_mensagem_from_string("audioMessage")
        TipoMensagem.AUDIO
        >>> tipo_mensagem_from_string("unknown")
        TipoMensagem.OUTROS
    """
    try:
        return TipoMensagem(tipo)
    except ValueError:
        return TipoMensagem.OUTROS


# ========== EXPORTAÇÕES ==========

__all__ = [
    # Enums
    "TipoMensagem",
    "AcaoFluxo",
    "IntencaoAgendamento",

    # Estado
    "AgentState",

    # Funções auxiliares
    "criar_estado_inicial",
    "validar_estado",
    "extrair_numero_whatsapp",
    "formatar_jid_whatsapp",
    "tipo_mensagem_from_string",
]
