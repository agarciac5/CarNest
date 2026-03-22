from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from PIL import Image

from inventario.models import FotoVehiculo, Vehiculo

User = get_user_model()


def _jpeg(color, size=(960, 640)):
    buf = BytesIO()
    Image.new('RGB', size, color=color).save(buf, format='JPEG', quality=88)
    buf.seek(0)
    return ContentFile(buf.read())


VEHICULOS = [
    {
        'marca': 'Toyota',
        'modelo': 'Corolla XLE',
        'año': 2024,
        'precio': 389500,
        'kilometraje': 18500,
        'color': 'Blanco perla',
        'combustible': 'hibrido',
        'transmision': 'cvt',
        'descripcion': 'Sedán confiable con asientos en piel, pantalla táctil y asistentes de seguridad Toyota Safety Sense. Historial de servicios en agencia.',
        'main': (235, 245, 255),
        'extras': [(220, 230, 240), (200, 210, 220)],
    },
    {
        'marca': 'Honda',
        'modelo': 'Civic Touring',
        'año': 2023,
        'precio': 425000,
        'kilometraje': 24000,
        'color': 'Gris metálico',
        'combustible': 'gasolina',
        'transmision': 'cvt',
        'descripcion': 'Turbo 1.5L, techo solar, sistema de audio premium y cámara multiángulo. Un solo dueño.',
        'main': (90, 100, 110),
        'extras': [(70, 80, 90), (110, 115, 120)],
    },
    {
        'marca': 'Mazda',
        'modelo': 'CX-5 Signature',
        'año': 2022,
        'precio': 498000,
        'kilometraje': 42000,
        'color': 'Rojo soul',
        'combustible': 'gasolina',
        'transmision': 'automatica',
        'descripcion': 'SUV AWD, interior en piel Nappa, head-up display y G-Vectoring Control. Ideal para ciudad y carretera.',
        'main': (140, 40, 50),
        'extras': [(120, 30, 40), (160, 50, 60)],
    },
    {
        'marca': 'Volkswagen',
        'modelo': 'Jetta GLI',
        'año': 2021,
        'precio': 365000,
        'kilometraje': 55000,
        'color': 'Azul noche',
        'combustible': 'gasolina',
        'transmision': 'manual',
        'descripcion': 'Motor 2.0 TSI, suspensión deportiva, diferencial electrónico y sonido Beats. Emoción y practicidad.',
        'main': (30, 50, 90),
        'extras': [(40, 60, 100), (25, 45, 85)],
    },
    {
        'marca': 'Nissan',
        'modelo': 'Versa Advance',
        'año': 2024,
        'precio': 289000,
        'kilometraje': 8000,
        'color': 'Plata brillante',
        'combustible': 'gasolina',
        'transmision': 'cvt',
        'descripcion': 'Económico y espacioso, cámara 360°, alerta de punto ciego y garantía de fábrica vigente.',
        'main': (190, 195, 200),
        'extras': [(175, 180, 185), (200, 205, 210)],
    },
    {
        'marca': 'Ford',
        'modelo': 'Ranger XLT',
        'año': 2023,
        'precio': 615000,
        'kilometraje': 32000,
        'color': 'Negro',
        'combustible': 'diesel',
        'transmision': 'automatica',
        'descripcion': 'Doble cabina 4x4, arrastre asistido, barra antivuelcos y caja reforzada. Lista para trabajo o aventura.',
        'main': (35, 35, 40),
        'extras': [(50, 50, 55), (25, 25, 30)],
    },
]


class Command(BaseCommand):
    help = 'Crea un usuario demo y 6 vehículos de ejemplo con fotos generadas (Pillow).'

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username='carnest_demo',
            defaults={
                'email': 'demo@carnest.local',
                'rol': User.Rol.CLIENTE,
            },
        )
        if created:
            user.set_password('demo12345')
            user.save()
            self.stdout.write(self.style.SUCCESS('Usuario carnest_demo creado (contraseña: demo12345).'))
        else:
            self.stdout.write('Usuario carnest_demo ya existía; se reutiliza.')

        if Vehiculo.objects.filter(propietario=user, marca='Toyota', modelo='Corolla XLE').exists():
            self.stdout.write(self.style.WARNING('Los vehículos de ejemplo ya están cargados. Ejecuta con otra base o borra esos registros.'))
            return

        for item in VEHICULOS:
            data = {**item}
            extras_colors = data.pop('extras')
            main_color = data.pop('main')
            v = Vehiculo.objects.create(
                propietario=user,
                estado='en_venta',
                **data,
            )
            fname = f'seed_{v.pk}_main.jpg'
            v.imagen.save(fname, _jpeg(main_color), save=True)

            for j, rgb in enumerate(extras_colors):
                foto = FotoVehiculo(vehiculo=v, orden=j)
                foto.imagen.save(f'seed_{v.pk}_extra_{j}.jpg', _jpeg(rgb), save=True)

            self.stdout.write(f'  + {v.marca} {v.modelo} ({v.año})')

        self.stdout.write(self.style.SUCCESS('Listo. Abre /inventario/ para ver el catálogo.'))
