from django.contrib import admin
from .models import Vehiculo, FotoVehiculo, Concesionaria


@admin.register(Concesionaria)
class ConcesionariaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'direccion', 'propietario')


class FotoVehiculoInline(admin.TabularInline):
    model = FotoVehiculo
    extra = 1


@admin.register(Vehiculo)
class VehiculoAdmin(admin.ModelAdmin):
    list_display = ('marca', 'modelo', 'año', 'precio', 'estado', 'fecha_publicacion')
    list_filter = ('estado', 'combustible', 'transmision')
    search_fields = ('marca', 'modelo', 'descripcion', 'color')
    inlines = [FotoVehiculoInline]


@admin.register(FotoVehiculo)
class FotoVehiculoAdmin(admin.ModelAdmin):
    list_display = ('vehiculo', 'orden')
