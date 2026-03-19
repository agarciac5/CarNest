from django.db import models
from django.conf import settings
from django.utils import timezone
from inventario.models import Vehiculo


class Venta(models.Model):
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name='ventas'
    )

    comprador = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='compras'
    )

    fecha = models.DateTimeField(auto_now_add=True)
    precio_final = models.DecimalField(max_digits=12, decimal_places=2)

    def realizar_venta(self):
        if self.vehiculo.estado == 'en_venta':
            self.vehiculo.estado = 'vendido'
            self.vehiculo.fecha_venta = timezone.now()
            self.vehiculo.save()
            self.save()

    def clean(self):
        #evitar vender dos veces
        if self.vehiculo.estado == 'vendido':
            raise ValueError("Este vehículo ya fue vendido.")


    def __str__(self):
        return f"Venta de {self.vehiculo} a {self.comprador}"