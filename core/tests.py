"""
core/tests.py
-------------
Tests unitarios para los 4 puntos implementados:

  Punto 3 - Inversión de dependencias:
      - Verificar que los protocolos son satisfechos por las implementaciones.
      - Verificar que las vistas usan dependencias inyectadas (mock).

  Punto 5 - Internacionalización:
      - Verificar que las URLs responden con el prefijo de idioma correcto.
      - Verificar que el middleware activa el idioma de sesión.

  Punto 6 - API JSON propia:
      - GET /api/vehiculos/ → 200 con JSON válido.
      - GET /api/vehiculos/<pk>/ → 200 con datos del vehículo.
      - GET /api/tipo-cambio/ → 200 o 503 con estructura correcta.
      - GET /api/mis-compras/ → 401 sin login, 200 con login.

  Punto 8 - API externa:
      - TipoCambioService.cop_a_usd() retorna float o None.
      - El caché evita llamadas repetidas a la API.
      - Fallo de red retorna None sin lanzar excepción.
"""
from unittest.mock import patch, MagicMock

from django.test import TestCase, RequestFactory, Client
from django.contrib.auth import get_user_model

from core.protocols import IVehiculoRepository, IVentaService, ITipoCambioService
from core.dependencies import (
    _VehiculoRepo, _VentaService,
    get_vehiculo_repo, get_tipo_cambio_service,
)
from core.services import TipoCambioService

Usuario = get_user_model()


# ═══════════════════════════════════════════════════════════════════
# Punto 3 — Inversión de dependencias
# ═══════════════════════════════════════════════════════════════════

class ProtocolosTests(TestCase):
    """Las implementaciones concretas deben satisfacer los protocolos."""

    def test_vehiculo_repo_cumple_protocolo(self):
        repo = _VehiculoRepo()
        self.assertIsInstance(repo, IVehiculoRepository)

    def test_venta_service_cumple_protocolo(self):
        service = _VentaService()
        self.assertIsInstance(service, IVentaService)

    def test_tipo_cambio_service_cumple_protocolo(self):
        service = TipoCambioService()
        self.assertIsInstance(service, ITipoCambioService)


class InyeccionDependenciasTests(TestCase):
    """Las vistas usan get_vehiculo_repo() — se puede reemplazar en tests."""

    def setUp(self):
        import core.dependencies as deps
        # Guardamos el original
        self._original = deps._vehiculo_repo

    def tearDown(self):
        import core.dependencies as deps
        # Restauramos el original
        deps._vehiculo_repo = self._original

    def test_reemplazo_repo_en_vista(self):
        """Podemos inyectar un repo falso y la vista lo usa."""
        import core.dependencies as deps

        mock_repo = MagicMock()
        mock_repo.listar_en_venta.return_value = []
        deps._vehiculo_repo = mock_repo

        client = Client()
        response = client.get('/inventario/')

        mock_repo.listar_en_venta.assert_called_once()
        self.assertEqual(response.status_code, 200)


# ═══════════════════════════════════════════════════════════════════
# Punto 5 — Internacionalización
# ═══════════════════════════════════════════════════════════════════

class I18nURLTests(TestCase):
    """Las URLs respetan el prefijo de idioma configurado."""

    def test_home_español_sin_prefijo(self):
        """Español (idioma por defecto) no lleva prefijo /es/."""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_home_ingles_con_prefijo(self):
        """Inglés lleva prefijo /en/."""
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
    """El middleware guarda y activa el idioma de sesión."""

    def test_cambio_a_ingles_redirige(self):
        """POST con _set_idioma=1 e idioma=en debe redirigir a /en/."""
        response = self.client.post(
            '/inventario/',
            {'_set_idioma': '1', 'idioma': 'en'},
            HTTP_REFERER='http://testserver/inventario/',
        )
        self.assertEqual(response.status_code, 302)
        self.assertIn('/en/', response['Location'])

    def test_cambio_a_español_redirige_sin_prefijo(self):
        """POST con idioma=es debe redirigir sin prefijo /es/."""
        response = self.client.post(
            '/en/inventario/',
            {'_set_idioma': '1', 'idioma': 'es'},
            HTTP_REFERER='http://testserver/en/inventario/',
        )
        self.assertEqual(response.status_code, 302)
        location = response['Location']
        self.assertNotIn('/es/', location)

    def test_idioma_guardado_en_sesion(self):
        """Después del cambio, la sesión debe tener el idioma elegido."""
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
    """Endpoints de la API JSON devuelven respuestas válidas."""

    def test_lista_vehiculos_sin_datos(self):
        """GET /api/vehiculos/ → 200 con lista vacía."""
        response = self.client.get('/api/vehiculos/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('results', data)
        self.assertIn('count', data)
        self.assertEqual(data['count'], 0)

    def test_lista_vehiculos_acepta_query(self):
        """GET /api/vehiculos/?q=toyota → 200."""
        response = self.client.get('/api/vehiculos/?q=toyota')
        self.assertEqual(response.status_code, 200)

    def test_detalle_vehiculo_no_encontrado(self):
        """GET /api/vehiculos/9999/ → 404."""
        response = self.client.get('/api/vehiculos/9999/')
        self.assertEqual(response.status_code, 404)
        data = response.json()
        self.assertIn('error', data)

    def test_tipo_cambio_estructura(self):
        """GET /api/tipo-cambio/ → JSON con campos esperados."""
        response = self.client.get('/api/tipo-cambio/')
        self.assertIn(response.status_code, [200, 503])
        data = response.json()
        self.assertIn('usd_a_cop', data)
        self.assertIn('fuente', data)
        self.assertIn('disponible', data)

    def test_mis_compras_requiere_login(self):
        """GET /api/mis-compras/ sin sesión → 302 redirect al login."""
        response = self.client.get('/api/mis-compras/')
        self.assertEqual(response.status_code, 302)

    def test_mis_compras_con_login(self):
        """GET /api/mis-compras/ autenticado → 200 con lista."""
        user = Usuario.objects.create_user(username='testapi', password='pass1234')
        self.client.login(username='testapi', password='pass1234')
        response = self.client.get('/api/mis-compras/')
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('compras', data)
        self.assertIn('count', data)


# ═══════════════════════════════════════════════════════════════════
# Punto 8 — Consumo API externa
# ═══════════════════════════════════════════════════════════════════

class TipoCambioServiceTests(TestCase):
    """TipoCambioService maneja la API externa correctamente."""

    def _make_mock_response(self, tasa_cop: float):
        """Crea un mock de urllib response con la tasa dada."""
        import json
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps(
            {'rates': {'COP': tasa_cop}}
        ).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        return mock_resp

    def test_cop_a_usd_retorna_float(self):
        """Con API disponible, cop_a_usd devuelve un float."""
        service = TipoCambioService()
        mock_resp = self._make_mock_response(4000.0)

        with patch('urllib.request.urlopen', return_value=mock_resp):
            resultado = service.cop_a_usd(4_000_000)

        self.assertIsNotNone(resultado)
        self.assertAlmostEqual(resultado, 1000.0, places=1)

    def test_fallo_de_red_retorna_none(self):
        """Si la API falla, cop_a_usd retorna None sin lanzar excepción."""
        import urllib.error
        service = TipoCambioService()

        with patch('urllib.request.urlopen', side_effect=urllib.error.URLError('timeout')):
            resultado = service.cop_a_usd(1_000_000)

        self.assertIsNone(resultado)

    def test_cache_evita_llamadas_repetidas(self):
        """La segunda llamada usa caché, no llama a urlopen de nuevo."""
        service = TipoCambioService()
        mock_resp = self._make_mock_response(4100.0)

        with patch('urllib.request.urlopen', return_value=mock_resp) as mock_open:
            service.cop_a_usd(1_000_000)
            service.cop_a_usd(2_000_000)

        # urlopen se llamó solo una vez (segunda usa caché)
        self.assertEqual(mock_open.call_count, 1)

    def test_tasa_invalida_retorna_none(self):
        """Respuesta malformada de la API retorna None."""
        import json
        service = TipoCambioService()
        mock_resp = MagicMock()
        mock_resp.read.return_value = json.dumps({'rates': {}}).encode()
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)

        with patch('urllib.request.urlopen', return_value=mock_resp):
            resultado = service.cop_a_usd(1_000_000)

        self.assertIsNone(resultado)

    def test_obtener_tasa_usd_cop(self):
        """obtener_tasa_usd_cop retorna el valor directamente de la API."""
        service = TipoCambioService()
        mock_resp = self._make_mock_response(4250.0)

        with patch('urllib.request.urlopen', return_value=mock_resp):
            tasa = service.obtener_tasa_usd_cop()

        self.assertAlmostEqual(tasa, 4250.0, places=1)