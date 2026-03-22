from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils import timezone


class Concesionaria(models.Model):
    nombre = models.CharField(max_length=100)
    direccion = models.CharField(max_length=255)
    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='concesionarias',
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

    COMBUSTIBLE = [
        ('gasolina', 'Gasolina'),
        ('diesel', 'Diésel'),
        ('hibrido', 'Híbrido'),
        ('electrico', 'Eléctrico'),
        ('glp', 'GLP'),
    ]

    TRANSMISION = [
        ('manual', 'Manual'),
        ('automatica', 'Automática'),
        ('cvt', 'CVT'),
    ]

    marca = models.CharField(max_length=50)
    modelo = models.CharField(max_length=50)
    año = models.IntegerField()
    precio = models.DecimalField(max_digits=12, decimal_places=2)
    kilometraje = models.PositiveIntegerField(default=0)
    color = models.CharField(max_length=40, blank=True, default='')
    combustible = models.CharField(max_length=20, choices=COMBUSTIBLE, default='gasolina')
    transmision = models.CharField(max_length=20, choices=TRANSMISION, default='manual')
    descripcion = models.TextField(blank=True, default='')

    propietario = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='vehiculos'
    )
    concesionaria = models.ForeignKey(
        Concesionaria,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='vehiculos',
    )

    estado = models.CharField(max_length=20, choices=ESTADOS, default='posteado')

    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fecha_compra = models.DateTimeField(null=True, blank=True)
    fecha_venta = models.DateTimeField(null=True, blank=True)

    imagen = models.ImageField(upload_to='vehiculos/', null=True, blank=True)

    def get_absolute_url(self):
        return reverse('detalle_vehiculo', args=[self.pk])

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
        return f"{self.marca} {self.modelo} ({self.año})"

    class Meta:
        ordering = ['-fecha_publicacion']


class FotoVehiculo(models.Model):
    vehiculo = models.ForeignKey(
        Vehiculo,
        on_delete=models.CASCADE,
        related_name='fotos_extra',
    )
    imagen = models.ImageField(upload_to='vehiculos/galeria/')
    orden = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['orden', 'pk']

    def __str__(self):
        return f"Foto {self.pk} — {self.vehiculo}"
