-- ============================================================
-- SQL para criar tabelas no Supabase
-- Execute este script no SQL Editor do Supabase
-- ============================================================

-- 1. Tabela de clientes
CREATE TABLE IF NOT EXISTS public.clientes (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nome_lead TEXT NOT NULL,
    phone_numero TEXT NOT NULL UNIQUE,
    message TEXT,
    tipo_mensagem TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index para busca rápida por telefone
CREATE INDEX IF NOT EXISTS idx_clientes_phone ON public.clientes(phone_numero);

-- Comentários
COMMENT ON TABLE public.clientes IS 'Tabela de clientes do WhatsApp Bot';
COMMENT ON COLUMN public.clientes.id IS 'ID único do cliente (UUID)';
COMMENT ON COLUMN public.clientes.nome_lead IS 'Nome do cliente/lead';
COMMENT ON COLUMN public.clientes.phone_numero IS 'Número de telefone (com código do país)';
COMMENT ON COLUMN public.clientes.message IS 'Primeira mensagem recebida';
COMMENT ON COLUMN public.clientes.tipo_mensagem IS 'Tipo da mensagem (conversation, audioMessage, imageMessage, etc)';

-- ============================================================
-- 2. Tabela de documentos para RAG (se necessário)
-- ============================================================

CREATE TABLE IF NOT EXISTS public.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    metadata JSONB,
    embedding vector(1536),  -- OpenAI ada-002 gera embeddings de 1536 dimensões
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Index para busca vetorial
CREATE INDEX IF NOT EXISTS idx_documents_embedding ON public.documents
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);

-- Index para busca por metadata
CREATE INDEX IF NOT EXISTS idx_documents_metadata ON public.documents USING gin(metadata);

COMMENT ON TABLE public.documents IS 'Documentos para RAG (Retrieval Augmented Generation)';
COMMENT ON COLUMN public.documents.content IS 'Conteúdo do documento';
COMMENT ON COLUMN public.documents.metadata IS 'Metadados em formato JSON';
COMMENT ON COLUMN public.documents.embedding IS 'Embedding vetorial do documento (OpenAI)';

-- ============================================================
-- 3. Habilitar extensão pgvector (se não estiver habilitada)
-- ============================================================

CREATE EXTENSION IF NOT EXISTS vector;

-- ============================================================
-- 4. Políticas de RLS (Row Level Security) - OPCIONAL
-- ============================================================

-- Se você quiser habilitar RLS:
-- ALTER TABLE public.clientes ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;

-- Política para permitir todas as operações (para API key)
-- CREATE POLICY "Allow all operations for service role" ON public.clientes
--     FOR ALL USING (true);

-- CREATE POLICY "Allow all operations for service role" ON public.documents
--     FOR ALL USING (true);

-- ============================================================
-- 5. Função de atualização automática de updated_at
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Triggers para atualização automática
CREATE TRIGGER update_clientes_updated_at
    BEFORE UPDATE ON public.clientes
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON public.documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================
-- FIM DO SCRIPT
-- ============================================================

-- Para verificar se as tabelas foram criadas:
-- SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
