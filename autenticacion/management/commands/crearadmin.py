"""
Management command para crear el primer administrador del sistema.

Uso:
    python manage.py crearadmin --email admin@empresa.com --password S3gura!2026
    python manage.py crearadmin   # (modo interactivo, pide los datos)
"""

import getpass

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from autenticacion.models import Propietario, Credencial


class Command(BaseCommand):
    help = "Crea el primer usuario administrador (empresa programadora)."

    def add_arguments(self, parser):
        parser.add_argument("--nombre", type=str, default="Admin")
        parser.add_argument("--apellidos", type=str, default="Rentiva")
        parser.add_argument("--email", type=str)
        parser.add_argument("--password", type=str)

    @transaction.atomic
    def handle(self, *args, **options):
        # ── Verificar si ya existe un admin ──────────────────────
        admins = Propietario.objects.filter(rol=Propietario.Rol.ADMIN)
        if admins.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Ya existen {admins.count()} admin(s): "
                    f"{', '.join(a.email for a in admins)}"
                )
            )
            respuesta = input("¿Crear otro admin de todas formas? [s/N]: ")
            if respuesta.lower() != "s":
                self.stdout.write("Cancelado.")
                return

        # ── Recopilar datos ──────────────────────────────────────
        email = options["email"]
        if not email:
            email = input("Email del admin: ").strip()
        if not email:
            raise CommandError("El email es obligatorio.")

        if Propietario.objects.filter(email=email).exists():
            raise CommandError(f"Ya existe un propietario con email {email}.")

        password = options["password"]
        if not password:
            password = getpass.getpass("Contraseña: ")
            password2 = getpass.getpass("Confirmar contraseña: ")
            if password != password2:
                raise CommandError("Las contraseñas no coinciden.")
        if len(password) < 8:
            raise CommandError("La contraseña debe tener al menos 8 caracteres.")

        nombre = options["nombre"]
        apellidos = options["apellidos"]

        # ── Crear propietario + credencial ────────────────────────
        propietario = Propietario.objects.create(
            nombre=nombre,
            apellidos=apellidos,
            email=email,
            rol=Propietario.Rol.ADMIN,
        )
        credencial = Credencial(propietario=propietario, email=email)
        credencial.set_password(password)
        credencial.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Admin creado exitosamente: {propietario.nombre} "
                f"{propietario.apellidos} ({email})"
            )
        )
