# CarNest — Arquitectura del Sistema
### *Tu próximo auto, a un clic*

---

## Visión general

CarNest es una plataforma web de compra y venta de vehículos usados construida con Django 6 y desplegada en Google Cloud Platform. El sistema permite a usuarios particulares publicar vehículos, a administradores gestionar el inventario y a compradores explorar y adquirir vehículos verificados con pago integrado vía Stripe.

---

## Arquitectura de producción

```
Internet
    │
    ▼
┌─────────────────────────────────────────┐
│           Google Cloud Platform          │
│                                         │
│  ┌──────────┐    ┌──────────────────┐   │
│  │  Nginx   │───▶│    Gunicorn      │   │
│  │ puerto 80│    │  3 workers       │   │
│  └──────────┘    │  puerto 8000     │   │
│       │          └────────┬─────────┘   │
│       │                   │             │
│  Archivos          ┌──────▼──────┐      │
│  estáticos         │   Django 6  │      │
│  /staticfiles      │   CarNest   │      │
│  /media            └──────┬──────┘      │
│                           │             │
│                    ┌──────▼──────┐      │
│                    │ PostgreSQL  │      │
│                    │  puerto 5432│      │
│                    └─────────────┘      │
└─────────────────────────────────────────┘
```

Todos los servicios corren en contenedores Docker orquestados con Docker Compose.

---

## Stack tecnológico

| Capa | Tecnología | Versión |
|---|---|---|
| Backend | Python / Django | 3.12 / 6.0 |
| Base de datos | PostgreSQL | 15 |
| Servidor web | Nginx | Alpine |
| Servidor WSGI | Gunicorn | 21.2 |
| Frontend | Bootstrap | 5.3 |
| Contenedores | Docker / Docker Compose | - |
| Nube | Google Cloud Platform (Compute Engine) | - |
| Pagos | Stripe (modo test) | - |
| Tipo de cambio | open.er-api.com | - |

---

## Estructura de carpetas

```
CarNest/
├── CarNest/                  # Configuración principal Django
│   ├── settings.py           # Configuración desarrollo
│   ├── settings_prod.py      # Configuración producción
│   ├── urls.py               # URLconf principal
│   ├── asgi.py
│   └── wsgi.py
│
├── core/                     # App central — utilidades compartidas
│   ├── api_views.py          # Endpoints REST/JSON propios
│   ├── dependencies.py       # Inyector de dependencias
│   ├── protocols.py          # Interfaces (Protocol) — contratos
│   ├── services.py           # TipoCambioService (API externa)
│   ├── context_processors.py # Datos globales para templates
│   ├── tests.py              # 29 tests unitarios
│   └── urls.py               # Rutas de la API JSON
│
├── inventario/               # Gestión de vehículos
│   ├── models.py             # Vehiculo, FotoVehiculo, Concesionaria
│   ├── views.py              # Lista, detalle, crear vehículo
│   ├── services.py           # Lógica de negocio del inventario
│   └── urls.py
│
├── usuarios/                 # Autenticación y registro
│   ├── models.py             # Usuario (extiende AbstractUser)
│   ├── views.py              # Registro, login
│   ├── forms.py              # RegistroForm
│   └── urls.py
│
├── ventas/                   # Carrito y proceso de compra
│   ├── models.py             # Venta
│   ├── views.py              # Carrito, confirmar compra, mis compras
│   ├── services.py           # Lógica de ventas
│   ├── middleware.py         # Middleware de idioma
│   └── urls.py
│
├── anuncios/                 # Revisión de anuncios pendientes
│   ├── views.py              # Lista, aprobar, rechazar anuncios
│   ├── services.py           # Lógica de anuncios
│   └── urls.py
│
├── templates/                # Templates HTML (Django templates)
│   ├── base.html             # Template base con navbar
│   ├── auth_base.html        # Template base para auth
│   ├── index.html            # Página de inicio
│   ├── inventario/
│   ├── ventas/
│   ├── usuarios/
│   ├── anuncios/
│   └── partials/             # Componentes reutilizables
│
├── static/                   # CSS e imágenes estáticas
│   ├── css/
│   └── img/
│
├── locale/                   # Traducciones i18n
│   ├── es/LC_MESSAGES/       # Español
│   └── en/LC_MESSAGES/       # Inglés
│
├── docker-compose.yml        # Entorno de desarrollo
├── docker-compose.prod.yml   # Entorno de producción
├── nginx.conf                # Configuración Nginx
├── Dockerfile                # Imagen Docker
└── manage.py
```

---

## Modelo de datos

```
Usuario (AbstractUser)
    │ rol: cliente | propietario | admin
    │ telefono
    │
    ├──── Vehiculo (propietario)
    │         │ marca, modelo, año, precio
    │         │ combustible, transmision, color
    │         │ estado: posteado | en_venta | vendido
    │         │ imagen
    │         └── FotoVehiculo (fotos_extra)
    │
    └──── Venta (comprador)
              │ vehiculo (FK)
              │ precio_final
              └── fecha
```

---

## Flujo de negocio

```
Usuario normal publica vehículo
        │
        ▼
Estado: POSTEADO → aparece en /anuncios/ (solo admin)
        │
        ▼ Admin aprueba
Estado: EN_VENTA → aparece en /inventario/ (todos)
        │
        ▼ Comprador agrega al carrito y confirma pago (Stripe)
Estado: VENDIDO → desaparece del inventario
        │
        ▼
Venta registrada → aparece en /mis-compras/ del comprador
```

---

## Patrones de arquitectura implementados

### 1. Inversión de dependencias
Las vistas no importan servicios directamente. Usan un inyector (`core/dependencies.py`) que provee implementaciones concretas a través de interfaces definidas en `core/protocols.py`.

```
IVehiculoRepository ──► _VehiculoRepo (implementación)
IVentaService       ──► _VentaService (implementación)
ITipoCambioService  ──► TipoCambioService     (API en vivo)
                   └──► TipoCambioFijoService  (fallback offline)
```

### 2. Capa de servicios
Toda la lógica de negocio vive en archivos `services.py` de cada app, separada de las vistas. Las vistas solo coordinan HTTP — no contienen lógica.

### 3. Middleware de idioma
`ventas/middleware.py` intercepta requests para activar el idioma correcto según la sesión del usuario, conectando el selector visual con el sistema i18n de Django.

---

## API REST propia

| Método | Endpoint | Descripción | Auth |
|---|---|---|---|
| GET | `/api/vehiculos/` | Lista vehículos en venta | No |
| GET | `/api/vehiculos/?q=toyota` | Búsqueda filtrada | No |
| GET | `/api/vehiculos/<pk>/` | Detalle + precio USD | No |
| GET | `/api/tipo-cambio/` | Tasa USD↔COP en vivo | No |
| GET | `/api/mis-compras/` | Compras del usuario | Sí |

---

## Integraciones externas

### Stripe (pagos)
- Modo sandbox/test — no se procesan pagos reales
- Tarjeta de prueba: `4242 4242 4242 4242`
- Las claves se configuran vía variables de entorno

### open.er-api.com (tipo de cambio)
- API gratuita sin API key
- Devuelve tasa USD→COP en tiempo real
- Resultado cacheado 10 minutos en memoria
- Fallback a tasa fija si la API no responde

---

## Internacionalización

- Dos idiomas: **español** (`/es/`) e **inglés** (sin prefijo)
- Sin textos quemados — todo usa `{% trans %}` en templates y `_()` en Python
- Archivos de traducción en `locale/en/LC_MESSAGES/django.po`
- Compilar con: `python manage.py compilemessages`

---

## Despliegue

**VM en GCP:**
- Tipo: `e2-small` (2 vCPU, 2GB RAM)
- OS: Ubuntu 22.04 LTS
- IP pública: `34.27.19.160`

**URLs de producción:**
- Español: `http://34.27.19.160/es/`
- Inglés: `http://34.27.19.160/`
- Admin: `http://34.27.19.160/es/admin/`
- API: `http://34.27.19.160/api/vehiculos/`
