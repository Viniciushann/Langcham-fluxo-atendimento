# Configuração do Google Calendar API

Este guia explica como configurar a integração com o Google Calendar para o sistema de agendamento.

## Pré-requisitos

- Conta Google
- Python 3.8+
- Pacotes instalados: `google-auth-oauthlib`, `google-auth-httplib2`, `google-api-python-client`

## Passo 1: Criar Projeto no Google Cloud Console

1. Acesse [Google Cloud Console](https://console.cloud.google.com/)
2. Crie um novo projeto ou selecione um existente
3. Nomeie o projeto (ex: "Sistema Agendamento")

## Passo 2: Ativar Google Calendar API

1. No menu lateral, vá em **APIs e Serviços** > **Biblioteca**
2. Busque por "Google Calendar API"
3. Clique em **Ativar**

## Passo 3: Criar Credenciais OAuth 2.0

1. Vá em **APIs e Serviços** > **Credenciais**
2. Clique em **+ CRIAR CREDENCIAIS** > **ID do cliente OAuth**
3. Configure a tela de consentimento OAuth:
   - Tipo: **Externo** (ou Interno se G Workspace)
   - Nome do app: "Sistema de Agendamento"
   - Email de suporte: seu email
   - Escopos: adicione `.../auth/calendar`
4. Tipo de aplicativo: **Aplicativo para computador**
5. Nome: "Desktop Client"
6. Clique em **Criar**

## Passo 4: Baixar Credenciais

1. Após criar, clique no ícone de download (⬇️) das credenciais
2. Salve o arquivo como `credentials.json` na raiz do projeto
3. **IMPORTANTE**: Adicione `credentials.json` ao `.gitignore`

## Passo 5: Estrutura do Arquivo credentials.json

O arquivo deve ter esta estrutura:

```json
{
  "installed": {
    "client_id": "SEU_CLIENT_ID.apps.googleusercontent.com",
    "project_id": "seu-projeto-id",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_secret": "SEU_CLIENT_SECRET",
    "redirect_uris": ["http://localhost"]
  }
}
```

## Passo 6: Instalação de Dependências

```bash
pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client
```

Ou adicione ao `requirements.txt`:

```
google-auth-oauthlib==1.2.0
google-auth-httplib2==0.2.0
google-api-python-client==2.111.0
```

## Passo 7: Primeira Execução

Na primeira vez que executar o código:

1. Um navegador abrirá automaticamente
2. Faça login com sua conta Google
3. Autorize o aplicativo a acessar seu Google Calendar
4. Um arquivo `token.json` será criado automaticamente
5. **IMPORTANTE**: Adicione `token.json` ao `.gitignore`

## Passo 8: Variáveis de Ambiente (Opcional)

Crie um arquivo `.env` na raiz do projeto:

```env
GOOGLE_CALENDAR_CREDENTIALS_FILE=credentials.json
```

## Segurança

### Arquivos a adicionar no .gitignore:

```gitignore
# Google Calendar
credentials.json
token.json
```

### Permissões

A aplicação solicita o scope:
- `https://www.googleapis.com/auth/calendar` - Acesso completo ao calendário

## Estrutura de Arquivos

```
seu-projeto/
├── credentials.json          # Credenciais OAuth (NÃO COMMITAR)
├── token.json               # Token de acesso (NÃO COMMITAR)
├── src/
│   └── tools/
│       └── scheduling.py    # Implementação das ferramentas
└── .env                     # Variáveis de ambiente (NÃO COMMITAR)
```

## Renovação de Token

O token expira após algum tempo. O código já trata isso automaticamente:
- Se o token expirou mas tem `refresh_token`, renova automaticamente
- Se não conseguir renovar, solicita nova autenticação

## Testando a Integração

Execute o seguinte código Python para testar:

```python
import asyncio
from src.tools.scheduling import agendamento_tool

async def teste():
    resultado = await agendamento_tool(
        nome_cliente="Teste",
        telefone_cliente="11999999999",
        email_cliente="teste@email.com",
        data_consulta_reuniao="2025-10-25",
        intencao="consultar",
        informacao_extra=""
    )
    print(resultado)

asyncio.run(teste())
```

## Troubleshooting

### Erro: "File credentials.json not found"
- Verifique se o arquivo `credentials.json` está na raiz do projeto
- Configure a variável de ambiente `GOOGLE_CALENDAR_CREDENTIALS_FILE`

### Erro: "Access denied"
- Verifique se a Google Calendar API está ativada no projeto
- Confirme que os escopos OAuth estão corretos

### Erro: "Invalid grant"
- Delete o arquivo `token.json`
- Execute novamente para refazer a autenticação

### Token expira constantemente
- Verifique se o `refresh_token` está sendo salvo corretamente
- Certifique-se de que o tipo de aplicativo é "Desktop" não "Web"

## Limites da API

O Google Calendar API tem limites de uso:
- **Quota de leitura**: 1.000.000 requisições/dia
- **Quota de escrita**: 3.000 requisições/dia

Para a maioria dos casos de uso, esses limites são mais do que suficientes.

## Referências

- [Google Calendar API Documentation](https://developers.google.com/calendar/api/guides/overview)
- [Python Quickstart](https://developers.google.com/calendar/api/quickstart/python)
- [OAuth 2.0 for Desktop Apps](https://developers.google.com/identity/protocols/oauth2/native-app)
