from django.contrib.auth.models import AbstractUser
from django.db import models

class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        CLIENTE = "cliente", "Cliente"
        PROPIETARIO = "propietario", "Propietario"

    rol = models.CharField(max_length=20, choices=Rol.choices)
    telefono = models.CharField(max_length=15, blank=True)