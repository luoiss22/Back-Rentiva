#!/bin/bash
# Deploy manual del backend — córrelo desde tu máquina
# Uso: bash deploy.sh

VPS="root@23.94.202.152"

echo ">>> Desplegando backend en el VPS..."

ssh $VPS << 'EOF'
  set -e
  cd /var/www/rentiva/backend

  echo "--- Jalando cambios ---"
  git pull origin main

  echo "--- Instalando dependencias ---"
  .venv/bin/pip install -r requirements.txt --quiet

  echo "--- Migraciones ---"
  .venv/bin/python manage.py migrate --noinput

  echo "--- Archivos estáticos ---"
  .venv/bin/python manage.py collectstatic --noinput

  echo "--- Directorios de media ---"
  mkdir -p media/propiedades/fotos
  mkdir -p media/mobiliario/fotos
  chmod -R 755 media

  echo "--- Reiniciando Gunicorn ---"
  systemctl restart rentiva-backend

  echo "--- Listo ---"
EOF

echo ">>> Backend desplegado en http://23.94.202.152:8080"
