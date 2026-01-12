Setup local (docker-compose)

Pré-requisitos

- Docker Desktop instalado (Windows) e WSL2 habilitado.
- Git (opcional).

Passos

1. Copie o arquivo de exemplo: `cp .env.example .env` e ajuste senhas.
2. Inicie a stack: `docker-compose up -d`.
3. Aguarde os containers iniciarem (use `docker-compose logs -f` para acompanhar).
4. Acesse Zabbix Web: http://localhost:8080 (usuário: Admin / senha: zabbix).
5. Acesse Grafana: http://localhost:3000 (usuário: admin / senha: admin).

Notas

- No Windows PowerShell, use `Copy-Item .env.example .env` em vez de `cp`.
