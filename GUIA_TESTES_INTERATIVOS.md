# 🧪 Guia de Testes Interativos - Modo n8n

## 📋 Visão Geral

Este guia explica como testar os nós do bot de forma **interativa**, similar ao fluxo visual do n8n, onde você executa **um nó por vez** e visualiza o input/output de cada etapa.

---

## 🎯 Opções Disponíveis

### **Opção 1: Jupyter Notebook** ⭐ RECOMENDADO

Teste visual e interativo com células executáveis.

### **Opção 2: Script Python**

Teste via terminal com menu interativo.

---

## 📓 OPÇÃO 1: Jupyter Notebook (Recomendado)

### ✅ Vantagens

- ✅ Execução célula por célula (como nós do n8n)
- ✅ Visualização rica de dados
- ✅ Pode modificar estado entre execuções
- ✅ Salva resultados para documentação
- ✅ Suporte a gráficos e visualizações
- ✅ Fácil depuração

### 📦 Instalação

```bash
# 1. Instalar Jupyter
pip install jupyter ipython

# 2. Navegar até o projeto
cd "C:\Users\Vinicius Soutenio\OneDrive\Sites Vinicius\Langcham. fluxo atendimento"

# 3. Iniciar Jupyter Notebook
jupyter notebook
```

### 🚀 Como Usar

1. **Abrir o notebook**:
   - No navegador que abrir, navegue até: `notebooks/teste_nos_interativo.ipynb`

2. **Executar célula por célula**:
   - Clique em uma célula
   - Pressione `Shift + Enter` para executar
   - Veja o resultado imediatamente abaixo

3. **Fluxo de execução**:
   ```
   CÉLULA 1: Imports e Setup
      ↓
   CÉLULA 2: Criar Estado Inicial (Webhook)
      ↓
   CÉLULA 3: NÓ 1 - validar_webhook
      ↓
   CÉLULA 4: NÓ 2 - verificar_cliente
      ↓
   CÉLULA 5: NÓ 3 - cadastrar_cliente (se necessário)
      ↓
   CÉLULA 6: NÓ 4 - processar_texto
      ↓
   CÉLULA 7: NÓ 5 - gerenciar_fila
      ↓
   CÉLULA 8: Visualizar Estado Completo
   ```

### 📝 Exemplo de Uso

**CÉLULA 2: Criar Webhook**
```python
webhook_data = {
    "body": {
        "data": {
            "key": {"remoteJid": "5562999999999@s.whatsapp.net"},
            "pushName": "João Silva",
            "message": {"conversation": "Olá"}
        }
    }
}
state = {"raw_webhook_data": webhook_data}
```

**CÉLULA 3: Executar NÓ 1**
```python
state = await validar_webhook(state)

# OUTPUT:
# ✓ Cliente número: 5562999999999
# ✓ Cliente nome: João Silva
# ✓ Próxima ação: verificar_cliente
```

**CÉLULA 4: Executar NÓ 2**
```python
state = await verificar_cliente(state)

# OUTPUT:
# ✓ Cliente existe: False
# ✓ Próxima ação: cadastrar_cliente
```

E assim por diante...

### 🔄 Modificar Estado Entre Nós

Você pode modificar o estado manualmente entre execuções:

```python
# Após executar validar_webhook
state["cliente_nome"] = "Novo Nome"  # Modificar manualmente

# Executar próximo nó
state = await verificar_cliente(state)
```

### 💾 Salvar Resultados

O notebook salva automaticamente. Você pode exportar:

```bash
# Exportar para HTML
jupyter nbconvert --to html notebooks/teste_nos_interativo.ipynb

# Exportar para PDF (requer wkhtmltopdf)
jupyter nbconvert --to pdf notebooks/teste_nos_interativo.ipynb
```

---

## 🐍 OPÇÃO 2: Script Python Interativo

### ✅ Vantagens

- ✅ Não requer Jupyter
- ✅ Execução via terminal
- ✅ Menu interativo
- ✅ Múltiplos cenários pré-programados

### 🚀 Como Usar

```bash
# Executar script
python teste_fluxo_interativo.py
```

### 📝 Menu de Opções

```
===========================================================
🧪 TESTE INTERATIVO DOS NÓS
===========================================================

Escolha uma opção:

1. Testar fluxo completo (cliente novo)
2. Testar cenário: cliente existente
3. Sair

===========================================================
```

### 🎬 Fluxo de Execução

Ao escolher opção 1:

```
1. Mostra webhook recebido
   📱 Webhook de: João Silva
   📞 Número: 5562999999999@s.whatsapp.net
   💬 Mensagem: Olá, quero saber...

2. Pressione ENTER → Executa NÓ 1
   ✓ cliente_numero: 5562999999999
   ✓ cliente_nome: João Silva
   ✓ next_action: verificar_cliente

3. Pressione ENTER → Executa NÓ 2
   ✓ cliente_existe: False
   ✓ next_action: cadastrar_cliente

4. Pressione ENTER → Executa NÓ 3
   ✓ cliente_id: novo_cliente_xyz789
   ✓ cliente_existe: True

5. Pressione ENTER → Continua...
```

### 🔀 Múltiplos Cenários

**Cenário 1: Cliente Novo**
- validar_webhook → verificar_cliente → **cadastrar_cliente** → processar_texto

**Cenário 2: Cliente Existente**
- validar_webhook → verificar_cliente → processar_texto (pula cadastro)

---

## 📊 Comparação das Opções

| Característica | Jupyter Notebook | Script Python |
|----------------|------------------|---------------|
| **Visualização** | ⭐⭐⭐⭐⭐ Rica | ⭐⭐⭐ Simples |
| **Flexibilidade** | ⭐⭐⭐⭐⭐ Total | ⭐⭐⭐ Média |
| **Facilidade** | ⭐⭐⭐⭐ Fácil | ⭐⭐⭐⭐⭐ Muito fácil |
| **Instalação** | Requer Jupyter | Nenhuma |
| **Modificar Estado** | ⭐⭐⭐⭐⭐ Sim | ⭐⭐ Limitado |
| **Salvar Resultados** | ⭐⭐⭐⭐⭐ Automático | ⭐ Não |
| **Debugging** | ⭐⭐⭐⭐⭐ Excelente | ⭐⭐⭐ Bom |

---

## 🎯 Casos de Uso

### Use Jupyter Notebook quando:
- ✅ Quer depurar e modificar estado em tempo real
- ✅ Precisa visualizar dados complexos
- ✅ Quer documentar testes
- ✅ Está desenvolvendo novos nós

### Use Script Python quando:
- ✅ Quer teste rápido sem setup
- ✅ Não tem Jupyter instalado
- ✅ Quer testar cenários pré-definidos
- ✅ Prefere terminal ao invés de navegador

---

## 🛠️ Configuração Completa

### 1. Instalar Dependências

```bash
# Dependências do projeto
pip install -r requirements.txt

# Jupyter (apenas para Opção 1)
pip install jupyter ipython
```

### 2. Configurar .env

```bash
# Copiar template
cp .env.example .env

# Editar com credenciais reais
# (necessário apenas para testes com nós reais)
```

### 3. Descomentar Imports

Em ambos os arquivos, quando estiver pronto para testar nós reais:

**No Jupyter Notebook (Célula 1):**
```python
# Descomentar estas linhas:
from src.nodes.webhook import validar_webhook, verificar_cliente
from src.nodes.media import processar_texto
# etc...
```

**No Script Python:**
```python
# Descomentar estas linhas:
# from src.nodes.webhook import validar_webhook
# state = await validar_webhook(state)
```

---

## 📚 Exemplos Práticos

### Exemplo 1: Testar Validação de Webhook

**Jupyter:**
```python
# CÉLULA 2: Criar webhook
state = {"raw_webhook_data": webhook_data}

# CÉLULA 3: Validar
state = await validar_webhook(state)
print(state["cliente_numero"])  # 5562999999999
```

**Script Python:**
Escolha opção 1 → Pressione ENTER na primeira pergunta

### Exemplo 2: Testar Cliente Existente

**Jupyter:**
```python
# CÉLULA 4: Forçar cliente existente
state["cliente_existe"] = True
state["cliente_id"] = "abc123"
# Pula CÉLULA 5 (cadastro)
# Vai direto para CÉLULA 6
```

**Script Python:**
Escolha opção 2 → Vê cenário de cliente existente

### Exemplo 3: Modificar Mensagem Entre Nós

**Jupyter:**
```python
# Após validar_webhook
state["mensagem_base64"] = "Nova mensagem modificada"

# Executar processar_texto com mensagem modificada
state = processar_texto(state)
```

---

## 🔧 Troubleshooting

### Problema: Jupyter não abre

**Solução:**
```bash
# Reinstalar Jupyter
pip uninstall jupyter
pip install jupyter ipython

# Ou usar JupyterLab
pip install jupyterlab
jupyter lab
```

### Problema: Imports não funcionam

**Solução:**
```python
# No notebook, adicionar na CÉLULA 1:
import sys
sys.path.insert(0, '..')  # Adiciona diretório pai ao path
```

### Problema: Erro ao executar nó

**Solução:**
1. Verificar se dependências estão instaladas
2. Verificar se .env está configurado
3. Ver logs para entender o erro

---

## 📖 Próximos Passos

Após dominar os testes interativos:

1. **Fase 4**: Implementar processamento de mídia
2. **Fase 5**: Implementar gerenciamento de fila
3. **Fase 9**: Montar grafo completo no LangGraph
4. **Teste integrado**: Executar grafo completo

---

## ✅ Checklist de Testes

### Antes de começar
- [ ] Python 3.11+ instalado
- [ ] Dependências instaladas (`pip install -r requirements.txt`)
- [ ] Jupyter instalado (para Opção 1)
- [ ] .env configurado

### Durante testes
- [ ] Testar cada nó individualmente
- [ ] Verificar input e output de cada nó
- [ ] Testar cenário: cliente novo
- [ ] Testar cenário: cliente existente
- [ ] Testar cenário: erro (webhook inválido)
- [ ] Modificar estado entre nós (Jupyter)

### Após testes
- [ ] Documentar bugs encontrados
- [ ] Salvar notebooks de teste
- [ ] Criar testes automatizados baseados nos resultados

---

## 🎊 Conclusão

O modo de teste interativo permite:

✅ Executar nós individualmente
✅ Visualizar input/output de cada etapa
✅ Depurar facilmente
✅ Modificar estado em tempo real
✅ Documentar testes

**Similar ao n8n, mas com total controle programático!**

---

**Arquivos:**
- `notebooks/teste_nos_interativo.ipynb` - Jupyter Notebook
- `teste_fluxo_interativo.py` - Script Python
- `GUIA_TESTES_INTERATIVOS.md` - Este guia

**Próximo passo:** Escolha uma opção e comece a testar! 🚀
