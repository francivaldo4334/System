#!/bin/sh

set -e

# Força o uso do binário do ambiente virtual do UV explicitamente
echo "Executando migrações do Django Tenants..."
python manage.py migrate_schemas --shared
python manage.py migrate_schemas --tenant

echo "Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

echo "Compilando mensagens..."
python manage.py compilemessages

# Configura o Cron de Produção para as 5h da manhã (Sintaxe Debian)
echo "Configurando Tarefas Cron..."
echo "0 * * * * cd /app && python manage.py all_tenants_command --command='execute_every_hour' >> /app/cron_notificacoes.log 2>&1" | crontab -

echo "Iniciando daemon do Cron..."
service cron start

# Inicia o servidor de produção (Gunicorn)
echo "Iniciando Gunicorn..."
exec gunicorn core.wsgi:application --bind 0.0.0.0:8000 --workers 3
