# 🤖 Guia Completo - Configurar RAG no Supabase

Este guia mostra como configurar completamente o sistema RAG (Retrieval Augmented Generation) para que o bot possa buscar informações na base de conhecimento.

---

## 📋 O que é RAG?

RAG permite que o bot:
- ✅ Busque informações relevantes em uma base de documentos
- ✅ Responda perguntas com dados específicos da empresa
- ✅ Use contexto atualizado sem re-treinar o modelo
- ✅ Forneça respostas mais precisas e confiáveis

---

## 🎯 Passo a Passo

### ✅ PASSO 1: Executar Script SQL no Supabase

1. Acesse o SQL Editor do Supabase:
   ```
   https://znyypdwnqdlvqwwvffzk.supabase.co/project/_/sql/new
   ```

2. Abra o arquivo `setup_rag_supabase.sql` e copie todo o conteúdo

3. Cole no SQL Editor do Supabase

4. Clique em **"Run"** ou pressione `Ctrl + Enter`

5. Aguarde a execução (deve levar ~5 segundos)

6. Verifique se não há erros (mensagens em vermelho)

**O que este script faz:**
- ✅ Habilita extensão `pgvector` (para busca vetorial)
- ✅ Cria/verifica tabela `documents`
- ✅ Cria índices para busca eficiente
- ✅ Cria função `match_documents` (busca por similaridade)
- ✅ Insere 5 documentos de exemplo
- ✅ Cria triggers para atualização automática

---

### ✅ PASSO 2: Gerar Embeddings dos Documentos

Os embeddings são vetores numéricos que representam o significado dos textos. Precisamos gerá-los usando OpenAI.

Execute no terminal:

```bash
python gerar_embeddings.py
```

**O que vai acontecer:**
1. Script busca todos os documentos sem embedding
2. Para cada documento:
   - Gera embedding usando OpenAI (text-embedding-ada-002)
   - Salva o embedding no Supabase
3. Mostra progresso e resultado final

**Saída esperada:**
```
============================================================
GERANDO EMBEDDINGS DOS DOCUMENTOS
============================================================

[1/4] Buscando documentos sem embedding...
    Encontrados 5 documentos para processar

[2/4] Gerando embeddings com OpenAI...
    [1/5] Processando documento: Centro Oeste Drywall...
         OK - Embedding gerado e salvo (1536 dimensões)
    ...

[3/4] Embeddings gerados: 5/5

[4/4] Verificando resultados...
    Total de documentos com embedding: 5

============================================================
CONCLUÍDO!
============================================================
```

**Custo:** ~$0.0001 por documento (muito barato!)

---

### ✅ PASSO 3: Testar o Sistema RAG

Agora vamos testar se tudo está funcionando:

```bash
python testar_rag.py
```

**O que vai acontecer:**
1. Verifica se a função `match_documents` existe
2. Testa 4 queries diferentes:
   - "Quanto custa instalação de drywall?"
   - "Quais serviços vocês oferecem?"
   - "Qual o horário de atendimento?"
   - "O que é drywall?"
3. Para cada query:
   - Gera embedding da pergunta
   - Busca documentos similares
   - Mostra os 3 documentos mais relevantes
   - Mostra score de similaridade

**Saída esperada:**
```
============================================================
TESTANDO SISTEMA RAG
============================================================

[TESTE 1/4] Query: 'Quanto custa instalação de drywall?'
------------------------------------------------------------
  [1/3] Gerando embedding da query...
       OK - Embedding gerado (1536 dims)
  [2/3] Buscando documentos similares...
       OK - 3 documentos encontrados
  [3/3] Resultados:

       Documento 1:
         Similaridade: 0.8542 (85.4%)
         Categoria: comercial
         Conteudo: Preços e orçamento: Trabalhamos com preços...

       Documento 2:
         Similaridade: 0.7234 (72.3%)
         Categoria: servicos
         Conteudo: Serviços oferecidos: Instalação de drywall...
```

---

## 🎉 Pronto! RAG Configurado

Se todos os passos funcionaram, o RAG está 100% configurado!

---

## 🧪 Como Usar no Bot

O bot já está preparado para usar o RAG automaticamente. Quando um cliente fizer uma pergunta:

1. Bot processa a mensagem
2. **Agente busca no RAG** documentos relevantes
3. Agente usa os documentos como contexto
4. Gera resposta baseada nos documentos encontrados

**Exemplo de uso no código:**
```python
from src.clients.supabase_client import criar_supabase_client

# No nó do agente
supabase = criar_supabase_client(settings.supabase_url, settings.supabase_key)
documentos = await supabase.buscar_documentos_rag(
    query="preços de instalação",
    limit=3
)

# documentos contém os textos mais relevantes
contexto = "\n".join([doc['content'] for doc in documentos])
```

---

## 📝 Adicionar Mais Documentos

Para adicionar novos documentos à base de conhecimento:

### Opção 1: Via SQL (Supabase)

```sql
INSERT INTO public.documents (content, metadata)
VALUES (
    'Seu conteúdo aqui...',
    '{"categoria": "servicos", "tipo": "novo"}'::jsonb
);
```

Depois execute: `python gerar_embeddings.py`

### Opção 2: Via Python

```python
from src.clients.supabase_client import criar_supabase_client
from src.config.settings import get_settings

settings = get_settings()
supabase = criar_supabase_client(settings.supabase_url, settings.supabase_key)

# Inserir documento
supabase.client.table("documents").insert({
    "content": "Seu conteúdo aqui...",
    "metadata": {"categoria": "servicos", "tipo": "novo"}
}).execute()

# Gerar embedding
# Execute: python gerar_embeddings.py
```

---

## 🔍 Verificar Status do RAG

Para verificar quantos documentos você tem:

```sql
-- Total de documentos
SELECT COUNT(*) FROM documents;

-- Documentos com embedding
SELECT COUNT(*) FROM documents WHERE embedding IS NOT NULL;

-- Ver todos os documentos
SELECT id, LEFT(content, 100) as preview, metadata
FROM documents
ORDER BY created_at DESC;
```

---

## ⚠️ Troubleshooting

### Erro: "Could not find the function match_documents"

**Solução:** Execute o script SQL novamente (`setup_rag_supabase.sql`)

### Erro: "extension vector does not exist"

**Solução:**
1. Vá em Database > Extensions no Supabase
2. Habilite "vector"
3. Execute o script SQL novamente

### Erro: OpenAI rate limit

**Solução:** Aguarde alguns segundos e tente novamente

### Embeddings não foram gerados

**Solução:**
1. Verifique se OPENAI_API_KEY está configurada
2. Execute: `python gerar_embeddings.py`

---

## 📊 Custos Estimados

**OpenAI Embeddings (text-embedding-ada-002):**
- $0.0001 por 1K tokens
- ~1 documento = 100 tokens = $0.00001
- 1000 documentos ≈ $0.01 (muito barato!)

**Supabase:**
- Plano gratuito suporta até 500MB de dados
- RAG usa muito pouco espaço

---

## 🎯 Próximos Passos

1. ✅ Adicione documentos relevantes sobre sua empresa
2. ✅ Teste diferentes queries
3. ✅ Ajuste os metadados (categorias)
4. ✅ Configure filtros por categoria se necessário
5. ✅ Integre com o bot principal

---

## 📚 Recursos Úteis

- [Supabase Vector Docs](https://supabase.com/docs/guides/ai/vector-columns)
- [OpenAI Embeddings Guide](https://platform.openai.com/docs/guides/embeddings)
- [pgvector Documentation](https://github.com/pgvector/pgvector)

---

**Dúvidas?** Entre em contato ou consulte a documentação do projeto.

**Versão:** 1.0
**Última atualização:** 2025-10-27
