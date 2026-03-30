#!/bin/bash
# Deploy manual del backend — córrelo desde tu máquina
# Uso: bash deploy.sh

VPS="root@23.94.202.152"

echo ">>> Desplegando backend en el VPS..."

ssh $VPS << 'EOF'
  ERRORS=0

  echo "--- Jalando cambios ---"
  git -C /var/www/rentiva/backend pull origin main || { echo "[WARN] git pull falló, continuando..."; ERRORS=$((ERRORS+1)); }

  cd /var/www/rentiva/backend

  echo "--- Instalando dependencias ---"
  .venv/bin/pip install -r requirements.txt --quiet || { echo "[WARN] pip install falló, continuando..."; ERRORS=$((ERRORS+1)); }

  echo "--- Migraciones ---"
  .venv/bin/python manage.py migrate --noinput || { echo "[WARN] migrate falló, continuando..."; ERRORS=$((ERRORS+1)); }

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

EOF

echo ""
echo ">>> Sesión SSH cerrada. Script terminado."
