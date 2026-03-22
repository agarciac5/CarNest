"""
Asigna precios de ejemplo en pesos colombianos (COP) a los vehículos del catálogo
según marca y modelo. Ejecutar: python manage.py actualizar_precios_cop
"""
from decimal import Decimal

from django.core.management.base import BaseCommand

from inventario.models import Vehiculo

# Valores orientativos de mercado usado en Colombia (COP, sin decimales)
PRECIOS_COP = [
    ('Toyota', 'Corolla', Decimal('108000000')),
    ('Honda', 'Civic', Decimal('118000000')),
    ('Mazda', 'CX-5', Decimal('148000000')),
    ('Volkswagen', 'Jetta', Decimal('92000000')),
    ('Nissan', 'Versa', Decimal('78000000')),
    ('Ford', 'Ranger', Decimal('212000000')),
]


def _en_lista(v):
    for marca, frag, _ in PRECIOS_COP:
        if v.marca.lower() == marca.lower() and frag.lower() in v.modelo.lower():
            return True
    return False


class Command(BaseCommand):
    help = 'Actualiza precios de vehículos conocidos a valores en pesos colombianos (COP).'

    def handle(self, *args, **options):
        total = 0
        for marca, frag, precio in PRECIOS_COP:
            n = Vehiculo.objects.filter(marca__iexact=marca, modelo__icontains=frag).update(precio=precio)
            total += n
            if n:
                self.stdout.write(self.style.SUCCESS(f'{marca} {frag}: {precio} COP ({n} reg.)'))
        if total == 0:
            self.stdout.write(self.style.WARNING('Ningun vehiculo coincidio con la lista.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Total actualizados: {total}'))

        otros = [v for v in Vehiculo.objects.all() if not _en_lista(v)]
        if otros:
            self.stdout.write(
                self.style.WARNING(
                    f'{len(otros)} vehiculo(s) sin regla de precio (no modificados).'
                )
            )
