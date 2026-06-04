#!/bin/sh

set -e

# Força o uso do binário do ambiente virtual do UV explicitamente
echo "Executando migrações do Django Tenants..."
/app/.venv/bin/python manage.py migrate_schemas --shared
/app/.venv/bin/python manage.py migrate_schemas --tenant

# Configura o Cron de Produção para as 5h da manhã (Sintaxe Debian)
echo "Configurando Tarefas Cron..."
echo "0 5 * * * cd /app && /app/.venv/bin/python manage.py all_tenants_command --command='trigger_reminders' >> /app/cron_notificacoes.log 2>&1" | crontab -

echo "Iniciando daemon do Cron..."
service cron start

# Inicia o servidor de produção (Gunicorn)
echo "Iniciando Gunicorn..."
exec /app/.venv/bin/gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3
