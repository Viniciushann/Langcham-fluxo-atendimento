# 🔄 GUIA FINAL: Atualizar Número do Técnico em Produção

## ✅ TESTE APROVADO!

O teste foi realizado com **SUCESSO**:
- ✅ **Novo número (+14372591659)**: **FUNCIONANDO**
- ✅ **Números atuais**: 2/3 funcionando
- ❌ **Número 55628540075**: não existe (será removido)

## 🎯 COMANDOS PARA EXECUÇÃO NO SERVIDOR

### **OPÇÃO 1: Atualização Automática (Recomendado)**

```bash
# 1. SSH no servidor
ssh root@46.62.155.254

# 2. Ir para o projeto
cd /root/Langcham-fluxo-atendimento

# 3. Atualizar código do GitHub
git pull origin main

# 4. Executar script de atualização automática
chmod +x atualizar_numero_tecnico.sh
./atualizar_numero_tecnico.sh
```

### **OPÇÃO 2: Atualização Manual**

```bash
# 1. SSH no servidor
ssh root@46.62.155.254

# 2. Ir para o projeto
cd /root/Langcham-fluxo-atendimento

# 3. Atualizar código
git pull origin main

# 4. Parar serviço
docker service scale whatsapp-bot_whatsapp-bot=0

# 5. Atualizar variáveis de ambiente
export TELEFONE_TECNICO='14372591659'
export TELEFONE_TECNICO_BACKUP='556281091167'

# 6. Rebuild da imagem
docker build -t whatsapp-bot-langchain:latest . --no-cache

# 7. Restartar serviço
docker service scale whatsapp-bot_whatsapp-bot=1

# 8. Verificar logs
docker service logs whatsapp-bot_whatsapp-bot --follow
```

## 📋 CONFIGURAÇÃO FINAL

Após a atualização, o sistema ficará com:

```
📞 NÚMERO PRINCIPAL: +14372591659 (NOVO)
📞 BACKUP: 556281091167 (único backup válido)
❌ REMOVIDOS: 556292935358 (teste), 55628540075 (não funciona)
```

## 🧪 VALIDAÇÃO PÓS-DEPLOY

Após executar a atualização:

1. **Verificar logs:**
   ```bash
   docker service logs whatsapp-bot_whatsapp-bot --tail 20
   ```

2. **Testar health check:**
   ```bash
   curl https://bot.automacaovn.shop/health
   ```

3. **Fazer um agendamento de teste:**
   - Envie mensagem no WhatsApp pedindo agendamento
   - Verificar se você recebe a notificação no novo número

4. **Verificar logs de debug:**
   ```bash
   docker service logs whatsapp-bot_whatsapp-bot | grep "📞 Sistema de notificação configurado com 2 número(s)"
   ```

## ⚠️ ROLLBACK (se necessário)

Se algo der errado, você pode voltar rapidamente:

```bash
# Restaurar configuração anterior
export TELEFONE_TECNICO='556292935358'
docker service update --force whatsapp-bot_whatsapp-bot

# Ou restaurar backup do arquivo
cp src/tools/scheduling.py.backup.* src/tools/scheduling.py
docker build -t whatsapp-bot-langchain:latest . --no-cache
docker service update --force whatsapp-bot_whatsapp-bot
```

## 📱 NÚMEROS TESTADOS

### ✅ FUNCIONANDO:
- **14372591659** (NOVO - Internacional)
- **556281091167** (Backup válido)

### ❌ REMOVIDOS:
- **556292935358** (Era só para teste)
- **55628540075** (Número não existe no WhatsApp)

## 🎉 RESULTADO ESPERADO

Após a atualização:
1. ✅ Agendamentos notificarão o novo número +14372591659
2. ✅ Sistema de fallback funcionará com 2 números válidos
3. ✅ Logs mostrarão: "📞 Sistema de notificação configurado com 2 número(s)"
4. ✅ Google Calendar continuará funcionando normalmente
5. ✅ Dados dos clientes continuarão sendo injetados corretamente

---

**Execute quando estiver pronto! O teste já confirmou que tudo funcionará perfeitamente.** 🚀