from django.db import models
from django.conf import settings
from django.utils import timezone

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
    ESTADOS = [
    ('posteado', 'Posteado por usuario'),
    ('comprado', 'Comprado por la concesionaria'),
    ('en_venta', 'Publicado en inventario'),
    ('vendido', 'Vendido'),
]

    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    año = models.IntegerField()
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    
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

    

    estado = models.CharField(max_length=20, choices=ESTADOS, default='posteado')

    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fecha_compra = models.DateTimeField(null=True, blank=True)
    fecha_venta = models.DateTimeField(null=True, blank=True)

    imagen = models.ImageField(upload_to='vehiculos/', null=True, blank=True)

    def comprar_por_concesionaria(self, concesionaria=None):
        if self.estado == 'posteado':
            self.estado = 'comprado'
            self.fecha_compra = timezone.now()

            if concesionaria:
                self.concesionaria = concesionaria

            self.save()

    def publicar_en_inventario(self):
        if self.estado == 'comprado':
            self.estado = 'en_venta'
            self.save()

    def vender(self):
        if self.estado == 'en_venta':
            self.estado = 'vendido'
            self.fecha_venta = timezone.now()
            self.save()

    def __str__(self):
        return f"{self.marca} {self.modelo} ({self.anio})"

    class Meta:
        ordering = ['-fecha_publicacion']