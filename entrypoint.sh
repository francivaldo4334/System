#!/bin/sh

# 1. Executa as migrações do Django Tenants (Public e Tenants)
python manage.py migrate_schemas --shared
python manage.py migrate_schemas --tenant

# 3. Configura o Cron de Produção para as 5h da manhã
echo "Configurando Tarefas Cron..."
echo "0 5 * * * /app/.venv/bin/python /app/manage.py all_tenants_command --command='trigger_reminders' >> /app/cron_notificacoes.log 2>&1" > /etc/crontabs/root

# 4. Inicia o daemon do Cron em background
crond -b -l 2

# 5. Inicia o servidor de produção (Gunicorn)
echo "Iniciando Gunicorn..."
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3
