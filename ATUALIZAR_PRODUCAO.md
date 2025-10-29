# 🚀 GUIA DE ATUALIZAÇÃO - CORREÇÃO DO TELEFONE DO TÉCNICO

## 📋 Informações do Ambiente

- **Ambiente**: Produção
- **Plataforma**: Docker Swarm
- **Gerenciamento**: Portainer
- **Serviço**: `whatsapp-bot`
- **Última atualização**: 2025-10-27 14:16:5 by admin8

---

## ⚠️ IMPORTANTE - LEIA ANTES DE ATUALIZAR

Esta atualização corrige um bug crítico no sistema de notificações:
- ❌ **Número incorreto**: `556298540075` (13 dígitos)
- ✅ **Número correto**: `55628540075` (12 dígitos)

O técnico possui um número **antigo (pré-2016)** SEM o 9º dígito adicional.

---

## 🔄 PASSOS PARA ATUALIZAÇÃO

### **1. BACKUP DO CÓDIGO ATUAL (SEGURANÇA)**

```bash
# Conectar ao servidor de produção via SSH
ssh usuario@servidor-producao

# Fazer backup do arquivo atual
cd "/caminho/para/Langcham. fluxo atendimento"
cp src/tools/scheduling.py src/tools/scheduling.py.backup-$(date +%Y%m%d-%H%M%S)

# Verificar backup
ls -lh src/tools/scheduling.py*
```

---

### **2. ATUALIZAR CÓDIGO NO SERVIDOR**

#### **Opção A: Via Git (RECOMENDADO)**

```bash
# No servidor de produção
cd "/caminho/para/Langcham. fluxo atendimento"

# Fazer commit das mudanças (se ainda não foi feito)
git add src/tools/scheduling.py
git add .env.example
git add tests/test_telefone_tecnico.py

git commit -m "Fix: Corrigir número do técnico e melhorar sistema de notificação

- Corrigir TELEFONE_TECNICO: 556298540075 → 55628540075
- Implementar sistema de fallback com múltiplos técnicos
- Melhorar logging e tratamento de erros
- Adicionar teste de validação de números
- Nunca bloquear agendamento se notificação falhar"

# Push para repositório
git push origin main

# Pull no servidor de produção
git pull origin main
```

#### **Opção B: Upload Manual (se não usar Git)**

1. Acesse o servidor via FTP/SFTP
2. Faça upload dos arquivos modificados:
   - `src/tools/scheduling.py`
   - `.env.example`
   - `tests/test_telefone_tecnico.py`

---

### **3. ATUALIZAR VARIÁVEIS DE AMBIENTE**

#### **Via Portainer (Interface Web)**

1. Acesse o Portainer: `https://seu-portainer.com`
2. Navegue: **Stacks** → **whatsapp-bot**
3. Clique em **Editor** ou **Environment Variables**
4. Adicione/Atualize as seguintes variáveis:

```bash
# Número principal do técnico (OBRIGATÓRIO)
# Número antigo (pré-2016) - 12 dígitos SEM o 9º dígito
TELEFONE_TECNICO=55628540075

# Número backup (OPCIONAL)
# Número novo (pós-2016) - 13 dígitos COM o 9º dígito
TELEFONE_TECNICO_BACKUP=556281091167

# ID do Google Calendar (se ainda não existir)
GOOGLE_CALENDAR_ID=centrooestedrywalldry@gmail.com
```

5. Clique em **Update the stack**

#### **Via Arquivo .env (Alternativa)**

```bash
# No servidor de produção
cd "/caminho/para/Langcham. fluxo atendimento"

# Editar arquivo .env
nano .env

# Adicionar/atualizar as linhas:
# TELEFONE_TECNICO=55628540075
# TELEFONE_TECNICO_BACKUP=556281091167
# GOOGLE_CALENDAR_ID=centrooestedrywalldry@gmail.com

# Salvar: Ctrl+O, Enter, Ctrl+X
```

---

### **4. RECONSTRUIR E REINICIAR O SERVIÇO**

#### **Via Portainer (RECOMENDADO)**

1. Acesse: **Stacks** → **whatsapp-bot**
2. Clique em **Update the stack**
3. Marque: ☑️ **Re-pull image and redeploy**
4. Clique em **Update**

**OU**

1. Acesse: **Services** → **whatsapp-bot**
2. Clique em **Update the service**
3. Marque: ☑️ **Pull latest image**
4. Clique em **Update service**

#### **Via Docker CLI (Alternativa)**

```bash
# No servidor de produção
cd "/caminho/para/Langcham. fluxo atendimento"

# Reconstruir imagem
docker build -t whatsapp-bot:latest .

# Atualizar serviço no Swarm
docker service update --image whatsapp-bot:latest whatsapp-bot

# OU reiniciar stack completa
docker stack deploy -c docker-compose.yml whatsapp-bot
```

---

### **5. VERIFICAR ATUALIZAÇÃO**

#### **5.1. Verificar Logs do Serviço**

```bash
# Via Docker CLI
docker service logs -f whatsapp-bot --tail 100

# Procurar por:
# ✅ "📞 Sistema de notificação configurado com 2 número(s)"
# ✅ "Service Account carregada com sucesso"
```

#### **Via Portainer**
1. **Services** → **whatsapp-bot** → **Logs**
2. Procurar mensagem: `📞 Sistema de notificação configurado com 2 número(s)`

#### **5.2. Executar Teste de Validação**

```bash
# No servidor de produção
cd "/caminho/para/Langcham. fluxo atendimento"

# Executar teste
python tests/test_telefone_tecnico.py

# Resultado esperado:
# ✅ Principal 55628540075    ✅ ATIVO
# ✅ Backup    556281091167   ✅ ATIVO (ou ❌ INATIVO se não tiver WhatsApp)
```

#### **5.3. Teste Real de Agendamento**

```bash
# Fazer um agendamento de teste via WhatsApp
# Verificar se:
# 1. ✅ Agendamento criado no Google Calendar
# 2. ✅ Notificação enviada ao técnico (55628540075)
# 3. ✅ Mensagem recebida no WhatsApp do técnico
```

---

### **6. MONITORAMENTO PÓS-ATUALIZAÇÃO**

```bash
# Monitorar logs em tempo real (15 minutos)
docker service logs -f whatsapp-bot | grep -i "técnico\|notifica\|agendamento"

# Verificar status do serviço
docker service ls | grep whatsapp-bot
# Deve mostrar: REPLICAS = 1/1 (running)

# Verificar saúde do container
docker service ps whatsapp-bot
# Status deve ser: Running
```

---

## 📊 CHECKLIST DE VALIDAÇÃO

Marque conforme avança:

- [ ] Backup do código atual criado
- [ ] Código atualizado no servidor (Git pull ou upload manual)
- [ ] Variáveis de ambiente configuradas:
  - [ ] `TELEFONE_TECNICO=55628540075`
  - [ ] `TELEFONE_TECNICO_BACKUP=556281091167`
  - [ ] `GOOGLE_CALENDAR_ID=centrooestedrywalldry@gmail.com`
- [ ] Serviço reconstruído e reiniciado
- [ ] Log mostra: "Sistema de notificação configurado com 2 número(s)"
- [ ] Teste de validação executado com sucesso
- [ ] Teste real de agendamento realizado
- [ ] Notificação recebida pelo técnico
- [ ] Sistema monitorado por 15 minutos sem erros

---

## 🆘 TROUBLESHOOTING

### **Problema 1: Serviço não inicia após atualização**

```bash
# Verificar logs de erro
docker service logs whatsapp-bot --tail 50

# Verificar se variáveis estão corretas
docker service inspect whatsapp-bot --format='{{json .Spec.TaskTemplate.ContainerSpec.Env}}' | jq

# Rollback se necessário
docker service rollback whatsapp-bot
```

### **Problema 2: Notificação ainda não funciona**

```bash
# Verificar número configurado
docker exec $(docker ps -q -f name=whatsapp-bot) env | grep TELEFONE_TECNICO

# Testar conexão com Evolution API
curl -X POST "https://evolution.centrooestedrywalldry.com.br/message/sendText/Centro_oeste_draywal" \
  -H "apikey: SUA_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"number":"55628540075","text":"Teste manual"}'

# Verificar se número tem WhatsApp
python tests/test_telefone_tecnico.py
```

### **Problema 3: Variáveis de ambiente não aplicadas**

```bash
# Forçar recriação do serviço
docker service update --force whatsapp-bot

# Verificar se .env está sendo lido
docker service inspect whatsapp-bot | grep -i env
```

---

## 🔙 ROLLBACK (Se Necessário)

```bash
# Restaurar código anterior
cp src/tools/scheduling.py.backup-YYYYMMDD-HHMMSS src/tools/scheduling.py

# Reverter commit
git revert HEAD
git push origin main

# Atualizar serviço
docker service update --force whatsapp-bot

# Verificar logs
docker service logs -f whatsapp-bot
```

---

## 📞 CONTATOS DE SUPORTE

- **Admin**: admin8
- **Última atualização**: 2025-10-27 14:16:5
- **Portainer**: [URL do Portainer]
- **Evolution API**: https://evolution.centrooestedrywalldry.com.br

---

## 📚 REFERÊNCIAS

- Evolution API Docs: https://doc.evolution-api.com
- Google Calendar API: https://developers.google.com/calendar
- Docker Swarm: https://docs.docker.com/engine/swarm/

---

## ✅ RESULTADO ESPERADO

Após a atualização bem-sucedida:

1. ✅ Número do técnico corrigido: `55628540075`
2. ✅ Sistema de fallback funcionando
3. ✅ Notificações chegando ao WhatsApp do técnico
4. ✅ Agendamentos nunca bloqueados
5. ✅ Logs detalhados e informativos
6. ✅ Zero downtime durante atualização

---

**Data deste guia**: 2025-10-29
**Versão**: 1.0
**Prioridade**: 🔴 ALTA (Bug crítico)
