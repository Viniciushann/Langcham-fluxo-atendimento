"""
Módulo de ferramentas de agendamento com integração ao Google Calendar.

Este módulo fornece funcionalidades para:
- Consultar horários disponíveis
- Agendar novos compromissos
- Cancelar agendamentos existentes
- Atualizar agendamentos

Autor: Sistema de Agendamento
Data: 2025-10-21
"""

import os
import logging
from datetime import datetime, timedelta
from typing import Literal, Optional, Dict, List, Any
from zoneinfo import ZoneInfo

from langchain.tools import tool
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from src.clients.whatsapp_client import WhatsAppClient
from src.config.settings import get_settings

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configurações do Google Calendar
SCOPES = ['https://www.googleapis.com/auth/calendar']
SERVICE_ACCOUNT_FILE = os.getenv('GOOGLE_CALENDAR_CREDENTIALS_FILE', 'credentials.json')
CALENDAR_ID = os.getenv('GOOGLE_CALENDAR_ID', 'centrooestedrywalldry@gmail.com')
TIMEZONE = 'America/Sao_Paulo'

# Configurações de horário comercial
HORARIO_INICIO = 8  # 8h
HORARIO_FIM = 18    # 18h
DURACAO_CONSULTA = 1  # 1 hora

# Configuração do técnico
TELEFONE_TECNICO = "556298540075"  # +55 62 98540-0075


def _get_calendar_service() -> Any:
    """
    Obtém o serviço do Google Calendar autenticado via Service Account.

    Returns:
        Resource: Serviço do Google Calendar

    Raises:
        FileNotFoundError: Se o arquivo de credenciais não for encontrado
        Exception: Erros de autenticação
    """
    if not os.path.exists(SERVICE_ACCOUNT_FILE):
        raise FileNotFoundError(
            f"Arquivo de credenciais da Service Account não encontrado: {SERVICE_ACCOUNT_FILE}"
        )

    try:
        # Carregar credenciais da Service Account
        credentials = service_account.Credentials.from_service_account_file(
            SERVICE_ACCOUNT_FILE,
            scopes=SCOPES
        )
        logger.info("Service Account carregada com sucesso")

        # Criar serviço do Google Calendar
        service = build('calendar', 'v3', credentials=credentials)
        logger.info("Serviço do Google Calendar inicializado")

        return service

    except Exception as e:
        logger.error(f"Erro ao autenticar com Service Account: {e}")
        raise


def _parsear_data(data_str: str) -> datetime:
    """
    Converte string de data para objeto datetime.

    Args:
        data_str: Data no formato ISO 8601 ou variações

    Returns:
        datetime: Objeto datetime parseado

    Raises:
        ValueError: Se o formato da data for inválido
    """
    formatos = [
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%S',
        '%Y-%m-%d %H:%M:%S',
        '%Y-%m-%d',
        '%d/%m/%Y %H:%M',
        '%d/%m/%Y'
    ]

    for formato in formatos:
        try:
            dt = datetime.strptime(data_str, formato)
            # Se não tem timezone, adiciona o timezone padrão
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=ZoneInfo(TIMEZONE))
            return dt
        except ValueError:
            continue

    raise ValueError(f"Formato de data inválido: {data_str}")


def _validar_data_futura(data: datetime) -> bool:
    """
    Valida se a data está no futuro.

    Args:
        data: Data a ser validada

    Returns:
        bool: True se a data é futura, False caso contrário
    """
    agora = datetime.now(ZoneInfo(TIMEZONE))
    return data > agora


def _gerar_slots_horario(data_referencia: datetime) -> List[Dict[str, str]]:
    """
    Gera lista de slots de horário disponíveis para um dia.

    Args:
        data_referencia: Data para gerar os slots

    Returns:
        List[Dict]: Lista de slots com inicio e fim
    """
    slots = []
    data_base = data_referencia.replace(hour=HORARIO_INICIO, minute=0, second=0, microsecond=0)

    hora_atual = HORARIO_INICIO
    while hora_atual < HORARIO_FIM:
        inicio = data_base.replace(hour=hora_atual)
        fim = inicio + timedelta(hours=DURACAO_CONSULTA)

        slots.append({
            "inicio": inicio.isoformat(),
            "fim": fim.isoformat()
        })

        hora_atual += DURACAO_CONSULTA

    return slots


async def _notificar_tecnico(
    nome_cliente: str,
    telefone_cliente: str,
    endereco: str,
    data_inicio: datetime,
    tipo_servico: str = "visita/orçamento"
) -> bool:
    """
    Envia notificação WhatsApp para o técnico sobre novo agendamento.

    Args:
        nome_cliente: Nome do cliente
        telefone_cliente: Telefone do cliente
        endereco: Endereço do serviço
        data_inicio: Data e hora do agendamento
        tipo_servico: Tipo de serviço agendado

    Returns:
        bool: True se enviou com sucesso, False caso contrário
    """
    try:
        settings = get_settings()

        whatsapp = WhatsAppClient(
            base_url=settings.whatsapp_api_url,
            api_key=settings.whatsapp_api_key,
            instance=settings.whatsapp_instance
        )

        # Formatar data/hora
        data_formatada = data_inicio.strftime("%d/%m/%Y")
        hora_formatada = data_inicio.strftime("%H:%M")
        dia_semana = data_inicio.strftime("%A")

        # Traduzir dia da semana
        dias_pt = {
            "Monday": "Segunda-feira",
            "Tuesday": "Terça-feira",
            "Wednesday": "Quarta-feira",
            "Thursday": "Quinta-feira",
            "Friday": "Sexta-feira",
            "Saturday": "Sábado",
            "Sunday": "Domingo"
        }
        dia_semana_pt = dias_pt.get(dia_semana, dia_semana)

        # Montar mensagem
        mensagem = f"""🔔 *NOVO AGENDAMENTO*

📅 *Data:* {dia_semana_pt}, {data_formatada}
🕐 *Horário:* {hora_formatada}

👤 *Cliente:* {nome_cliente}
📱 *Telefone:* {telefone_cliente}
📍 *Endereço:* {endereco}

🔧 *Tipo:* {tipo_servico}

⚠️ Lembre-se de confirmar presença com o cliente!"""

        # Enviar mensagem
        resultado = await whatsapp.enviar_mensagem(
            telefone=TELEFONE_TECNICO,
            texto=mensagem
        )

        if resultado:
            logger.info(f"Notificação enviada ao técnico para agendamento de {nome_cliente}")
            return True
        else:
            logger.warning("Falha ao enviar notificação ao técnico")
            return False

    except Exception as e:
        logger.error(f"Erro ao notificar técnico: {e}")
        return False


async def consultar_horarios(
    data_referencia: str,
    informacao_extra: str = ""
) -> Dict[str, Any]:
    """
    Consulta horários disponíveis no Google Calendar.

    Args:
        data_referencia: Data para consultar (formato ISO ou DD/MM/YYYY)
        informacao_extra: Contexto adicional como "período da tarde"

    Returns:
        Dict: {
            "sucesso": bool,
            "mensagem": str,
            "dados": {
                "horarios": List[Dict],
                "data_referencia": str
            }
        }
    """
    try:
        logger.info(f"Consultando horários para: {data_referencia}")

        # Parsear data
        data = _parsear_data(data_referencia)

        # Validar se é data futura
        if not _validar_data_futura(data):
            return {
                "sucesso": False,
                "mensagem": "Não é possível consultar horários no passado",
                "dados": {}
            }

        # Obter serviço do calendar
        service = _get_calendar_service()

        # Definir período de busca (dia inteiro)
        inicio_dia = data.replace(hour=0, minute=0, second=0, microsecond=0)
        fim_dia = inicio_dia + timedelta(days=1)

        # Buscar eventos existentes
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=inicio_dia.isoformat(),
            timeMax=fim_dia.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        eventos = events_result.get('items', [])
        logger.info(f"Encontrados {len(eventos)} eventos agendados")

        # Gerar todos os slots possíveis
        todos_slots = _gerar_slots_horario(data)

        # Filtrar slots ocupados
        slots_disponiveis = []
        for slot in todos_slots:
            slot_inicio = datetime.fromisoformat(slot['inicio'])
            slot_fim = datetime.fromisoformat(slot['fim'])

            # Verificar se slot está livre
            ocupado = False
            for evento in eventos:
                evento_inicio = datetime.fromisoformat(
                    evento['start'].get('dateTime', evento['start'].get('date'))
                )
                evento_fim = datetime.fromisoformat(
                    evento['end'].get('dateTime', evento['end'].get('date'))
                )

                # Verifica sobreposição
                if not (slot_fim <= evento_inicio or slot_inicio >= evento_fim):
                    ocupado = True
                    break

            if not ocupado and _validar_data_futura(slot_inicio):
                slots_disponiveis.append(slot)

        # Filtrar por período se especificado
        if "tarde" in informacao_extra.lower():
            slots_disponiveis = [
                s for s in slots_disponiveis
                if 12 <= datetime.fromisoformat(s['inicio']).hour < 18
            ]
        elif "manha" in informacao_extra.lower() or "manhã" in informacao_extra.lower():
            slots_disponiveis = [
                s for s in slots_disponiveis
                if datetime.fromisoformat(s['inicio']).hour < 12
            ]

        logger.info(f"Encontrados {len(slots_disponiveis)} horários disponíveis")

        return {
            "sucesso": True,
            "mensagem": f"Encontrados {len(slots_disponiveis)} horários disponíveis",
            "dados": {
                "horarios": slots_disponiveis,
                "data_referencia": data.strftime("%d/%m/%Y")
            }
        }

    except ValueError as e:
        logger.error(f"Erro ao parsear data: {e}")
        return {
            "sucesso": False,
            "mensagem": f"Formato de data inválido: {str(e)}",
            "dados": {}
        }
    except FileNotFoundError as e:
        logger.error(f"Arquivo de credenciais não encontrado: {e}")
        return {
            "sucesso": False,
            "mensagem": "Erro de configuração: arquivo de credenciais não encontrado",
            "dados": {}
        }
    except HttpError as e:
        logger.error(f"Erro na API do Google Calendar: {e}")
        return {
            "sucesso": False,
            "mensagem": f"Erro ao acessar Google Calendar: {str(e)}",
            "dados": {}
        }
    except Exception as e:
        logger.error(f"Erro inesperado ao consultar horários: {e}")
        return {
            "sucesso": False,
            "mensagem": f"Erro ao consultar horários: {str(e)}",
            "dados": {}
        }


async def agendar_horario(
    nome_cliente: str,
    telefone_cliente: str,
    email_cliente: str,
    data_consulta_reuniao: str,
    informacao_extra: str = ""
) -> Dict[str, Any]:
    """
    Agenda um novo compromisso no Google Calendar.

    Args:
        nome_cliente: Nome completo do cliente
        telefone_cliente: Telefone do cliente com DDD
        email_cliente: Email do cliente
        data_consulta_reuniao: Data/hora do agendamento
        informacao_extra: Informações adicionais para a descrição

    Returns:
        Dict: {
            "sucesso": bool,
            "mensagem": str,
            "dados": {
                "evento_id": str,
                "link": str,
                "inicio": str,
                "fim": str
            }
        }
    """
    try:
        logger.info(f"Agendando horário para {nome_cliente} em {data_consulta_reuniao}")

        # Parsear data
        data_inicio = _parsear_data(data_consulta_reuniao)

        # Validar se é data futura
        if not _validar_data_futura(data_inicio):
            return {
                "sucesso": False,
                "mensagem": "Não é possível agendar no passado",
                "dados": {}
            }

        # Calcular fim (início + duração)
        data_fim = data_inicio + timedelta(hours=DURACAO_CONSULTA)

        # Obter serviço do calendar
        service = _get_calendar_service()

        # Verificar se horário está disponível
        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=data_inicio.isoformat(),
            timeMax=data_fim.isoformat(),
            singleEvents=True
        ).execute()

        if events_result.get('items', []):
            logger.warning("Horário já está ocupado")
            return {
                "sucesso": False,
                "mensagem": "Horário já está ocupado. Por favor, escolha outro horário.",
                "dados": {}
            }

        # Criar evento
        evento = {
            'summary': f'Consulta - {nome_cliente}',
            'description': f"""Cliente: {nome_cliente}
Telefone: {telefone_cliente}
Email: {email_cliente}

{informacao_extra}""",
            'start': {
                'dateTime': data_inicio.isoformat(),
                'timeZone': TIMEZONE,
            },
            'end': {
                'dateTime': data_fim.isoformat(),
                'timeZone': TIMEZONE,
            },
            'reminders': {
                'useDefault': False,
                'overrides': [
                    {'method': 'popup', 'minutes': 60},  # 1 hora antes
                ],
            },
        }

        # Inserir evento no calendar (sem attendees para evitar erro de Service Account)
        evento_criado = service.events().insert(
            calendarId=CALENDAR_ID,
            body=evento
        ).execute()

        logger.info(f"Evento criado com sucesso: {evento_criado['id']}")

        # Notificar técnico sobre o novo agendamento
        # Extrair endereço de informacao_extra se disponível
        endereco = "Endereço a confirmar"
        if informacao_extra:
            # Procurar por endereço na informação extra
            if "endereço:" in informacao_extra.lower() or "endereco:" in informacao_extra.lower():
                partes = informacao_extra.split(":")
                if len(partes) > 1:
                    endereco = partes[1].strip()
            elif informacao_extra and len(informacao_extra) > 10:
                # Se informacao_extra parece ser um endereço
                endereco = informacao_extra

        # Tentar enviar notificação (não bloqueia se falhar)
        try:
            await _notificar_tecnico(
                nome_cliente=nome_cliente,
                telefone_cliente=telefone_cliente,
                endereco=endereco,
                data_inicio=data_inicio,
                tipo_servico="Visita/Orçamento"
            )
        except Exception as e:
            logger.warning(f"Não foi possível notificar técnico: {e}")
            # Não falha o agendamento se a notificação falhar

        return {
            "sucesso": True,
            "mensagem": f"Agendamento confirmado para {nome_cliente} no dia {data_inicio.strftime('%d/%m/%Y às %H:%M')}. Técnico notificado!",
            "dados": {
                "evento_id": evento_criado['id'],
                "link": evento_criado.get('htmlLink', ''),
                "inicio": data_inicio.isoformat(),
                "fim": data_fim.isoformat()
            }
        }

    except ValueError as e:
        logger.error(f"Erro ao parsear data: {e}")
        return {
            "sucesso": False,
            "mensagem": f"Formato de data inválido: {str(e)}",
            "dados": {}
        }
    except HttpError as e:
        logger.error(f"Erro na API do Google Calendar: {e}")
        return {
            "sucesso": False,
            "mensagem": f"Erro ao criar agendamento: {str(e)}",
            "dados": {}
        }
    except Exception as e:
        logger.error(f"Erro inesperado ao agendar: {e}")
        return {
            "sucesso": False,
            "mensagem": f"Erro ao agendar: {str(e)}",
            "dados": {}
        }


async def cancelar_horario(
    nome_cliente: str,
    data_consulta_reuniao: str
) -> Dict[str, Any]:
    """
    Cancela um agendamento existente no Google Calendar.

    Args:
        nome_cliente: Nome do cliente para buscar o evento
        data_consulta_reuniao: Data/hora do agendamento a cancelar

    Returns:
        Dict: {
            "sucesso": bool,
            "mensagem": str,
            "dados": {}
        }
    """
    try:
        logger.info(f"Cancelando agendamento de {nome_cliente} em {data_consulta_reuniao}")

        # Parsear data
        data_busca = _parsear_data(data_consulta_reuniao)

        # Obter serviço do calendar
        service = _get_calendar_service()

        # Buscar evento
        inicio_busca = data_busca - timedelta(hours=1)
        fim_busca = data_busca + timedelta(hours=2)

        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=inicio_busca.isoformat(),
            timeMax=fim_busca.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        eventos = events_result.get('items', [])

        # Procurar evento do cliente
        evento_encontrado = None
        for evento in eventos:
            if nome_cliente.lower() in evento.get('summary', '').lower():
                evento_encontrado = evento
                break

        if not evento_encontrado:
            logger.warning(f"Evento não encontrado para {nome_cliente}")
            return {
                "sucesso": False,
                "mensagem": f"Não foi encontrado agendamento para {nome_cliente} nesta data",
                "dados": {}
            }

        # Extrair telefone da descrição do evento
        descricao = evento_encontrado.get('description', '')
        telefone_cliente = ""
        try:
            if 'Telefone:' in descricao:
                telefone_cliente = descricao.split('Telefone:')[1].split('\n')[0].strip()
        except:
            telefone_cliente = "não informado"

        # Deletar evento
        service.events().delete(
            calendarId=CALENDAR_ID,
            eventId=evento_encontrado['id'],
            sendUpdates='all'  # Notifica participantes
        ).execute()

        logger.info(f"Evento cancelado com sucesso: {evento_encontrado['id']}")

        # Notificar técnico sobre o cancelamento
        try:
            settings = get_settings()
            whatsapp = WhatsAppClient(
                base_url=settings.whatsapp_api_url,
                api_key=settings.whatsapp_api_key,
                instance=settings.whatsapp_instance
            )

            # Formatar data/hora
            data_formatada = data_busca.strftime("%d/%m/%Y")
            hora_formatada = data_busca.strftime("%H:%M")
            dia_semana = data_busca.strftime("%A")

            # Traduzir dia da semana
            dias_pt = {
                "Monday": "Segunda-feira",
                "Tuesday": "Terça-feira",
                "Wednesday": "Quarta-feira",
                "Thursday": "Quinta-feira",
                "Friday": "Sexta-feira",
                "Saturday": "Sábado",
                "Sunday": "Domingo"
            }
            dia_semana_pt = dias_pt.get(dia_semana, dia_semana)

            mensagem = f"""❌ AGENDAMENTO CANCELADO

📅 Data: {dia_semana_pt}, {data_formatada}
🕐 Horário: {hora_formatada}

👤 Cliente: {nome_cliente}
📱 Telefone: {telefone_cliente}

⚠️ O cliente cancelou este agendamento."""

            await whatsapp.enviar_mensagem(
                telefone=TELEFONE_TECNICO,
                texto=mensagem
            )
            logger.info(f"Notificação de cancelamento enviada ao técnico")
        except Exception as e:
            logger.warning(f"Não foi possível notificar técnico sobre cancelamento: {e}")

        return {
            "sucesso": True,
            "mensagem": f"Agendamento de {nome_cliente} cancelado com sucesso. Notificações enviadas.",
            "dados": {
                "evento_cancelado": evento_encontrado.get('summary', ''),
                "data": data_busca.strftime('%d/%m/%Y às %H:%M')
            }
        }

    except ValueError as e:
        logger.error(f"Erro ao parsear data: {e}")
        return {
            "sucesso": False,
            "mensagem": f"Formato de data inválido: {str(e)}",
            "dados": {}
        }
    except HttpError as e:
        logger.error(f"Erro na API do Google Calendar: {e}")
        return {
            "sucesso": False,
            "mensagem": f"Erro ao cancelar agendamento: {str(e)}",
            "dados": {}
        }
    except Exception as e:
        logger.error(f"Erro inesperado ao cancelar: {e}")
        return {
            "sucesso": False,
            "mensagem": f"Erro ao cancelar: {str(e)}",
            "dados": {}
        }


async def atualizar_horario(
    nome_cliente: str,
    data_consulta_antiga: str,
    data_consulta_nova: str,
    telefone_cliente: str = "",
    email_cliente: str = ""
) -> Dict[str, Any]:
    """
    Atualiza um agendamento existente no Google Calendar.

    Args:
        nome_cliente: Nome do cliente
        data_consulta_antiga: Data/hora atual do agendamento
        data_consulta_nova: Nova data/hora desejada
        telefone_cliente: Novo telefone (opcional)
        email_cliente: Novo email (opcional)

    Returns:
        Dict: {
            "sucesso": bool,
            "mensagem": str,
            "dados": {}
        }
    """
    try:
        logger.info(f"Atualizando agendamento de {nome_cliente}")

        # Parsear datas
        data_antiga = _parsear_data(data_consulta_antiga)
        data_nova = _parsear_data(data_consulta_nova)

        # Validar se nova data é futura
        if not _validar_data_futura(data_nova):
            return {
                "sucesso": False,
                "mensagem": "Não é possível agendar no passado",
                "dados": {}
            }

        # Obter serviço do calendar
        service = _get_calendar_service()

        # Buscar evento existente
        inicio_busca = data_antiga - timedelta(hours=1)
        fim_busca = data_antiga + timedelta(hours=2)

        events_result = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=inicio_busca.isoformat(),
            timeMax=fim_busca.isoformat(),
            singleEvents=True,
            orderBy='startTime'
        ).execute()

        eventos = events_result.get('items', [])

        # Procurar evento do cliente
        evento_encontrado = None
        for evento in eventos:
            if nome_cliente.lower() in evento.get('summary', '').lower():
                evento_encontrado = evento
                break

        if not evento_encontrado:
            logger.warning(f"Evento não encontrado para {nome_cliente}")
            return {
                "sucesso": False,
                "mensagem": f"Não foi encontrado agendamento para {nome_cliente} nesta data",
                "dados": {}
            }

        # Verificar disponibilidade do novo horário
        data_nova_fim = data_nova + timedelta(hours=DURACAO_CONSULTA)

        eventos_conflito = service.events().list(
            calendarId=CALENDAR_ID,
            timeMin=data_nova.isoformat(),
            timeMax=data_nova_fim.isoformat(),
            singleEvents=True
        ).execute()

        # Ignora o próprio evento na verificação
        conflito = [e for e in eventos_conflito.get('items', [])
                   if e['id'] != evento_encontrado['id']]

        if conflito:
            logger.warning("Novo horário já está ocupado")
            return {
                "sucesso": False,
                "mensagem": "Novo horário já está ocupado. Por favor, escolha outro horário.",
                "dados": {}
            }

        # Atualizar evento
        evento_encontrado['start'] = {
            'dateTime': data_nova.isoformat(),
            'timeZone': TIMEZONE,
        }
        evento_encontrado['end'] = {
            'dateTime': data_nova_fim.isoformat(),
            'timeZone': TIMEZONE,
        }

        # Atualizar descrição se fornecidos novos dados
        if telefone_cliente or email_cliente:
            descricao = evento_encontrado.get('description', '')
            if telefone_cliente:
                descricao = descricao.replace(
                    descricao.split('Telefone: ')[1].split('\n')[0],
                    telefone_cliente
                )
            if email_cliente:
                descricao = descricao.replace(
                    descricao.split('Email: ')[1].split('\n')[0],
                    email_cliente
                )
                evento_encontrado['attendees'] = [{'email': email_cliente}]
            evento_encontrado['description'] = descricao

        # Atualizar no calendar
        evento_atualizado = service.events().update(
            calendarId=CALENDAR_ID,
            eventId=evento_encontrado['id'],
            body=evento_encontrado,
            sendUpdates='all'  # Notifica participantes
        ).execute()

        logger.info(f"Evento atualizado com sucesso: {evento_atualizado['id']}")

        # Notificar técnico sobre o reagendamento
        try:
            # Extrair telefone e endereço da descrição
            descricao = evento_encontrado.get('description', '')
            telefone = telefone_cliente if telefone_cliente else ""
            endereco = "Endereço a confirmar"

            try:
                if 'Telefone:' in descricao and not telefone:
                    telefone = descricao.split('Telefone:')[1].split('\n')[0].strip()
                if 'Endereço:' in descricao or 'Endereco:' in descricao:
                    if 'Endereço:' in descricao:
                        endereco = descricao.split('Endereço:')[1].split('\n')[0].strip()
                    elif 'Endereco:' in descricao:
                        endereco = descricao.split('Endereco:')[1].split('\n')[0].strip()
            except:
                pass

            settings = get_settings()
            whatsapp = WhatsAppClient(
                base_url=settings.whatsapp_api_url,
                api_key=settings.whatsapp_api_key,
                instance=settings.whatsapp_instance
            )

            # Formatar datas
            data_antiga_formatada = data_antiga.strftime("%d/%m/%Y às %H:%M")
            data_nova_formatada = data_nova.strftime("%d/%m/%Y")
            hora_nova_formatada = data_nova.strftime("%H:%M")
            dia_semana = data_nova.strftime("%A")

            # Traduzir dia da semana
            dias_pt = {
                "Monday": "Segunda-feira",
                "Tuesday": "Terça-feira",
                "Wednesday": "Quarta-feira",
                "Thursday": "Quinta-feira",
                "Friday": "Sexta-feira",
                "Saturday": "Sábado",
                "Sunday": "Domingo"
            }
            dia_semana_pt = dias_pt.get(dia_semana, dia_semana)

            mensagem = f"""🔄 AGENDAMENTO REAGENDADO

👤 Cliente: {nome_cliente}
📱 Telefone: {telefone}
📍 Endereço: {endereco}

❌ Horário anterior: {data_antiga_formatada}

✅ Novo horário:
📅 Data: {dia_semana_pt}, {data_nova_formatada}
🕐 Horário: {hora_nova_formatada}

⚠️ Lembre-se de confirmar presença com o cliente!"""

            await whatsapp.enviar_mensagem(
                telefone=TELEFONE_TECNICO,
                texto=mensagem
            )
            logger.info(f"Notificação de reagendamento enviada ao técnico")
        except Exception as e:
            logger.warning(f"Não foi possível notificar técnico sobre reagendamento: {e}")

        return {
            "sucesso": True,
            "mensagem": f"Agendamento de {nome_cliente} atualizado para {data_nova.strftime('%d/%m/%Y às %H:%M')}. Notificações enviadas.",
            "dados": {
                "evento_id": evento_atualizado['id'],
                "link": evento_atualizado.get('htmlLink', ''),
                "novo_horario": data_nova.isoformat()
            }
        }

    except ValueError as e:
        logger.error(f"Erro ao parsear data: {e}")
        return {
            "sucesso": False,
            "mensagem": f"Formato de data inválido: {str(e)}",
            "dados": {}
        }
    except HttpError as e:
        logger.error(f"Erro na API do Google Calendar: {e}")
        return {
            "sucesso": False,
            "mensagem": f"Erro ao atualizar agendamento: {str(e)}",
            "dados": {}
        }
    except Exception as e:
        logger.error(f"Erro inesperado ao atualizar: {e}")
        return {
            "sucesso": False,
            "mensagem": f"Erro ao atualizar: {str(e)}",
            "dados": {}
        }


@tool
async def agendamento_tool(
    nome_cliente: str,
    telefone_cliente: str,
    email_cliente: str,
    data_consulta_reuniao: str,
    intencao: Literal["consultar", "agendar", "cancelar", "atualizar"],
    informacao_extra: str = ""
) -> dict:
    """
    Ferramenta principal para gerenciar agendamentos no Google Calendar.

    Esta ferramenta permite:
    - Consultar horários disponíveis
    - Agendar novos compromissos
    - Cancelar agendamentos existentes
    - Atualizar agendamentos (remarcar)

    Args:
        nome_cliente: Nome completo do cliente
        telefone_cliente: Telefone do cliente com DDD (ex: "11987654321")
        email_cliente: Email do cliente (use "sememail@gmail.com" se não fornecido)
        data_consulta_reuniao: Data/hora no formato ISO 8601 (ex: "2025-10-25T14:00:00-03:00")
                               ou formatos brasileiros como "25/10/2025 14:00"
        intencao: Ação desejada:
                 - "consultar": Ver horários disponíveis
                 - "agendar": Criar novo agendamento
                 - "cancelar": Remover agendamento existente
                 - "atualizar": Mudar data/hora de agendamento
        informacao_extra: Contexto adicional como:
                         - "período da tarde" / "período da manhã"
                         - "urgente"
                         - Nova data para atualização (formato: "nova_data:DD/MM/YYYY HH:MM")

    Returns:
        dict: {
            "sucesso": bool,
            "mensagem": str,
            "dados": dict  # Contém informações específicas da operação
        }

    Examples:
        >>> # Consultar horários
        >>> agendamento_tool(
        ...     nome_cliente="João Silva",
        ...     telefone_cliente="11987654321",
        ...     email_cliente="joao@email.com",
        ...     data_consulta_reuniao="2025-10-25",
        ...     intencao="consultar",
        ...     informacao_extra="período da tarde"
        ... )

        >>> # Agendar consulta
        >>> agendamento_tool(
        ...     nome_cliente="Maria Santos",
        ...     telefone_cliente="11976543210",
        ...     email_cliente="maria@email.com",
        ...     data_consulta_reuniao="2025-10-25T14:00:00-03:00",
        ...     intencao="agendar",
        ...     informacao_extra="Primeira consulta"
        ... )
    """
    logger.info(f"Executando agendamento_tool - Intenção: {intencao}, Cliente: {nome_cliente}")

    try:
        # Validar email
        if not email_cliente or email_cliente == "":
            email_cliente = "sememail@gmail.com"

        # Roteamento baseado na intenção
        if intencao == "consultar":
            resultado = await consultar_horarios(
                data_referencia=data_consulta_reuniao,
                informacao_extra=informacao_extra
            )

        elif intencao == "agendar":
            resultado = await agendar_horario(
                nome_cliente=nome_cliente,
                telefone_cliente=telefone_cliente,
                email_cliente=email_cliente,
                data_consulta_reuniao=data_consulta_reuniao,
                informacao_extra=informacao_extra
            )

        elif intencao == "cancelar":
            resultado = await cancelar_horario(
                nome_cliente=nome_cliente,
                data_consulta_reuniao=data_consulta_reuniao
            )

        elif intencao == "atualizar":
            # Extrair nova data de informacao_extra
            nova_data = ""
            if "nova_data:" in informacao_extra:
                nova_data = informacao_extra.split("nova_data:")[1].strip()

            if not nova_data:
                return {
                    "sucesso": False,
                    "mensagem": "Para atualizar, forneça a nova data em informacao_extra como 'nova_data:DD/MM/YYYY HH:MM'",
                    "dados": {}
                }

            resultado = await atualizar_horario(
                nome_cliente=nome_cliente,
                data_consulta_antiga=data_consulta_reuniao,
                data_consulta_nova=nova_data,
                telefone_cliente=telefone_cliente,
                email_cliente=email_cliente
            )

        else:
            resultado = {
                "sucesso": False,
                "mensagem": f"Intenção inválida: {intencao}. Use: consultar, agendar, cancelar ou atualizar",
                "dados": {}
            }

        logger.info(f"Resultado da operação {intencao}: sucesso={resultado['sucesso']}")
        return resultado

    except Exception as e:
        logger.error(f"Erro na ferramenta de agendamento: {e}")
        return {
            "sucesso": False,
            "mensagem": f"Erro ao processar agendamento: {str(e)}",
            "dados": {}
        }
