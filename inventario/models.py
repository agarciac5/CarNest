from django.db import models
from django.conf import settings
from django.utils import timezone




class Vehiculo(models.Model):
    ESTADOS = [
    ('posteado', 'Posteado por usuario'),
    ('en_venta', 'Publicado en inventario'),
    ('vendido', 'Vendido'),
]

    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    año = models.IntegerField()
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    
   
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

    def comprar_por_admin(self, concesionaria=None):
        if self.estado == 'posteado':
            self.estado = 'en_venta'
            self.fecha_compra = timezone.now()

            if concesionaria:
                self.concesionaria = concesionaria

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