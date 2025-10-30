# 🚀 COMANDOS DE DEPLOY PARA SERVIDOR HETZNER
# Execute estes comandos no servidor de produção via SSH

# 1. SSH no servidor
ssh root@46.62.155.254

# 2. Navegar para o projeto
cd /root/Langcham-fluxo-atendimento

# 3. Atualizar código
git pull origin main

# 4. Verificar se as correções estão aplicadas
grep -n "contexto_cliente_atual" src/nodes/agent.py
grep -n "cliente_nome: str = \"Cliente\", telefone_cliente: str = \"\"" src/nodes/agent.py

# 5. Rebuild da imagem
docker build -t whatsapp-bot-langchain:latest . --no-cache

# 6. Update do serviço (zero downtime)
docker service update --force whatsapp-bot_whatsapp-bot

# 7. Verificar status
docker service ps whatsapp-bot_whatsapp-bot

# 8. Verificar logs em tempo real
docker service logs whatsapp-bot_whatsapp-bot --follow

# 9. Testar health check
curl https://bot.automacaovn.shop/health

# 10. Testar endpoint de documentação
curl https://bot.automacaovn.shop/docs