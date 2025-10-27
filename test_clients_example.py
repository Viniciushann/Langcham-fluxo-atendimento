"""
Exemplo de uso dos clientes externos (Supabase, Redis, WhatsApp).

NOTA: Este arquivo demonstra como usar os clientes.
Para executar, é necessário instalar as dependências:
    pip install -r requirements.txt

E configurar as variáveis de ambiente no arquivo .env
"""

# Imports comentados até instalar dependências
# from src.clients import (
#     SupabaseClient,
#     RedisQueue,
#     WhatsAppClient,
#     criar_supabase_client,
#     criar_redis_queue,
#     criar_whatsapp_client,
# )
# from src.config import get_settings
# import asyncio


# ========== EXEMPLOS DE USO ==========

def exemplo_supabase():
    """
    Exemplo de uso do SupabaseClient.

    Demonstra:
    - Buscar cliente por telefone
    - Cadastrar novo cliente
    - Buscar documentos para RAG
    """
    print("\n" + "=" * 60)
    print("EXEMPLO: SupabaseClient")
    print("=" * 60)

    exemplo_codigo = '''
# Inicializar cliente
from src.clients import criar_supabase_client
from src.config import get_settings

settings = get_settings()
supabase = criar_supabase_client(
    url=settings.supabase_url,
    key=settings.supabase_key
)

# Buscar cliente existente
cliente = await supabase.buscar_cliente("5562999999999")
if cliente:
    print(f"Cliente encontrado: {cliente['nome_lead']}")
    print(f"ID: {cliente['id']}")

# Cadastrar novo cliente
novo_cliente = await supabase.cadastrar_cliente({
    "nome_lead": "João Silva",
    "phone_numero": "5562888888888",
    "message": "Olá, preciso de informações",
    "tipo_mensagem": "conversation"
})
print(f"Cliente cadastrado: ID {novo_cliente['id']}")

# Buscar documentos para RAG
documentos = await supabase.buscar_documentos_rag(
    query="preços de instalação de drywall",
    limit=5
)
for doc in documentos:
    print(f"Documento: {doc['content'][:100]}...")
    print(f"Similaridade: {doc.get('similarity', 'N/A')}")
    '''

    print(exemplo_codigo)


def exemplo_redis():
    """
    Exemplo de uso do RedisQueue.

    Demonstra:
    - Adicionar mensagem à fila
    - Buscar mensagens
    - Contar mensagens
    - Limpar fila
    """
    print("\n" + "=" * 60)
    print("EXEMPLO: RedisQueue")
    print("=" * 60)

    exemplo_codigo = '''
# Inicializar Redis Queue
from src.clients import criar_redis_queue
from src.config import get_settings

settings = get_settings()
queue = await criar_redis_queue(
    host=settings.redis_host,
    port=settings.redis_port,
    password=settings.redis_password,
    db=settings.redis_db
)

# Adicionar mensagem à fila
telefone = "5562999999999"
await queue.adicionar_mensagem(
    telefone=telefone,
    mensagem={
        "conteudo": "Olá, quero agendar",
        "timestamp": "2025-10-21T10:00:00",
        "tipo": "conversation"
    }
)
print("Mensagem adicionada à fila")

# Contar mensagens
count = await queue.contar_mensagens(telefone)
print(f"Mensagens na fila: {count}")

# Buscar todas as mensagens
mensagens = await queue.buscar_mensagens(telefone)
for msg in mensagens:
    print(f"Mensagem: {msg['conteudo']}")
    print(f"Timestamp: {msg['timestamp']}")

# Limpar fila após processar
await queue.limpar_fila(telefone)
print("Fila limpa")

# Fechar conexão
await queue.close()
    '''

    print(exemplo_codigo)


def exemplo_whatsapp():
    """
    Exemplo de uso do WhatsAppClient.

    Demonstra:
    - Enviar mensagem de texto
    - Enviar status "digitando"
    - Obter mídia em base64
    """
    print("\n" + "=" * 60)
    print("EXEMPLO: WhatsAppClient")
    print("=" * 60)

    exemplo_codigo = '''
# Inicializar WhatsApp Client
from src.clients import criar_whatsapp_client
from src.config import get_settings
import asyncio

settings = get_settings()
whatsapp = criar_whatsapp_client(
    base_url=settings.whatsapp_api_url,
    api_key=settings.whatsapp_api_key,
    instance=settings.whatsapp_instance
)

# Enviar status "digitando"
telefone = "5562999999999"
await whatsapp.enviar_status_typing(telefone)
print("Status 'digitando' enviado")

# Aguardar um pouco
await asyncio.sleep(2)

# Enviar mensagem
response = await whatsapp.enviar_mensagem(
    telefone=telefone,
    texto="Olá! Como posso ajudar você hoje?"
)
print(f"Mensagem enviada: ID {response.get('id')}")

# Obter mídia de uma mensagem
message_id = "MSG123456"
media = await whatsapp.obter_media_base64(message_id)
print(f"Mídia obtida:")
print(f"  Tipo: {media['mimetype']}")
print(f"  Tamanho base64: {len(media['base64'])} caracteres")

# Fechar conexão
await whatsapp.close()
    '''

    print(exemplo_codigo)


def exemplo_uso_integrado():
    """
    Exemplo de uso integrado de todos os clientes.

    Demonstra um fluxo completo:
    1. Receber webhook
    2. Buscar/cadastrar cliente no Supabase
    3. Adicionar mensagem à fila Redis
    4. Processar e enviar resposta via WhatsApp
    """
    print("\n" + "=" * 60)
    print("EXEMPLO: Uso Integrado (Fluxo Completo)")
    print("=" * 60)

    exemplo_codigo = '''
async def processar_mensagem_completo():
    """Fluxo completo de processamento de mensagem"""

    # 1. Inicializar todos os clientes
    from src.clients import (
        criar_supabase_client,
        criar_redis_queue,
        criar_whatsapp_client
    )
    from src.config import get_settings

    settings = get_settings()

    supabase = criar_supabase_client(
        settings.supabase_url,
        settings.supabase_key
    )

    queue = await criar_redis_queue(
        settings.redis_host,
        settings.redis_port,
        settings.redis_password
    )

    whatsapp = criar_whatsapp_client(
        settings.whatsapp_api_url,
        settings.whatsapp_api_key,
        settings.whatsapp_instance
    )

    # 2. Dados do webhook (simulado)
    telefone = "5562999999999"
    nome = "João Silva"
    mensagem = "Quero agendar uma consulta"

    # 3. Buscar ou cadastrar cliente
    cliente = await supabase.buscar_cliente(telefone)

    if not cliente:
        print("Cliente não encontrado. Cadastrando...")
        cliente = await supabase.cadastrar_cliente({
            "nome_lead": nome,
            "phone_numero": telefone,
            "message": mensagem,
            "tipo_mensagem": "conversation"
        })
        print(f"Cliente cadastrado: ID {cliente['id']}")
    else:
        print(f"Cliente encontrado: {cliente['nome_lead']}")

    # 4. Adicionar mensagem à fila
    await queue.adicionar_mensagem(
        telefone=telefone,
        mensagem={
            "conteudo": mensagem,
            "timestamp": "2025-10-21T10:00:00",
            "tipo": "conversation"
        }
    )

    # 5. Contar mensagens na fila
    count = await queue.contar_mensagens(telefone)
    print(f"Mensagens na fila: {count}")

    # 6. Processar mensagens (simulado)
    mensagens = await queue.buscar_mensagens(telefone)
    texto_completo = " ".join([msg["conteudo"] for msg in mensagens])

    # 7. Buscar contexto do RAG
    documentos = await supabase.buscar_documentos_rag(texto_completo, limit=3)
    contexto = "\\n".join([doc.get("content", "") for doc in documentos])

    # 8. Gerar resposta (aqui seria o agente LangChain)
    resposta = f"Olá {nome}! Entendi que você deseja: {mensagem}. Como posso ajudar?"

    # 9. Enviar status digitando
    await whatsapp.enviar_status_typing(telefone)
    await asyncio.sleep(1)

    # 10. Enviar resposta
    await whatsapp.enviar_mensagem(telefone, resposta)
    print("Resposta enviada!")

    # 11. Limpar fila
    await queue.limpar_fila(telefone)

    # 12. Fechar conexões
    await queue.close()
    await whatsapp.close()

    print("\\nFluxo completo executado com sucesso!")

# Executar
import asyncio
asyncio.run(processar_mensagem_completo())
    '''

    print(exemplo_codigo)


def exemplo_tratamento_erros():
    """
    Exemplo de tratamento de erros.
    """
    print("\n" + "=" * 60)
    print("EXEMPLO: Tratamento de Erros")
    print("=" * 60)

    exemplo_codigo = '''
# Tratamento de erros com try/except

try:
    # Tentar buscar cliente
    cliente = await supabase.buscar_cliente("5562999999999")

except Exception as e:
    print(f"Erro ao buscar cliente: {e}")
    # Log do erro
    import logging
    logger = logging.getLogger(__name__)
    logger.error(f"Erro: {e}", exc_info=True)

# WhatsApp com retry automático
try:
    # Se falhar, tenta 3 vezes automaticamente
    response = await whatsapp.enviar_mensagem(
        telefone="5562999999999",
        texto="Teste"
    )
except Exception as e:
    print(f"Falhou após 3 tentativas: {e}")

# Redis com fallback
try:
    await queue.adicionar_mensagem(telefone, mensagem)
except Exception as e:
    print(f"Redis indisponível: {e}")
    # Processar diretamente sem fila
    processar_sem_fila(mensagem)
    '''

    print(exemplo_codigo)


# ========== MAIN ==========

if __name__ == "__main__":
    print("=" * 60)
    print("EXEMPLOS DE USO DOS CLIENTES EXTERNOS")
    print("=" * 60)
    print("\nNOTA: Para executar estes exemplos, instale as dependências:")
    print("  pip install -r requirements.txt")
    print("\nE configure o arquivo .env com suas credenciais.")
    print("\n" + "=" * 60)

    exemplo_supabase()
    exemplo_redis()
    exemplo_whatsapp()
    exemplo_uso_integrado()
    exemplo_tratamento_erros()

    print("\n" + "=" * 60)
    print("DOCUMENTAÇÃO COMPLETA")
    print("=" * 60)
    print("\nPara mais detalhes, consulte os docstrings nos arquivos:")
    print("  - src/clients/supabase_client.py")
    print("  - src/clients/redis_client.py")
    print("  - src/clients/whatsapp_client.py")
    print("\n" + "=" * 60)
