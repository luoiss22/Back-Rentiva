"""
Management command para crear el primer administrador del sistema.

Uso:
    python manage.py crearadmin --email admin@empresa.com --password S3gura!2026
    python manage.py crearadmin   # (modo interactivo, pide los datos)
"""

import getpass

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from autenticacion.models import Administrador, CredencialAdmin, Propietario


class Command(BaseCommand):
    help = "Crea un usuario administrador del sistema."

    def add_arguments(self, parser):
        parser.add_argument("--nombre", type=str, default="Admin")
        parser.add_argument("--apellidos", type=str, default="Rentiva")
        parser.add_argument("--email", type=str)
        parser.add_argument("--password", type=str)

    @transaction.atomic
    def handle(self, *args, **options):
        # Verificar si ya existe un admin
        admins = Administrador.objects.all()
        if admins.exists():
            self.stdout.write(
                self.style.WARNING(
                    f"Ya existen {admins.count()} admin(s): "
                    f"{', '.join(a.email for a in admins)}"
                )
            )
            respuesta = input("Crear otro admin de todas formas? [s/N]: ")
            if respuesta.lower() != "s":
                self.stdout.write("Cancelado.")
                return

        # Recopilar datos
        email = options["email"]
        if not email:
            email = input("Email del admin: ").strip()
        if not email:
            raise CommandError("El email es obligatorio.")

        if Administrador.objects.filter(email=email).exists():
            raise CommandError(f"Ya existe un admin con email {email}.")
        if Propietario.objects.filter(email=email).exists():
            raise CommandError(f"Ya existe un propietario con email {email}.")

        password = options["password"]
        if not password:
            password = getpass.getpass("Contrasena: ")
            password2 = getpass.getpass("Confirmar contrasena: ")
            if password != password2:
                raise CommandError("Las contrasenas no coinciden.")
        if len(password) < 8:
            raise CommandError("La contrasena debe tener al menos 8 caracteres.")

        nombre = options["nombre"]
        apellidos = options["apellidos"]

        # Crear administrador + credencial
        admin = Administrador.objects.create(
            nombre=nombre,
            apellidos=apellidos,
            email=email,
        )
        cred = CredencialAdmin(administrador=admin, email=email)
        cred.set_password(password)
        cred.save()

        self.stdout.write(
            self.style.SUCCESS(
                f"Admin creado exitosamente: {admin.nombre} "
                f"{admin.apellidos} ({email})"
            )
        )
