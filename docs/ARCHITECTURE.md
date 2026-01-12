Arquitetura proposta

- MySQL: armazena dados do Zabbix.
- Zabbix Server: responsável por coleta, triggers e alertas.
- Zabbix Web (NGINX + PHP): interface web para administração.
- Zabbix Agent: sincroniza métricas dos hosts (exemplo de configuração no docs).
- Grafana: conecta ao banco de dados ou ao Zabbix via plugin para dashboards.

Fluxo básico

1. Hosts executam Zabbix Agent e/ou SNMP.
2. Zabbix Server coleta dados periodicamente.
3. Triggers disparam alertas (e-mail, webhook, etc).
4. Grafana consome métricas e exibe dashboards.

Considerações de produção

- Não use credenciais padrões em produção.
- Separe redes e permita acesso apenas por VPN/segurança adequada.
- Habilite backups regulares do MySQL.
- Configure monitoramento de logs e retenção de dados.
