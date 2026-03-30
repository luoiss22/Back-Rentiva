#!/bin/bash
# =============================================================
# setup_vps.sh — Configuración inicial del VPS para Rentiva
# Corre esto UNA sola vez como root o con sudo en tu VPS.
# =============================================================
set -e

echo "=== Actualizando sistema ==="
apt update && apt upgrade -y
apt install -y python3 python3-pip python3-venv nginx git curl postgresql postgresql-contrib

# ── Configurar PostgreSQL ──────────────────────────────────────
echo "=== Configurando PostgreSQL ==="
sudo -u postgres psql -c "CREATE DATABASE rentiva_db;"
sudo -u postgres psql -c "CREATE USER admin WITH PASSWORD 'root';"
sudo -u postgres psql -c "ALTER ROLE admin SET client_encoding TO 'utf8';"
sudo -u postgres psql -c "ALTER ROLE admin SET default_transaction_isolation TO 'read committed';"
sudo -u postgres psql -c "ALTER ROLE admin SET timezone TO 'America/Mexico_City';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE rentiva_db TO admin;"
sudo -u postgres psql -c "ALTER DATABASE rentiva_db OWNER TO admin;"

# ── Directorios ──────────────────────────────────────────────
mkdir -p /var/www/rentiva/backend
mkdir -p /var/www/rentiva/frontend

# ── Clonar repos ─────────────────────────────────────────────
# Cambia las URLs por las de tus repos
echo "=== Clonando backend ==="
git clone https://github.com/luoiss22/Back-Rentiva.git /var/www/rentiva/backend

echo "=== Configurando entorno Python ==="
cd /var/www/rentiva/backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# ── Archivo .env ─────────────────────────────────────────────
# Crea el .env con tus valores reales ANTES de continuar
cat > /var/www/rentiva/backend/.env << 'EOF'
SECRET_KEY=django-insecure-tu_llave_secreta_aqui_cambiala
DEBUG=False
ALLOWED_HOSTS=23.94.202.152,localhost,127.0.0.1
CORS_ALLOWED_ORIGINS=http://23.94.202.152
DATABASE_URL=postgres://admin:root@127.0.0.1:5432/rentiva_db
EOF

echo ">>> Archivo .env generado. Puedes editarlo luego en /var/www/rentiva/backend/.env"

source .venv/bin/activate
python manage.py migrate --noinput
python manage.py collectstatic --noinput

# ── Crear usuario para el servicio (sin shell, más seguro) ────
id -u rentiva &>/dev/null || useradd --no-create-home --shell /bin/false rentiva
chown -R rentiva:rentiva /var/www/rentiva

# ── Systemd service para Gunicorn ─────────────────────────────
cat > /etc/systemd/system/rentiva-backend.service << 'EOF'
[Unit]
Description=Rentiva Backend (Gunicorn)
After=network.target

[Service]
User=rentiva
Group=rentiva
WorkingDirectory=/var/www/rentiva/backend
EnvironmentFile=/var/www/rentiva/backend/.env
ExecStart=/var/www/rentiva/backend/.venv/bin/gunicorn \
    --workers 3 \
    --bind 127.0.0.1:8000 \
    --access-logfile /var/log/rentiva-access.log \
    --error-logfile /var/log/rentiva-error.log \
    rentiva_backend.wsgi:application
Restart=always

[Install]
WantedBy=multi-user.target
EOF

# Permite al usuario deployer reiniciar el servicio sin password
echo "rentiva ALL=(ALL) NOPASSWD: /bin/systemctl restart rentiva-backend" >> /etc/sudoers.d/rentiva

systemctl daemon-reload
systemctl enable rentiva-backend
systemctl start rentiva-backend

# ── Nginx ─────────────────────────────────────────────────────
cat > /etc/nginx/sites-available/rentiva << 'EOF'
server {
    listen 80;
    server_name 23.94.202.152;

    # Frontend (Flutter web)
    location / {
        root /var/www/rentiva/frontend;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Admin de Django
    location /admin/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    # Static y media files de Django
    location /static/ {
        alias /var/www/rentiva/backend/staticfiles/;
    }
    location /media/ {
        alias /var/www/rentiva/backend/media/;
    }
}
EOF

ln -sf /etc/nginx/sites-available/rentiva /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

echo ""
echo "=== Setup completo ==="
echo "Backend corriendo en http://127.0.0.1:8000"
echo "Nginx sirviendo en http://23.94.202.152"
echo ""
echo "Recuerda que tu VPS ya está configurado"
