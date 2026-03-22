"""
Asigna archivos de media/vehiculos/ a cada Vehiculo del catálogo según marca/modelo
y elimina registros de galería (FotoVehiculo). Ejecutar tras colocar las imágenes con
nombres conocidos en media/vehiculos/.
"""
from pathlib import Path

from django.conf import settings
from django.core.files import File
from django.core.management.base import BaseCommand

from inventario.models import FotoVehiculo, Vehiculo

# (marca exacta, fragmento del modelo, nombre de archivo en media/vehiculos/)
ASIGNACIONES = [
    ('Toyota', 'Corolla', 'toyota-corolla-xle.avif'),
    ('Honda', 'Civic', 'honda-civic-touring.webp'),
    ('Mazda', 'CX-5', 'mazda-cx5-signature.jpg'),
    ('Nissan', 'Versa', 'nissan-versa-advance.webp'),
    ('Volkswagen', 'Jetta', 'Volskwagen-jetta-gli.webp'),
    ('Ford', 'Ranger', 'ford-ranger.avif'),
]


def _resolver_ruta(nombre_buscado: str, carpeta: Path) -> Path | None:
    """Encuentra el archivo aunque cambie mayúsculas (Windows)."""
    b = nombre_buscado.lower()
    for p in carpeta.iterdir():
        if p.is_file() and p.name.lower() == b:
            return p
    return None


class Command(BaseCommand):
    help = 'Enlaza imágenes locales de media/vehiculos/ con vehículos por marca/modelo.'

    def handle(self, *args, **options):
        carpeta = Path(settings.MEDIA_ROOT) / 'vehiculos'
        if not carpeta.is_dir():
            self.stdout.write(self.style.ERROR(f'No existe la carpeta {carpeta}'))
            return

        for marca, frag_modelo, archivo in ASIGNACIONES:
            v = Vehiculo.objects.filter(marca__iexact=marca, modelo__icontains=frag_modelo).first()
            if not v:
                self.stdout.write(self.style.WARNING(f'Sin vehículo: {marca} {frag_modelo}'))
                continue

            ruta = _resolver_ruta(archivo, carpeta)
            if not ruta:
                self.stdout.write(self.style.WARNING(f'Archivo no encontrado: {archivo}'))
                continue

            n_extra = FotoVehiculo.objects.filter(vehiculo=v).count()
            FotoVehiculo.objects.filter(vehiculo=v).delete()

            with open(ruta, 'rb') as f:
                v.imagen.save(ruta.name, File(f), save=True)

            self.stdout.write(
                self.style.SUCCESS(
                    f'OK {v.marca} {v.modelo} -> {ruta.name} (fotos extra borradas: {n_extra})'
                )
            )
