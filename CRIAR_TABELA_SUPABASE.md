# Como Criar as Tabelas no Supabase

## Problema Identificado

O sistema precisa de duas tabelas principais:

1. **`clientes`** - Para cadastro de clientes
2. **`message_history`** - Para histórico de conversas (memória do bot)

Se essas tabelas não existirem, você verá erros como:
```
Could not find the table 'public.clientes' in the schema cache
```

Ou o bot não manterá o contexto da conversa (não lembrará das mensagens anteriores).

## Solução: Criar as Tabelas Manualmente

⚠️ **IMPORTANTE**: Execute o script completo `create_tables.sql` que já contém todas as tabelas necessárias!

### Passo 1: Acessar o Supabase

1. Abra seu navegador
2. Acesse: https://znyypdwnqdlvqwwvffzk.supabase.co
3. Faça login com suas credenciais

### Passo 2: Abrir o SQL Editor

1. No menu lateral esquerdo, clique em **"SQL Editor"**
2. Clique em **"New query"** (Nova consulta)

### Passo 3: Copiar e Executar o SQL

**OPÇÃO 1 (Recomendada)**: Copie o conteúdo completo do arquivo `create_tables.sql`

**OPÇÃO 2**: Copie e cole o SQL abaixo no editor (apenas tabelas essenciais):

```sql
-- 1. Criar tabela de clientes
CREATE TABLE IF NOT EXISTS public.clientes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome_lead TEXT NOT NULL,
    phone_numero TEXT NOT NULL UNIQUE,
    message TEXT,
    tipo_mensagem TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índice para busca rápida por telefone
CREATE INDEX IF NOT EXISTS idx_clientes_phone
ON public.clientes(phone_numero);

-- 2. Criar tabela de histórico de mensagens (IMPORTANTE PARA MEMÓRIA DO BOT)
CREATE TABLE IF NOT EXISTS public.message_history (
    id SERIAL PRIMARY KEY,
    session_id TEXT NOT NULL,
    message JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Índices para busca rápida
CREATE INDEX IF NOT EXISTS idx_message_history_session_id
ON public.message_history(session_id);

CREATE INDEX IF NOT EXISTS idx_message_history_created_at
ON public.message_history(created_at);

-- 3. Função para atualização automática de updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger para atualização automática
CREATE TRIGGER update_clientes_updated_at
    BEFORE UPDATE ON public.clientes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
```

### Passo 4: Executar o SQL

1. Com o SQL colado no editor, clique em **"Run"** (Executar) ou pressione **Ctrl + Enter**
2. Aguarde a mensagem de sucesso aparecer

### Passo 5: Verificar se as Tabelas Foram Criadas

Execute esta consulta para verificar:

```sql
SELECT table_name FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name IN ('clientes', 'message_history')
ORDER BY table_name;
```

Você deve ver 2 linhas retornadas:
- `clientes`
- `message_history`

### Passo 6: Inserir um Cliente de Teste (Opcional)

```sql
INSERT INTO public.clientes (nome_lead, phone_numero, message, tipo_mensagem)
VALUES ('Cliente Teste', '556299999999', 'Mensagem de teste', 'conversation');

-- Verificar se foi inserido
SELECT * FROM public.clientes;
```

### Passo 7: Testar Novamente o Bot

Depois de criar a tabela, o sistema deve funcionar corretamente.

1. Envie uma nova mensagem via WhatsApp para: **+55 62 9970-28296**
2. Ou execute o teste novamente via script

---

## Estrutura das Tabelas

### Tabela `clientes`

| Campo | Tipo | Descrição                                    |
| ----- | ---- | -------------------------------------------- |
| id    | UUID | ID único do cliente (gerado automaticamente) |
| nome_lead | TEXT | Nome do cliente/lead (obrigatório) |
| phone_numero | TEXT | Número de telefone com código do país (único) |
| message | TEXT | Primeira mensagem recebida do cliente |
| tipo_mensagem | TEXT | Tipo da mensagem (conversation, audioMessage, etc) |
| created_at | TIMESTAMP | Data/hora de criação (automático) |
| updated_at | TIMESTAMP | Data/hora de última atualização (automático) |

### Tabela `message_history` (Memória do Bot)

| Campo | Tipo | Descrição                                    |
| ----- | ---- | -------------------------------------------- |
| id    | SERIAL | ID único da mensagem (gerado automaticamente) |
| session_id | TEXT | ID da sessão (número do telefone do cliente) |
| message | JSONB | Mensagem em formato JSON (compatível com LangChain) |
| created_at | TIMESTAMP | Data/hora da mensagem (automático) |

---

## Alternativa: Script Completo

Se preferir, você pode executar o script completo que está no arquivo:

**create_tables.sql**

Este script cria:

- ✅ Tabela `clientes`
- ✅ Tabela `message_history` (memória do bot)
- ✅ Tabela `documents` (para RAG)
- ✅ Índices para performance
- ✅ Extensão pgvector
- ✅ Triggers para atualização automática

---

## Após Criar as Tabelas

O sistema já está configurado e funcionando:

- ✅ FastAPI rodando em http://localhost:8000
- ✅ Ngrok ativo em https://unselective-marg-parisonic.ngrok-free.dev
- ✅ Webhook configurado na Evolution API
- ✅ Base64 habilitado no webhook
- ⚠️ **Tabelas precisam ser criadas manualmente no Supabase**

Depois de criar as tabelas:
- ✅ Bot funcionará 100%
- ✅ Bot manterá contexto da conversa (memória)
- ✅ Bot não repetirá perguntas já respondidas
- ✅ Histórico persistente por cliente
