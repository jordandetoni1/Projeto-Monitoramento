Projeto: Monitoramento de Equipamentos (base: Zabbix + Grafana)

Descrição

Projeto inicial para monitoramento de equipamentos inspirando-se em Zabbix (coleta, descoberta e alertas) e Grafana (visualização). Objetivo: fornecer um escopo e ambiente mínimo para iniciar desenvolvimento e colaboração.

Componentes

- Zabbix: coleta de métricas, gestão de hosts, alertas.
- Grafana: dashboards e visualizações.
- MySQL: banco de dados para Zabbix.
- Zabbix Agent: para coleta em hosts remotos (exemplo).
- Monitor service: microserviço Python para expor métricas locais e integrações.

Conteúdo deste repositório

- docker-compose.yml — stack mínima para testes locais.
- .env.example — variáveis sensíveis a configurar.
- docs/ — documentação: arquitetura, setup e contribuição.

Quickstart (teste local)

1. Copie e ajuste variáveis: renomeie `.env.example` para `.env` e preencha senhas.
2. Execute: docker-compose up -d
3. Acesse:
   - Zabbix frontend: http://localhost:8080 (usuário: Admin / senha: zabbix) — substituir após primeiro login.
   - Grafana: http://localhost:3000 (usuário: admin / senha: admin)
   - Monitor service: http://localhost:5000/health

Observações

- Este é um escopo inicial para compartilhar com colaboradores. Ajustes, segurança, volumes e backups devem ser tratados antes de produzir um ambiente de produção.

Links úteis

- docs/ARCHITECTURE.md
- docs/SETUP.md
- docs/CONTRIBUTING.md

Repositorio remoto

URL: https://github.com/jordandetoni1/Projeto-Monitoramento

Comandos para enviar (PowerShell):

- git init
- git add .
- git commit -m "Initial commit: scaffold monitoring (Zabbix + Grafana + monitor service + CI)"
- git branch -M main
- git remote add origin https://github.com/jordandetoni1/Projeto-Monitoramento.git
- git push -u origin main

Se usar HTTPS e pedir senha, gere um Personal Access Token (PAT) e use-o como senha.


