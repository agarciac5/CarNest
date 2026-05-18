from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.test import TestCase

from inventario.models import Vehiculo
from inventario.services import aprobar_vehiculo_posteado
from ventas.services import vender_vehiculo


class VehiculoBusinessTests(TestCase):
    def setUp(self):
        User = get_user_model()
        self.propietario = User.objects.create_user(
            username='propietario',
            password='testpass123',
            rol=User.Rol.CLIENTE,
        )
        self.comprador = User.objects.create_user(
            username='comprador',
            password='testpass123',
            rol=User.Rol.CLIENTE,
        )

    def crear_vehiculo(self, estado):
        return Vehiculo.objects.create(
            marca='Toyota',
            modelo='Corolla',
            año=2024,
            precio=100000000,
            propietario=self.propietario,
            estado=estado,
        )

    def test_vehiculo_posteado_puede_pasar_a_en_venta(self):
        vehiculo = self.crear_vehiculo('posteado')

        aprobar_vehiculo_posteado(vehiculo.id)
        vehiculo.refresh_from_db()

        self.assertEqual(vehiculo.estado, 'en_venta')
        self.assertIsNotNone(vehiculo.fecha_compra)

    def test_vehiculo_vendido_no_puede_volver_a_venderse(self):
        vehiculo = self.crear_vehiculo('vendido')

        with self.assertRaises(ValidationError):
            vender_vehiculo(vehiculo, self.comprador)

        vehiculo.refresh_from_db()
        self.assertEqual(vehiculo.estado, 'vendido')
        self.assertEqual(vehiculo.ventas.count(), 0)
