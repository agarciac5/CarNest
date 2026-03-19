from django.db import models
from inventario.models import Vehiculo


class Anuncio(models.Model):
    vehiculo = models.OneToOneField(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name='anuncio'
    )

    descripcion = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"Anuncio de {self.vehiculo}"