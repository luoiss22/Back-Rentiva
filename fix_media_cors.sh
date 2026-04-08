#!/bin/bash
# fix_media_cors.sh
# Aplica dos correcciones al VPS:
#   1. Agrega headers CORS a /media/ y /static/ en Nginx (puerto 8080)
#   2. Corrige SITE_BASE_URL en el .env para que las URLs de media
#      apunten al puerto 8080 y no al puerto 80
#
# Uso desde tu máquina: bash fix_media_cors.sh

VPS="root@23.94.202.152"

echo ">>> Aplicando fix de CORS para media en el VPS..."

ssh -t $VPS << 'ENDSSH'
set -e

# ── 1. Reescribir la config de Nginx con CORS en /media/ y /static/ ──
cat > /etc/nginx/sites-available/rentiva << 'NGINX'
server {
    listen 8080;
    server_name 23.94.202.152;

    # Frontend (Flutter web)
    location / {
        root /var/www/rentiva/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Admin de Django
    location /admin/ {
        proxy_pass http://127.0.0.1:8001;
        proxy_set_header Host $http_host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Archivos estáticos
    location /static/ {
        alias /var/www/rentiva/backend/staticfiles/;
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, OPTIONS";
        add_header Access-Control-Allow-Headers "Authorization, Content-Type";
    }

    # Archivos de media (fotos de propiedades, inquilinos, mobiliario)
    location /media/ {
        alias /var/www/rentiva/backend/media/;
        add_header Access-Control-Allow-Origin *;
        add_header Access-Control-Allow-Methods "GET, OPTIONS";
        add_header Access-Control-Allow-Headers "Authorization, Content-Type";
    }
}
NGINX

# ── 2. Corregir SITE_BASE_URL en el .env del backend ──────────────
ENV_FILE=/var/www/rentiva/backend/.env

# Eliminar cualquier línea SITE_BASE_URL existente y agregar la correcta
sed -i '/^SITE_BASE_URL/d' "$ENV_FILE"
echo "SITE_BASE_URL=http://23.94.202.152:8080" >> "$ENV_FILE"

echo ">>> .env actualizado:"
grep SITE_BASE_URL "$ENV_FILE"

# ── 3. Validar y recargar Nginx ────────────────────────────────────
nginx -t && systemctl reload nginx
echo ">>> Nginx recargado correctamente."

# ── 4. Reiniciar Gunicorn para que tome el nuevo .env ──────────────
systemctl restart rentiva-backend
echo ">>> Gunicorn reiniciado."

echo ""
echo ">>> Fix aplicado. Las URLs de media ahora apuntan a:"
echo "    http://23.94.202.152:8080/media/"
ENDSSH

echo ""
echo ">>> Script terminado."
