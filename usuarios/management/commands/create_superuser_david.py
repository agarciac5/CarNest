import os

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea o actualiza el superusuario david. Solo para desarrollo."

    def handle(self, *args, **options):
        User = get_user_model()
        u, created = User.objects.get_or_create(
            username="david",
            defaults={
                "email": "david@carnest.local",
                "rol": User.Rol.ADMIN,
                "is_staff": True,
                "is_superuser": True,
            },
        )
        u.email = u.email or "david@carnest.local"
        u.rol = User.Rol.ADMIN
        u.is_staff = True
        u.is_superuser = True
        password = os.environ.get("DAVID_SUPERUSER_PASSWORD")
        if password:
            u.set_password(password)
        else:
            u.set_unusable_password()
        u.save()
        self.stdout.write(
            self.style.SUCCESS(
                f"Superusuario {'creado' if created else 'actualizado'}: david"
            )
        )
