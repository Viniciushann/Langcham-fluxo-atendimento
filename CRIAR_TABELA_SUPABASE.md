# Como Criar a Tabela 'clientes' no Supabase

## Problema Identificado

O sistema está retornando o erro:
```
Could not find the table 'public.clientes' in the schema cache
```

Isso significa que a tabela `clientes` não existe no banco de dados Supabase.

## Solução: Criar a Tabela Manualmente

### Passo 1: Acessar o Supabase

1. Abra seu navegador
2. Acesse: https://znyypdwnqdlvqwwvffzk.supabase.co
3. Faça login com suas credenciais

### Passo 2: Abrir o SQL Editor

1. No menu lateral esquerdo, clique em **"SQL Editor"**
2. Clique em **"New query"** (Nova consulta)

### Passo 3: Copiar e Executar o SQL

Copie e cole o SQL abaixo no editor:

```sql
-- Criar tabela de clientes
CREATE TABLE IF NOT EXISTS public.clientes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome_lead TEXT NOT NULL,
    phone_numero TEXT NOT NULL UNIQUE,
    message TEXT,
    tipo_mensagem TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Criar índice para busca rápida por telefone
CREATE INDEX IF NOT EXISTS idx_clientes_phone
ON public.clientes(phone_numero);

-- Função para atualização automática de updated_at
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

### Passo 5: Verificar se a Tabela Foi Criada

Execute esta consulta para verificar:

```sql
SELECT * FROM information_schema.tables
WHERE table_schema = 'public'
AND table_name = 'clientes';
```

Você deve ver 1 linha retornada com informações sobre a tabela.

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

## Estrutura da Tabela

A tabela `clientes` tem os seguintes campos:

| Campo | Tipo | Descrição |
|-------|------|-----------|
| id | UUID | ID único do cliente (gerado automaticamente) |
| nome_lead | TEXT | Nome do cliente/lead (obrigatório) |
| phone_numero | TEXT | Número de telefone com código do país (único) |
| message | TEXT | Primeira mensagem recebida do cliente |
| tipo_mensagem | TEXT | Tipo da mensagem (conversation, audioMessage, etc) |
| created_at | TIMESTAMP | Data/hora de criação (automático) |
| updated_at | TIMESTAMP | Data/hora de última atualização (automático) |

---

## Alternativa: Script Completo

Se preferir, você pode executar o script completo que está no arquivo:

**create_tables.sql**

Este script cria:
- ✅ Tabela `clientes`
- ✅ Tabela `documents` (para RAG)
- ✅ Índices para performance
- ✅ Extensão pgvector
- ✅ Triggers para atualização automática

---

## Após Criar a Tabela

O sistema já está configurado e funcionando:

- ✅ FastAPI rodando em http://localhost:8000
- ✅ Ngrok ativo em https://unselective-marg-parisonic.ngrok-free.dev
- ✅ Webhook configurado na Evolution API
- ⚠️ **Tabela clientes precisa ser criada manualmente**

Depois de criar a tabela, o bot estará 100% operacional!
