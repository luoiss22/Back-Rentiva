#!/bin/bash
# Deploy manual del backend — córrelo desde tu máquina
# Uso: bash deploy.sh

VPS="root@23.94.202.152"

echo ">>> Desplegando backend en el VPS..."

ssh -t $VPS << 'EOF'
  ERRORS=0

  echo "--- Jalando cambios ---"
  git -C /var/www/rentiva/backend pull origin main || { echo "[WARN] git pull falló, continuando..."; ERRORS=$((ERRORS+1)); }

  cd /var/www/rentiva/backend

  echo "--- Instalando dependencias ---"
  .venv/bin/pip install -r requirements.txt --quiet || { echo "[WARN] pip install falló, continuando..."; ERRORS=$((ERRORS+1)); }

  echo "--- Migraciones ---"
  .venv/bin/python manage.py migrate --noinput --fake-initial || { echo "[WARN] migrate falló, continuando..."; ERRORS=$((ERRORS+1)); }

  echo "--- Archivos estáticos ---"
  .venv/bin/python manage.py collectstatic --noinput || { echo "[WARN] collectstatic falló, continuando..."; ERRORS=$((ERRORS+1)); }

  echo "--- Directorios de media ---"
  mkdir -p media/propiedades/fotos
  mkdir -p media/mobiliario/fotos
  chmod -R 755 media

  echo "--- Reiniciando Gunicorn ---"
  systemctl restart rentiva-backend || { echo "[WARN] restart gunicorn falló, continuando..."; ERRORS=$((ERRORS+1)); }

  echo ""
  if [ $ERRORS -eq 0 ]; then
    echo ">>> Deploy completado sin errores."
  else
    echo ">>> Deploy completado con $ERRORS advertencia(s). Revisa los [WARN] arriba."
  fi

  echo "--- Estado de Gunicorn ---"
  systemctl status rentiva-backend --no-pager

  echo ""
  echo ">>> Cerrando en 500 segundos... (Ctrl+C para salir antes)"
  for i in $(seq 500 -1 1); do
    printf "\r    Tiempo restante: %3d segundos   " $i
    sleep 1
  done
  echo ""
  echo ">>> Tiempo agotado. Cerrando sesión."
EOF

echo ""
echo ">>> Sesión SSH cerrada. Script terminado."
