from django.db import models
from django.conf import settings


class Concesionaria(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)

    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='concesionarias'
    )

    def __str__(self):
        return self.nombre


class Vehiculo(models.Model):
    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    año = models.IntegerField()
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    disponible = models.BooleanField(default=True)

    concesionaria = models.ForeignKey(
        Concesionaria,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='vehiculos'
    )

    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vehiculos'
    )

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.año})"