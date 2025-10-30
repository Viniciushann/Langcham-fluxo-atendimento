# 🚀 MONITORAMENTO DO DEPLOY - Correção do Telefone do Técnico

## 📊 Informações do Deploy

- **Commit**: `fba4eab`
- **Branch**: `main`
- **Autor**: Viniciushann
- **Data/Hora**: 2025-10-29
- **Tipo**: Deploy Automático via GitHub Actions
- **Servidor**: Hetzner Cloud (IP: 46.62.155.254)

---

## 🔍 Como Monitorar o Deploy

### 1️⃣ **GitHub Actions (Deploy Automático)**

Acesse: https://github.com/Viniciushann/Langcham-fluxo-atendimento/actions

**O que procurar:**
- ✅ Workflow: "Deploy to Hetzner #24" (ou próximo número)
- ✅ Status: Running → Success
- ✅ Commit: `fba4eab Fix: Corrigir número do técnico...`

**Tempo estimado:** 2-5 minutos

---

### 2️⃣ **Portainer (Status do Serviço)**

Acesse seu Portainer e verifique:

**Caminho:** Stacks → whatsapp-bot

**Verificações:**
- ✅ Status: Running
- ✅ Replicas: 1/1
- ✅ Updated: Deve mostrar timestamp recente

**OU**

**Caminho:** Services → whatsapp-bot

**Verificações:**
- ✅ Status: Running
- ✅ Tasks: 1/1 running
- ✅ Image: Deve ter sido atualizada recentemente

---

### 3️⃣ **Logs do Serviço (Verificação Crítica)**

#### Via Portainer:
1. Services → whatsapp-bot → Logs
2. Procurar por estas mensagens:

```
✅ "📞 Sistema de notificação configurado com 2 número(s)"
✅ "Service Account carregada com sucesso"
✅ "Serviço do Google Calendar inicializado"
```

#### Via SSH (se tiver acesso):
```bash
ssh usuario@46.62.155.254

# Ver logs em tempo real
docker service logs -f whatsapp-bot --tail 50

# Procurar especificamente por notificação
docker service logs whatsapp-bot --tail 100 | grep -i "notificação\|técnico"
```

---

## ✅ CHECKLIST DE VALIDAÇÃO PÓS-DEPLOY

### **Fase 1: Deploy Bem-Sucedido** (0-5 minutos)
- [ ] GitHub Actions mostra "Success" ✅
- [ ] Portainer mostra serviço "Running"
- [ ] Não há erros críticos nos logs

### **Fase 2: Sistema Inicializado** (5-10 minutos)
- [ ] Log mostra: "📞 Sistema de notificação configurado com 2 número(s)"
- [ ] Log mostra: "Service Account carregada com sucesso"
- [ ] Nenhum erro de importação ou sintaxe

### **Fase 3: Teste Funcional** (10-15 minutos)
- [ ] Fazer agendamento de teste via WhatsApp
- [ ] Evento criado no Google Calendar
- [ ] Técnico recebe notificação no WhatsApp (55628540075)
- [ ] Log mostra: "✅ Técnico notificado com sucesso: 55628540075"

### **Fase 4: Monitoramento Contínuo** (15-30 minutos)
- [ ] Nenhum erro novo nos logs
- [ ] Serviço permanece estável
- [ ] Resposta aos clientes funcionando normalmente

---

## 🔎 Mensagens de Log Esperadas

### ✅ **Sucesso - O que você DEVE ver:**

```
INFO - 📞 Sistema de notificação configurado com 2 número(s)
INFO - Service Account carregada com sucesso
INFO - Serviço do Google Calendar inicializado
INFO - 📤 Tentativa 1/2: Notificando técnico 55628540075
INFO - ✅ Técnico notificado com sucesso: 55628540075
```

### ⚠️ **Atenção - Pode acontecer (não é crítico):**

```
WARNING - ⚠️ Resposta vazia ao enviar para 55628540075
INFO - 📤 Tentativa 2/2: Notificando técnico 556281091167
```

Isso significa que tentou o número principal, falhou, e tentou o backup. É esperado se o backup não tiver WhatsApp.

### ❌ **Erro - NÃO deve aparecer:**

```
ERROR - Arquivo de credenciais não encontrado
ERROR - Erro ao autenticar com Service Account
ERROR - ModuleNotFoundError
ERROR - SyntaxError
```

Se aparecer, há um problema que precisa ser investigado.

---

## 🧪 Como Fazer Teste Funcional

### **Teste 1: Agendamento Completo**

1. **Via WhatsApp**, envie mensagem para o bot:
   ```
   Olá, gostaria de agendar uma visita
   ```

2. **Bot deve responder** pedindo informações

3. **Forneça dados**:
   - Nome: [Seu nome de teste]
   - Telefone: [Seu telefone]
   - Endereço: [Endereço de teste]
   - Data/Hora: [Próximo dia útil, horário comercial]

4. **Verificar**:
   - ✅ Bot confirma agendamento
   - ✅ Evento aparece no Google Calendar
   - ✅ Técnico recebe notificação no WhatsApp

### **Teste 2: Verificar Logs**

```bash
# Ver log específico do agendamento
docker service logs whatsapp-bot | grep -A 5 "NOVO AGENDAMENTO"

# Ver se técnico foi notificado
docker service logs whatsapp-bot | grep "Técnico notificado"
```

---

## 🆘 TROUBLESHOOTING

### **Problema 1: GitHub Actions falhou**

**Sintomas:**
- Status: Failed ❌
- Build error ou deploy error

**Solução:**
1. Verificar logs do GitHub Actions
2. Se erro de build: verificar sintaxe Python
3. Se erro de deploy: verificar conexão SSH com Hetzner

**Rollback:**
```bash
git revert HEAD
git push origin main
```

---

### **Problema 2: Serviço não inicia**

**Sintomas:**
- Portainer mostra: 0/1 replicas
- Logs mostram erros de inicialização

**Solução:**
1. Verificar logs completos:
   ```bash
   docker service logs whatsapp-bot --tail 200
   ```

2. Verificar se variáveis de ambiente estão corretas:
   ```bash
   docker service inspect whatsapp-bot | grep -i "env"
   ```

3. Verificar se imagem foi atualizada:
   ```bash
   docker service ps whatsapp-bot
   ```

**Rollback:**
```bash
# Via Portainer: Services → whatsapp-bot → Rollback
# OU via CLI:
docker service rollback whatsapp-bot
```

---

### **Problema 3: Notificação ainda não funciona**

**Sintomas:**
- Agendamento criado ✅
- Mas técnico não recebe notificação ❌

**Diagnóstico:**

1. **Verificar logs**:
   ```bash
   docker service logs whatsapp-bot | grep -i "notificar\|técnico"
   ```

2. **Procurar por**:
   - "Número não existe no WhatsApp" → Verificar se número tem WhatsApp ativo
   - "Requisição inválida" → Verificar Evolution API
   - "Erro ao notificar" → Ver detalhes do erro

3. **Testar manualmente** (via Evolution API):
   ```bash
   curl -X POST "https://evolution.centrooestedrywalldry.com.br/message/sendText/Centro_oeste_draywal" \
     -H "apikey: SUA_API_KEY" \
     -H "Content-Type: application/json" \
     -d '{"number":"55628540075","text":"Teste manual do deploy"}'
   ```

**Solução:**
- Se número não tem WhatsApp: Atualizar `TELEFONE_TECNICO` para número válido
- Se Evolution API com problema: Verificar status da API
- Se credenciais inválidas: Verificar `WHATSAPP_API_KEY`

---

### **Problema 4: Serviço OK mas bot não responde**

**Sintomas:**
- Serviço running ✅
- Logs sem erros ✅
- Mas bot não responde mensagens ❌

**Diagnóstico:**

1. **Verificar webhook**:
   ```bash
   curl https://bot.automacaovn.shop/health
   ```
   Deve retornar: `{"status":"healthy"}`

2. **Verificar Evolution API**:
   - Acessar Evolution API console
   - Verificar se instância está conectada
   - Verificar se webhook está configurado

**Solução:**
- Reconfigurar webhook na Evolution API
- Verificar se URL está correta: `https://bot.automacaovn.shop/webhook`

---

## 📊 Métricas de Sucesso

### **Deploy bem-sucedido se:**

1. ✅ GitHub Actions: Success
2. ✅ Portainer: Service Running (1/1)
3. ✅ Logs: "Sistema de notificação configurado com 2 número(s)"
4. ✅ Teste: Agendamento criado E técnico notificado
5. ✅ Estabilidade: 15+ minutos sem erros

### **Tempo estimado total:** 15-30 minutos

---

## 📞 Números Configurados

| Tipo | Número | Formato | Status |
|------|--------|---------|--------|
| **Principal** | 55628540075 | 12 dígitos (antigo) | ✅ Deve funcionar |
| **Backup** | 556281091167 | 13 dígitos (novo) | ⚠️ Verificar se tem WhatsApp |

---

## 🔗 Links Úteis

- **GitHub Actions**: https://github.com/Viniciushann/Langcham-fluxo-atendimento/actions
- **Portainer**: [Seu link do Portainer]
- **Bot Health**: https://bot.automacaovn.shop/health
- **Evolution API**: https://evolution.centrooestedrywalldry.com.br

---

## 📝 Notas Finais

### **IMPORTANTE:**

1. O sistema **nunca bloqueia** agendamentos se notificação falhar
2. Agendamento é criado no Google Calendar **mesmo que** técnico não receba notificação
3. Sistema tenta **múltiplos números** automaticamente (fallback)
4. Todos os erros são **logados detalhadamente**

### **Após validação:**

- [ ] Marcar este deploy como bem-sucedido
- [ ] Documentar qualquer problema encontrado
- [ ] Atualizar variáveis de ambiente se necessário
- [ ] Informar técnico sobre o novo sistema

---

**Status**: 🟡 Deploy em andamento
**Última atualização**: 2025-10-29
**Responsável**: Viniciushann + Claude Code
