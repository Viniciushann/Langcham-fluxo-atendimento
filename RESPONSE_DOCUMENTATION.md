# 📤 Documentação do Módulo de Respostas

Documentação completa do nó `response.py` - fragmentação e envio de mensagens.

---

## 📋 Visão Geral

O módulo **response** é responsável por:
1. Fragmentar respostas longas em mensagens menores
2. Limpar caracteres especiais que podem quebrar o JSON/WhatsApp
3. Enviar mensagens sequencialmente para o WhatsApp
4. Simular digitação para parecer natural

### Arquivo
- **Localização**: `src/nodes/response.py`
- **Funções Principais**:
  - `fragmentar_resposta(state: AgentState) -> AgentState`
  - `enviar_respostas(state: AgentState) -> AgentState`

---

## 🏗️ Arquitetura

```
┌────────────────────────────────────────────────────────┐
│          FASE 1: FRAGMENTAÇÃO                          │
│                                                        │
│  fragmentar_resposta()                                 │
│  ├─ Validar resposta do agente                        │
│  ├─ Quebrar em parágrafos (\n\n)                      │
│  ├─ Para cada parágrafo:                              │
│  │  ├─ Se > 300 chars: quebrar em frases             │
│  │  ├─ Se frase > 300: quebrar em palavras           │
│  │  └─ Manter integridade de frases                  │
│  └─ Salvar fragmentos no estado                       │
│                                                        │
└────────────────────────────────────────────────────────┘
                           │
                           ▼
┌────────────────────────────────────────────────────────┐
│          FASE 2: ENVIO                                 │
│                                                        │
│  enviar_respostas()                                    │
│  └─ Para cada fragmento:                              │
│     ├─ Enviar status "digitando"                      │
│     ├─ Aguardar 0.5s                                  │
│     ├─ Limpar caracteres especiais                    │
│     ├─ Enviar mensagem (retry: 3x)                    │
│     ├─ Log de sucesso/erro                            │
│     └─ Aguardar 1.5s antes do próximo                 │
│                                                        │
└────────────────────────────────────────────────────────┘
```

---

## ⚙️ Componentes

### 1. **quebrar_texto_inteligente()**

Algoritmo de fragmentação inteligente que respeita:
- Parágrafos (não quebra no meio)
- Frases completas (não quebra antes de . ! ?)
- Limite de caracteres (padrão: 300)

```python
def quebrar_texto_inteligente(texto: str, max_chars: int = 300) -> List[str]
```

**Lógica:**

1. **Texto pequeno**: Se ≤ max_chars, retorna inteiro
2. **Dividir por parágrafos**: Separa em `\\n\\n`
3. **Para cada parágrafo grande**:
   - Divide por frases (regex: `[.!?]+\\s+`)
   - Agrupa frases até atingir max_chars
   - Se frase sozinha > max_chars, quebra por palavras

**Exemplo:**

```python
texto = """Olá! Tudo bem?

Este é um parágrafo muito longo que precisa ser quebrado em partes menores para envio no WhatsApp."""

fragmentos = quebrar_texto_inteligente(texto, max_chars=50)

# Resultado:
# ['Olá! Tudo bem?',
#  'Este é um parágrafo muito longo que precisa',
#  'ser quebrado em partes menores para envio',
#  'no WhatsApp.']
```

### 2. **limpar_mensagem()**

Remove/escapa caracteres problemáticos para JSON/WhatsApp:

```python
def limpar_mensagem(texto: str) -> str
```

**Transformações:**

| Caractere | Ação | Razão |
|-----------|------|-------|
| `\` | `\\` | Escape barra |
| `"` | `\"` | Escape aspas |
| `\n` | `\\n` | Escape quebra de linha |
| `*` | `\\*` | Escape markdown |
| `_` | `\\_` | Escape markdown |
| `#` | `` | Remove hashtag |
| `\t` | ` ` | Substitui tab por espaço |

**Exemplo:**

```python
texto = 'Olá! "Teste" com *asterisco* e #hashtag'
limpo = limpar_mensagem(texto)
# Resultado: 'Olá! \\"Teste\\" com \\*asterisco\\* e hashtag'
```

### 3. **fragmentar_resposta()**

Fragmenta a resposta do agente em mensagens menores.

```python
async def fragmentar_resposta(state: AgentState) -> AgentState
```

**Fluxo:**

1. Valida `state["resposta_agente"]`
2. Obtém `max_fragment_size` do settings
3. Chama `quebrar_texto_inteligente()`
4. Salva em `state["respostas_fragmentadas"]`
5. Define `state["next_action"] = "enviar_respostas"`

**Saída de Log:**

```
============================================================
INICIANDO FRAGMENTAÇÃO DE RESPOSTA
============================================================
Resposta do agente (450 chars):
Olá! Tudo bem? 😊...
Tamanho máximo de fragmento: 300 chars
✅ Resposta fragmentada em 2 parte(s)
  Fragmento 1/2 (200 chars): Olá! Tudo bem?...
  Fragmento 2/2 (250 chars): Nossos serviços...
Fragmentação concluída em 0.003s
============================================================
```

### 4. **enviar_respostas()**

Envia fragmentos sequencialmente para o WhatsApp.

```python
async def enviar_respostas(state: AgentState) -> AgentState
```

**Fluxo Detalhado:**

1. **Validação**
   - Verifica fragmentos
   - Valida número do cliente

2. **Instanciação WhatsAppClient**
   ```python
   whatsapp = WhatsAppClient(
       api_url=settings.whatsapp_api_url,
       api_key=settings.whatsapp_api_key,
       instance=settings.whatsapp_instance
   )
   ```

3. **Loop de Envio** (para cada fragmento):

   a. **Status digitando**
   ```python
   await whatsapp.enviar_status_typing(cliente_numero)
   await asyncio.sleep(0.5)  # Simula digitação
   ```

   b. **Limpeza**
   ```python
   mensagem_limpa = limpar_mensagem(fragmento)
   ```

   c. **Envio com Retry**
   ```python
   max_tentativas = 3
   while tentativa < max_tentativas:
       resultado = await whatsapp.enviar_mensagem(
           telefone=cliente_numero,
           texto=mensagem_limpa
       )
       if resultado.get("sucesso"):
           break
       await asyncio.sleep(2)  # Aguarda antes de retry
   ```

   d. **Intervalo Natural**
   ```python
   await asyncio.sleep(1.5)  # Entre mensagens
   ```

4. **Estatísticas Finais**
   ```python
   state["envio_stats"] = {
       "total_fragmentos": 5,
       "enviados_sucesso": 5,
       "enviados_erro": 0,
       "tempo_total": 12.3,
       "taxa_sucesso": 100.0
   }
   ```

---

## 🎯 Casos de Uso

### Caso 1: Resposta Curta (< 300 chars)

**Entrada:**
```python
state["resposta_agente"] = "Olá! Como posso ajudar?"
```

**Processamento:**
```python
# Fragmentação
fragmentos = ["Olá! Como posso ajudar?"]  # 1 fragmento

# Envio
1. Status digitando
2. Aguarda 0.5s
3. Envia mensagem
4. Sem intervalo (última mensagem)
```

**Log:**
```
Resposta fragmentada em 1 parte(s)
Fragmento 1/1 enviado com sucesso!
Taxa de sucesso: 100.0%
Tempo total: 2.1s
```

### Caso 2: Resposta Média (300-600 chars)

**Entrada:**
```python
state["resposta_agente"] = """Olá! Tudo bem? 😊

Que bom que entrou em contato! Trabalhamos com instalação de drywall, gesso e forros.

Nossos serviços incluem paredes, divisórias, forros e rebaixamentos.

Posso ajudar com mais alguma coisa?"""
```

**Processamento:**
```python
# Fragmentação (por parágrafos)
fragmentos = [
    "Olá! Tudo bem? 😊",
    "Que bom que entrou em contato! Trabalhamos com instalação de drywall, gesso e forros.",
    "Nossos serviços incluem paredes, divisórias, forros e rebaixamentos.",
    "Posso ajudar com mais alguma coisa?"
]

# Envio (4 mensagens)
Total: ~10 segundos (4 msg × 2.0s médio cada)
```

### Caso 3: Resposta Longa (> 600 chars)

**Entrada:**
```python
state["resposta_agente"] = """[Resposta muito longa com múltiplos parágrafos,
listas, informações técnicas, etc...]"""
```

**Processamento:**
```python
# Fragmentação inteligente
# - Divide por parágrafos
# - Quebra parágrafos grandes em frases
# - Quebra frases gigantes em palavras

fragmentos = [...]  # 6-10 fragmentos

# Envio sequencial
# - Simula digitação entre cada
# - Parece conversa natural
```

---

## 🚨 Tratamento de Erros

### Erro: Resposta Vazia

```python
if not resposta_agente:
    logger.warning("Nenhuma resposta do agente")
    state["erro"] = "Resposta vazia"
    state["next_action"] = AcaoFluxo.ERRO.value
```

### Erro: Falha no Envio (com Retry)

```python
max_tentativas = 3
for tentativa in range(1, max_tentativas + 1):
    try:
        resultado = await whatsapp.enviar_mensagem(...)
        if resultado.get("sucesso"):
            break
    except Exception as e:
        if tentativa < max_tentativas:
            await asyncio.sleep(2)
        else:
            enviados_erro += 1
            # Continua para próximo fragmento
```

**Comportamento:**
- Tenta 3 vezes
- Aguarda 2s entre tentativas
- Se falhar tudo, **continua** para próximo fragmento
- Não interrompe fluxo completo

### Erro: Cliente WhatsApp não disponível

```python
try:
    whatsapp = WhatsAppClient(...)
except Exception as e:
    logger.error("Erro ao instanciar WhatsAppClient")
    state["erro"] = str(e)
    state["next_action"] = AcaoFluxo.ERRO.value
```

---

## 📊 Logging e Estatísticas

### Logs de Fragmentação

```
============================================================
INICIANDO FRAGMENTAÇÃO DE RESPOSTA
============================================================
Resposta do agente (523 chars):
Olá! Tudo bem? 😊 Que bom que entrou em contato...
Tamanho máximo de fragmento: 300 chars
✅ Resposta fragmentada em 3 parte(s)
  Fragmento 1/3 (145 chars): Olá! Tudo bem? 😊...
  Fragmento 2/3 (298 chars): Trabalhamos com instalação...
  Fragmento 3/3 (80 chars): Posso ajudar com mais alguma coisa?
Fragmentação concluída em 0.005s
============================================================
```

### Logs de Envio

```
============================================================
INICIANDO ENVIO DE RESPOSTAS
============================================================
Cliente: 5511999999999
Total de fragmentos a enviar: 3
WhatsAppClient inicializado
----------------------------------------
Fragmento 1/3
Tamanho: 145 chars
Preview: Olá! Tudo bem? 😊 Que bom que...
✅ Status 'digitando' enviado
Tentativa 1/3 de envio...
✅ Fragmento 1/3 enviado com sucesso!
Aguardando 1.5s antes do próximo fragmento...
----------------------------------------
Fragmento 2/3
...
============================================================
ESTATÍSTICAS DE ENVIO
============================================================
Total de fragmentos: 3
Enviados com sucesso: 3
Erros: 0
Taxa de sucesso: 100.0%
Tempo total: 8.45s
============================================================
```

### Estatísticas no Estado

```python
state["envio_stats"] = {
    "total_fragmentos": 3,
    "enviados_sucesso": 3,
    "enviados_erro": 0,
    "tempo_total": 8.45,
    "taxa_sucesso": 100.0
}
```

---

## 🔧 Configurações

### Variáveis de Ambiente

```env
# Tamanho máximo de fragmentos
MAX_FRAGMENT_SIZE=300

# WhatsApp API
WHATSAPP_API_URL=https://api.whatsapp.com/v1
WHATSAPP_API_KEY=your-key
WHATSAPP_INSTANCE=your-instance

# Timing
MESSAGE_GROUP_DELAY=13  # Não usado em response, mas importante
```

### Settings.py

```python
settings = get_settings()

settings.max_fragment_size        # 300
settings.whatsapp_api_url         # URL da API
settings.whatsapp_api_key         # Chave
settings.whatsapp_instance        # Instância
```

### Ajustar Intervalos

Edite em `response.py`:

```python
# Após enviar status digitando
await asyncio.sleep(0.5)  # ← Ajuste aqui

# Entre fragmentos
intervalo_entre_mensagens = 1.5  # ← Ajuste aqui
```

---

## 🧪 Testes

### Teste de Fragmentação

```bash
python src/nodes/response.py
```

**Saída:**
```
============================================================
TESTE DE FRAGMENTAÇÃO
============================================================

📝 Texto original (523 chars):
Olá! Tudo bem? 😊

Que bom que entrou em contato!...

------------------------------------------------------------

✂️ Fragmentado em 4 parte(s):

[Fragmento 1] (17 chars):
Olá! Tudo bem? 😊

[Fragmento 2] (148 chars):
Que bom que entrou em contato! Trabalhamos com instalação...

[Fragmento 3] (142 chars):
Nossos serviços incluem:
• Paredes de drywall...

[Fragmento 4] (105 chars):
Gostaria de agendar uma visita técnica gratuita...

✅ TESTE PASSOU!
```

### Teste de Limpeza

```bash
python src/nodes/response.py
```

**Saída:**
```
============================================================
TESTE DE LIMPEZA DE MENSAGENS
============================================================

Original: 'Teste com "aspas"'
Limpo:    'Teste com \\"aspas\\"'

Original: 'Teste com \n quebra de linha'
Limpo:    'Teste com \\n quebra de linha'

Original: 'Teste com *asteriscos* e _underscores_'
Limpo:    'Teste com \\*asteriscos\\* e \\_underscores\\_'

✅ TESTE CONCLUÍDO!
```

### Teste Manual

```python
import asyncio
from src.nodes.response import fragmentar_resposta, enviar_respostas
from src.models.state import criar_estado_inicial

async def teste():
    state = criar_estado_inicial()
    state["resposta_agente"] = """Olá! Tudo bem?

Trabalhamos com drywall e gesso.

Posso ajudar?"""
    state["cliente_numero"] = "5511999999999"

    # Fragmentar
    state = fragmentar_resposta(state)
    print(f"Fragmentos: {state['respostas_fragmentadas']}")

    # Enviar
    state = await enviar_respostas(state)
    print(f"Stats: {state['envio_stats']}")

asyncio.run(teste())
```

---

## 📈 Performance

### Métricas Típicas

| Métrica | Valor |
|---------|-------|
| **Tempo de fragmentação** | 1-5ms |
| **Tempo por mensagem** | 2-3s |
| **Intervalo entre mensagens** | 1.5s |
| **Tentativas de retry** | até 3 |
| **Taxa de sucesso** | >99% |

### Exemplo de Timeline

```
Fragmento 1:
0.0s - Status digitando enviado
0.5s - Mensagem enviada
0.7s - Confirmação recebida

1.5s - Intervalo (aguardar)

Fragmento 2:
3.2s - Status digitando enviado
3.7s - Mensagem enviada
3.9s - Confirmação recebida

Total: ~4 segundos para 2 mensagens
```

---

## 🔧 Manutenção

### Ajustar Tamanho de Fragmento

```env
# .env
MAX_FRAGMENT_SIZE=250  # ← Ajuste aqui
```

### Ajustar Timing Natural

```python
# response.py, linha ~350

# Após status digitando
await asyncio.sleep(0.8)  # Era 0.5s

# Entre fragmentos
intervalo_entre_mensagens = 2.0  # Era 1.5s
```

### Adicionar Novo Caractere de Limpeza

```python
def limpar_mensagem(texto: str) -> str:
    return (texto
        .replace('\\', '\\\\')
        .replace('"', '\\"')
        # ... existentes ...
        .replace('@', '')  # ← Novo: remove menções
    )
```

---

## 📚 Referências

- [WhatsApp Business API](https://developers.facebook.com/docs/whatsapp)
- [Regex em Python](https://docs.python.org/3/library/re.html)
- [Asyncio Sleep](https://docs.python.org/3/library/asyncio-task.html#asyncio.sleep)

---

**Status**: ✅ Implementado e funcional
**Última atualização**: 2025-10-21
