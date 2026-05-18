"""
core/tests.py
-------------
Tests unitarios para los 4 puntos implementados.

Punto 3 - Inversión de dependencias:
    - Ambas clases concretas cumplen ITipoCambioService.
    - TipoCambioConFallback usa la clase fija cuando la API falla.
    - Las vistas usan dependencias inyectadas (mock).

Punto 5 - Internacionalización:
    - URLs responden con prefijo de idioma correcto.
    - Middleware activa el idioma de sesión.

Punto 6 - API JSON propia:
    - Endpoints devuelven JSON válido con estructura esperada.

Punto 8 - API externa:
    - TipoCambioService maneja errores de red sin romper la app.
    - TipoCambioFijoService siempre retorna un valor.
    - TipoCambioConFallback usa el fijo cuando la API falla.
"""
from unittest.mock import patch, MagicMock

from django.test import TestCase, Client
from django.contrib.auth import get_user_model

from core.protocols import IVehiculoRepository, IVentaService, ITipoCambioService
from core.dependencies import _VehiculoRepo, _VentaService, get_vehiculo_repo
from core.services import TipoCambioService, TipoCambioFijoService, TipoCambioConFallback

Usuario = get_user_model()


# ═══════════════════════════════════════════════════════════════════
# Punto 3 — Inversión de dependencias
# ═══════════════════════════════════════════════════════════════════

class ProtocolosTests(TestCase):
    """Las implementaciones concretas deben satisfacer ITipoCambioService."""

    def test_vehiculo_repo_cumple_protocolo(self):
        self.assertIsInstance(_VehiculoRepo(), IVehiculoRepository)

    def test_venta_service_cumple_protocolo(self):
        self.assertIsInstance(_VentaService(), IVentaService)

    def test_tipo_cambio_vivo_cumple_protocolo(self):
        """Clase concreta 1: TipoCambioService cumple ITipoCambioService."""
        self.assertIsInstance(TipoCambioService(), ITipoCambioService)

    def test_tipo_cambio_fijo_cumple_protocolo(self):
        """Clase concreta 2: TipoCambioFijoService cumple ITipoCambioService."""
        self.assertIsInstance(TipoCambioFijoService(), ITipoCambioService)

    def test_tipo_cambio_fallback_cumple_protocolo(self):
        """TipoCambioConFallback también cumple ITipoCambioService."""
        self.assertIsInstance(TipoCambioConFallback(), ITipoCambioService)


class InyeccionDependenciasTests(TestCase):
    """Las vistas usan get_vehiculo_repo() — se puede reemplazar en tests."""

    def setUp(self):
        import core.dependencies as deps
        self._original = deps._vehiculo_repo

    def tearDown(self):
        import core.dependencies as deps
        deps._vehiculo_repo = self._original

    def test_reemplazo_repo_en_vista(self):
        import core.dependencies as deps
        mock_repo = MagicMock()
        mock_repo.listar_en_venta.return_value = []
        deps._vehiculo_repo = mock_repo

        client = Client()
        response = client.get('/inventario/')

        mock_repo.listar_en_venta.assert_called_once()
        self.assertEqual(response.status_code, 200)


class FallbackTipoCambioTests(TestCase):
    """TipoCambioConFallback usa la clase fija cuando la API falla."""

    def test_fallback_cuando_api_falla(self):
        """Si TipoCambioService retorna None, debe usar TipoCambioFijoService."""
        import urllib.error
        servicio_vivo = TipoCambioService()
        servicio_fijo = TipoCambioFijoService(tasa_cop=4200.0)
        fallback = TipoCambioConFallback(servicio_vivo, servicio_fijo)

        with patch('urllib.request.urlopen', side_effect=urllib.error.URLError('sin red')):
            resultado = fallback.cop_a_usd(4_200_000)

        # Debe retornar valor de la tasa fija (4200 COP = 1 USD → 4.2M = 1000 USD)
        self.assertIsNotNone(resultado)
        self.assertAlmostEqual(resultado, 1000.0, places=1)

    def test_fallback_usa_api_cuando_disponible(self):
        """Si la API responde, usa ese valor y no el fijo."""
        import json
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({'rates': {'COP': 4000.0}}).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        servicio_fijo = TipoCambioFijoService(tasa_cop=9999.0)  # valor absurdo
        servicio_vivo = TipoCambioService()
        fallback = TipoCambioConFallback(servicio_vivo, servicio_fijo)

        with patch('urllib.request.urlopen', return_value=mock_resp):
            tasa = fallback.obtener_tasa_usd_cop()

        # Debe usar la API (4000), no la fija (9999)
        self.assertAlmostEqual(tasa, 4000.0, places=1)


# ═══════════════════════════════════════════════════════════════════
# Punto 5 — Internacionalización
# ═══════════════════════════════════════════════════════════════════

class I18nURLTests(TestCase):

    def test_home_español_sin_prefijo(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_home_ingles_con_prefijo(self):
        response = self.client.get('/en/')
        self.assertEqual(response.status_code, 200)

    def test_inventario_español(self):
        response = self.client.get('/inventario/')
        self.assertEqual(response.status_code, 200)

    def test_inventario_ingles(self):
        response = self.client.get('/en/inventario/')
        self.assertEqual(response.status_code, 200)

    def test_url_con_prefijo_es_da_404(self):
        """/es/ no existe porque prefix_default_language=False."""
        response = self.client.get('/es/')
        self.assertEqual(response.status_code, 404)


class MiddlewareIdiomaTests(TestCase):

    def test_cambio_a_ingles_redirige(self):
        response = self.client.post(
            '/inventario/',
            {'_set_idioma': '1', 'idioma': 'en'},
            HTTP_REFERER='http://testserver/inventario/',
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/en/', response['Location'])

    def test_cambio_a_español_redirige_sin_prefijo(self):
        response = self.client.post(
            '/en/inventario/',
            {'_set_idioma': '1', 'idioma': 'es'},
            HTTP_REFERER='http://testserver/en/inventario/',
        )
        self.assertEqual(response.status_code, 302)
        self.assertNotIn('/es/', response['Location'])

    def test_idioma_guardado_en_sesion(self):
        self.client.post(
            '/inventario/',
            {'_set_idioma': '1', 'idioma': 'en'},
            HTTP_REFERER='http://testserver/inventario/',
        )
        self.assertEqual(self.client.session.get('idioma'), 'en')


# ═══════════════════════════════════════════════════════════════════
# Punto 6 — API JSON propia
# ═══════════════════════════════════════════════════════════════════

class ApiVehiculosTests(TestCase):

    def test_lista_vehiculos_sin_datos(self):
        response = self.client.get('/api/vehiculos/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)
        self.assertIn('count', data)

    def test_lista_vehiculos_acepta_query(self):
        response = self.client.get('/api/vehiculos/?q=toyota')
        self.assertEqual(response.status_code, 200)

    def test_detalle_vehiculo_no_encontrado(self):
        response = self.client.get('/api/vehiculos/9999/')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.json())

    def test_tipo_cambio_estructura(self):
        response = self.client.get('/api/tipo-cambio/')
        self.assertIn(response.status_code, [200, 503])
        data = response.json()
        self.assertIn('usd_a_cop', data)
        self.assertIn('fuente', data)
        self.assertIn('disponible', data)

    def test_mis_compras_requiere_login(self):
        response = self.client.get('/api/mis-compras/')
        self.assertEqual(response.status_code, 302)

    def test_mis_compras_con_login(self):
        user = Usuario.objects.create_user(username='testapi', password='pass1234')
        self.client.login(username='testapi', password='pass1234')
        response = self.client.get('/api/mis-compras/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('compras', data)
        self.assertIn('count', data)


# ═══════════════════════════════════════════════════════════════════
# Punto 8 — Consumo API externa + clases concretas
# ═══════════════════════════════════════════════════════════════════

class TipoCambioServiceTests(TestCase):
    """Tests para TipoCambioService (clase concreta 1 — API en vivo)."""

    def _mock_resp(self, tasa):
        import json
        mock = MagicMock()
        mock.read.return_value = json.dumps({'rates': {'COP': tasa}}).encode()
        mock.__enter__ = lambda s: s
        mock.__exit__ = MagicMock(return_value=False)
        return mock

    def test_cop_a_usd_retorna_float(self):
        with patch('urllib.request.urlopen', return_value=self._mock_resp(4000.0)):
            resultado = TipoCambioService().cop_a_usd(4_000_000)
        self.assertAlmostEqual(resultado, 1000.0, places=1)

    def test_fallo_de_red_retorna_none(self):
        import urllib.error
        with patch('urllib.request.urlopen', side_effect=urllib.error.URLError('timeout')):
            resultado = TipoCambioService().cop_a_usd(1_000_000)
        self.assertIsNone(resultado)

    def test_cache_evita_llamadas_repetidas(self):
        with patch('urllib.request.urlopen', return_value=self._mock_resp(4100.0)) as mock_open:
            s = TipoCambioService()
            s.cop_a_usd(1_000_000)
            s.cop_a_usd(2_000_000)
        self.assertEqual(mock_open.call_count, 1)

    def test_tasa_invalida_retorna_none(self):
        import json
        mock = MagicMock()
        mock.read.return_value = json.dumps({'rates': {}}).encode()
        mock.__enter__ = lambda s: s
        mock.__exit__ = MagicMock(return_value=False)
        with patch('urllib.request.urlopen', return_value=mock):
            resultado = TipoCambioService().cop_a_usd(1_000_000)
        self.assertIsNone(resultado)


class TipoCambioFijoServiceTests(TestCase):
    """Tests para TipoCambioFijoService (clase concreta 2 — tasa fija)."""

    def test_siempre_retorna_valor(self):
        """La clase fija nunca retorna None — siempre hay un valor."""
        service = TipoCambioFijoService(tasa_cop=4200.0)
        resultado = service.cop_a_usd(4_200_000)
        self.assertIsNotNone(resultado)
        self.assertAlmostEqual(resultado, 1000.0, places=1)

    def test_tasa_configurable(self):
        """Se puede configurar la tasa en el constructor."""
        service = TipoCambioFijoService(tasa_cop=5000.0)
        self.assertEqual(service.obtener_tasa_usd_cop(), 5000.0)

    def test_no_requiere_red(self):
        """Funciona correctamente aunque no haya red."""
        import urllib.error
        service = TipoCambioFijoService(tasa_cop=4200.0)
        with patch('urllib.request.urlopen', side_effect=urllib.error.URLError('sin red')):
            # No llama a urlopen, no debe fallar
            resultado = service.cop_a_usd(1_000_000)
        self.assertIsNotNone(resultado)