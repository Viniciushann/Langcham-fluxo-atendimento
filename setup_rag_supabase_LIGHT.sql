-- ============================================================
-- CONFIGURAÇÃO RAG PARA SUPABASE (VERSÃO LEVE - SEM ÍNDICE IVFFLAT)
-- Execute este script no SQL Editor do Supabase
-- URL: https://znyypdwnqdlvqwwvffzk.supabase.co/project/_/sql/new
-- ============================================================

-- Esta versão NÃO cria o índice ivfflat que requer muita memória
-- Funciona perfeitamente para até 10.000 documentos
-- Busca será um pouco mais lenta mas ainda muito rápida

-- ============================================================
-- PASSO 1: HABILITAR EXTENSÃO PGVECTOR
-- ============================================================
CREATE EXTENSION IF NOT EXISTS vector;

-- Verificar
SELECT extname, extversion FROM pg_extension WHERE extname = 'vector';


-- ============================================================
-- PASSO 2: CRIAR/VERIFICAR TABELA DOCUMENTS
-- ============================================================
CREATE TABLE IF NOT EXISTS public.documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}'::jsonb,
    embedding vector(1536),  -- OpenAI ada-002 = 1536 dimensões
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Apenas índice para metadata (esse é leve e sempre útil)
CREATE INDEX IF NOT EXISTS idx_documents_metadata ON public.documents
USING gin(metadata);

-- Índice simples para created_at (útil para ordenação)
CREATE INDEX IF NOT EXISTS idx_documents_created ON public.documents(created_at DESC);

-- Comentários
COMMENT ON TABLE public.documents IS 'Documentos vetorizados para RAG';
COMMENT ON COLUMN public.documents.content IS 'Conteúdo do documento (texto)';
COMMENT ON COLUMN public.documents.metadata IS 'Metadados: categoria, fonte, tags, etc';
COMMENT ON COLUMN public.documents.embedding IS 'Vetor embedding (OpenAI ada-002, 1536 dims)';


-- ============================================================
-- PASSO 3: FUNÇÃO DE BUSCA POR SIMILARIDADE
-- ============================================================

-- Remover funções antigas se existirem
DROP FUNCTION IF EXISTS match_documents(vector(1536), int, jsonb);
DROP FUNCTION IF EXISTS match_documents(vector(1536), int);
DROP FUNCTION IF EXISTS match_documents;

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
  FROM public.documents
  WHERE
    embedding IS NOT NULL
    AND (
      CASE
        WHEN filter = '{}'::jsonb THEN true
        ELSE documents.metadata @> filter
      END
    )
  ORDER BY documents.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

COMMENT ON FUNCTION match_documents IS 'Busca vetorial por similaridade de cosseno. Retorna top N documentos mais similares.';


-- ============================================================
-- PASSO 4: FUNÇÃO AUXILIAR - BUSCA POR TEXTO
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
    documents.id,
    documents.content,
    documents.metadata,
    LEFT(documents.content, 200) as excerpt
  FROM public.documents
  WHERE
    documents.content ILIKE '%' || search_query || '%'
  ORDER BY
    created_at DESC
  LIMIT match_count;
END;
$$;


-- ============================================================
-- PASSO 5: TRIGGER PARA AUTO-UPDATE DE updated_at
-- ============================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

DROP TRIGGER IF EXISTS update_documents_updated_at ON public.documents;

CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON public.documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();


-- ============================================================
-- PASSO 6: INSERIR DOCUMENTOS DE EXEMPLO
-- ============================================================

-- Apenas insere se não existir
INSERT INTO public.documents (content, metadata, embedding)
SELECT
    'Centro Oeste Drywall é especialista em instalação de drywall, forro de gesso, sancas decorativas e divisórias. Atendemos Goiânia e região metropolitana com qualidade, agilidade e preços competitivos. Nossa equipe é altamente qualificada e utiliza materiais de primeira linha.',
    '{"categoria": "empresa", "tipo": "apresentacao", "tags": ["sobre", "empresa", "servicos"]}'::jsonb,
    NULL
WHERE NOT EXISTS (
    SELECT 1 FROM public.documents WHERE content LIKE '%Centro Oeste Drywall é especialista%'
);

INSERT INTO public.documents (content, metadata, embedding)
SELECT
    'Serviços oferecidos pela Centro Oeste Drywall: Instalação completa de paredes em drywall, forros de gesso liso e decorativo, sancas abertas e fechadas, nichos e prateleiras, divisórias para ambientes comerciais e residenciais, isolamento acústico, isolamento térmico, acabamento com massa corrida e pintura. Todos os serviços incluem garantia.',
    '{"categoria": "servicos", "tipo": "lista_completa", "tags": ["servicos", "drywall", "instalacao"]}'::jsonb,
    NULL
WHERE NOT EXISTS (
    SELECT 1 FROM public.documents WHERE content LIKE '%Serviços oferecidos pela Centro Oeste%'
);

INSERT INTO public.documents (content, metadata, embedding)
SELECT
    'Preços e orçamentos: Nossos valores variam de acordo com o tipo de serviço, metragem, tipo de acabamento e prazo desejado. Em média, instalação de drywall custa entre R$ 40 a R$ 80 por m², forros entre R$ 60 a R$ 120 por m², e sancas a partir de R$ 150 o metro linear. Fazemos orçamento gratuito e personalizado. Entre em contato para uma avaliação sem compromisso.',
    '{"categoria": "comercial", "tipo": "precos", "tags": ["preco", "orcamento", "valores"]}'::jsonb,
    NULL
WHERE NOT EXISTS (
    SELECT 1 FROM public.documents WHERE content LIKE '%Preços e orçamentos: Nossos valores%'
);

INSERT INTO public.documents (content, metadata, embedding)
SELECT
    'Horário de atendimento: Atendemos de segunda a sexta-feira das 8h às 18h, e aos sábados das 8h às 12h. Nosso WhatsApp funciona 24 horas para recebimento de solicitações de orçamento, que serão respondidas no próximo dia útil. Para emergências, consulte disponibilidade pelo telefone.',
    '{"categoria": "atendimento", "tipo": "horarios", "tags": ["horario", "atendimento", "contato"]}'::jsonb,
    NULL
WHERE NOT EXISTS (
    SELECT 1 FROM public.documents WHERE content LIKE '%Horário de atendimento: Atendemos%'
);

INSERT INTO public.documents (content, metadata, embedding)
SELECT
    'O que é drywall? Drywall, também conhecido como gesso acartonado, é um sistema construtivo que utiliza placas de gesso revestidas com papel cartão. Principais vantagens: instalação rápida e limpa, menor peso estrutural, facilita passagem de instalações elétricas e hidráulicas, permite acabamentos diversos, excelente isolamento acústico, ótimo custo-benefício comparado à alvenaria tradicional. Ideal para reformas e construções modernas.',
    '{"categoria": "informativo", "tipo": "explicacao", "tags": ["drywall", "informacao", "vantagens"]}'::jsonb,
    NULL
WHERE NOT EXISTS (
    SELECT 1 FROM public.documents WHERE content LIKE '%O que é drywall? Drywall, também conhecido%'
);


-- ============================================================
-- PASSO 7: VERIFICAÇÕES FINAIS
-- ============================================================

-- Total de documentos
SELECT
    COUNT(*) as total_docs,
    COUNT(embedding) as docs_com_embedding,
    COUNT(*) - COUNT(embedding) as docs_sem_embedding
FROM public.documents;

-- Ver documentos inseridos
SELECT
    id,
    LEFT(content, 80) as preview,
    metadata->>'categoria' as categoria,
    metadata->>'tipo' as tipo,
    CASE WHEN embedding IS NULL THEN 'SEM EMBEDDING' ELSE 'COM EMBEDDING' END as status_embedding
FROM public.documents
ORDER BY created_at DESC
LIMIT 10;

-- Testar função de busca por texto
SELECT * FROM search_documents_text('drywall', 3);


-- ============================================================
-- SUCESSO!
-- ============================================================

-- Próximos passos:
-- 1. Execute: python gerar_embeddings.py
-- 2. Execute: python testar_rag.py
-- 3. Comece a usar o RAG no bot!

-- NOTA sobre performance:
-- Sem índice ivfflat, busca será um pouco mais lenta mas ainda muito rápida
-- Para até 10.000 documentos: <50ms de busca
-- Se precisar de mais performance no futuro (>10k docs), pode criar o índice:
--   CREATE INDEX idx_documents_embedding ON public.documents
--   USING ivfflat (embedding vector_cosine_ops) WITH (lists = 10);
