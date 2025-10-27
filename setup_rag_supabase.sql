-- ============================================================
-- CONFIGURAÇÃO COMPLETA DO RAG NO SUPABASE
-- Execute este script no SQL Editor do Supabase
-- URL: https://znyypdwnqdlvqwwvffzk.supabase.co/project/_/sql/new
-- ============================================================

-- 1. HABILITAR EXTENSÃO PGVECTOR (se ainda não estiver)
-- ============================================================
CREATE EXTENSION IF NOT EXISTS vector;

-- Verificar se foi habilitada
SELECT * FROM pg_extension WHERE extname = 'vector';


-- 2. GARANTIR QUE A TABELA DOCUMENTS EXISTE
-- ============================================================
CREATE TABLE IF NOT EXISTS public.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding vector(1536),  -- OpenAI ada-002 gera embeddings de 1536 dimensões
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Adicionar índice para busca vetorial (se não existir)
-- NOTA: ivfflat requer muita memória. Para poucos documentos (<1000),
-- o índice não é necessário. Vamos criar apenas se tiver muitos documentos.
-- Para criar depois quando tiver mais documentos:
-- CREATE INDEX idx_documents_embedding ON public.documents
-- USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);

-- Por enquanto, vamos usar busca sem índice (funciona bem para <10k documentos)
-- O Postgres fará busca sequencial que é rápida o suficiente para poucos docs

-- Adicionar índice para metadata
CREATE INDEX IF NOT EXISTS idx_documents_metadata ON public.documents
USING gin(metadata);

-- Comentários
COMMENT ON TABLE public.documents IS 'Documentos vetorizados para RAG (Retrieval Augmented Generation)';
COMMENT ON COLUMN public.documents.content IS 'Conteúdo do documento';
COMMENT ON COLUMN public.documents.metadata IS 'Metadados em formato JSON (categoria, fonte, etc)';
COMMENT ON COLUMN public.documents.embedding IS 'Embedding vetorial do documento (OpenAI ada-002, 1536 dim)';


-- 3. FUNÇÃO DE BUSCA POR SIMILARIDADE
-- ============================================================

-- Deletar função antiga se existir
DROP FUNCTION IF EXISTS match_documents(vector(1536), int, jsonb);
DROP FUNCTION IF EXISTS match_documents(vector(1536), int);

-- Criar função de busca vetorial
CREATE OR REPLACE FUNCTION match_documents (
  query_embedding vector(1536),
  match_count int DEFAULT 5,
  filter jsonb DEFAULT '{}'::jsonb
)
RETURNS TABLE (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    documents.id,
    documents.content,
    documents.metadata,
    1 - (documents.embedding <=> query_embedding) as similarity
  FROM documents
  WHERE
    CASE
      WHEN filter = '{}'::jsonb THEN true
      ELSE documents.metadata @> filter
    END
  ORDER BY documents.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Comentário da função
COMMENT ON FUNCTION match_documents IS 'Busca documentos similares usando distância de cosseno. Retorna os N documentos mais similares ao embedding fornecido.';


-- 4. FUNÇÃO AUXILIAR PARA BUSCA POR TEXTO
-- ============================================================

-- Busca simples por palavra-chave (fallback se embeddings falharem)
CREATE OR REPLACE FUNCTION search_documents_text (
  search_query text,
  match_count int DEFAULT 5
)
RETURNS TABLE (
  id uuid,
  content text,
  metadata jsonb,
  excerpt text
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    public.documents.id,
    public.documents.content,
    public.documents.metadata,
    LEFT(public.documents.content, 200) as excerpt
  FROM public.documents
  WHERE
    public.documents.content ILIKE '%' || search_query || '%'
  ORDER BY
    public.documents.created_at DESC
  LIMIT match_count;
END;
$$;


-- 5. TRIGGER PARA ATUALIZAÇÃO AUTOMÁTICA DE updated_at
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Criar trigger se não existir
DROP TRIGGER IF EXISTS update_documents_updated_at ON public.documents;

CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON public.documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- 6. INSERIR DOCUMENTOS DE EXEMPLO (OPCIONAL)
-- ============================================================

-- Inserir apenas se a tabela estiver vazia
INSERT INTO public.documents (content, metadata, embedding)
SELECT
    'Centro Oeste Drywall: Especialistas em instalação de drywall, forro de gesso, sancas e divisórias. Atendemos Goiânia e região com qualidade e agilidade.',
    '{"categoria": "servicos", "tipo": "apresentacao"}'::jsonb,
    NULL  -- Embedding será gerado pelo Python
WHERE NOT EXISTS (
    SELECT 1 FROM public.documents WHERE content LIKE '%Centro Oeste Drywall%'
);

INSERT INTO public.documents (content, metadata, embedding)
SELECT
    'Serviços oferecidos: Instalação de drywall para paredes e forros, sancas de gesso, nichos decorativos, isolamento acústico e térmico. Orçamento gratuito.',
    '{"categoria": "servicos", "tipo": "lista"}'::jsonb,
    NULL
WHERE NOT EXISTS (
    SELECT 1 FROM public.documents WHERE content LIKE '%Serviços oferecidos%'
);

INSERT INTO public.documents (content, metadata, embedding)
SELECT
    'Preços e orçamento: Trabalhamos com preços competitivos. O valor varia conforme o tipo de serviço, metragem e acabamento. Entre em contato para orçamento personalizado sem compromisso.',
    '{"categoria": "comercial", "tipo": "precos"}'::jsonb,
    NULL
WHERE NOT EXISTS (
    SELECT 1 FROM public.documents WHERE content LIKE '%Preços e orçamento%'
);

INSERT INTO public.documents (content, metadata, embedding)
SELECT
    'Horário de atendimento: Segunda a sexta das 8h às 18h, sábados das 8h às 12h. Atendimento via WhatsApp 24h para solicitação de orçamentos.',
    '{"categoria": "atendimento", "tipo": "horarios"}'::jsonb,
    NULL
WHERE NOT EXISTS (
    SELECT 1 FROM public.documents WHERE content LIKE '%Horário de atendimento%'
);

INSERT INTO public.documents (content, metadata, embedding)
SELECT
    'Drywall é uma placa de gesso acartonado usada para construção de paredes, forros e divisórias. Vantagens: instalação rápida, menor peso, facilita passagem de cabos e tubulações, excelente custo-benefício.',
    '{"categoria": "informativo", "tipo": "produto"}'::jsonb,
    NULL
WHERE NOT EXISTS (
    SELECT 1 FROM public.documents WHERE content LIKE '%Drywall é uma placa%'
);


-- 7. VERIFICAR INSTALAÇÃO
-- ============================================================

-- Contar documentos
SELECT COUNT(*) as total_documentos FROM public.documents;

-- Ver exemplos
SELECT id, LEFT(content, 100) as preview, metadata
FROM public.documents
LIMIT 5;

-- Testar busca por texto
SELECT * FROM search_documents('drywall', 3);


-- ============================================================
-- FIM DO SCRIPT
-- ============================================================

-- PRÓXIMOS PASSOS:
-- 1. Executar este script no SQL Editor do Supabase
-- 2. Verificar se não há erros
-- 3. Gerar embeddings para os documentos usando Python
-- 4. Testar a busca vetorial

-- Para gerar embeddings via Python, execute:
-- python gerar_embeddings.py
