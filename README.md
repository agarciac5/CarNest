# CarNest 🚗

Plataforma web de compra y venta de vehículos usados. Permite a usuarios particulares publicar sus vehículos, a la concesionaria gestionar el inventario y a los compradores explorar y adquirir vehículos verificados.

---

## 🌐 Despliegue en producción

La aplicación está desplegada en Google Cloud Platform:

| Entorno | URL |
|---|---|
| Español | http://34.27.19.160/es/ |
| Inglés | http://34.27.19.160/en/ |
| Admin | http://34.27.19.160/es/admin/ |
| API JSON | http://34.27.19.160/api/vehiculos/ |

---

## 📋 Requisitos (desarrollo local)

- Docker Desktop instalado y corriendo
- Git instalado

---

# 🚀 Cómo ejecutar el proyecto (desarrollo local)

## 1. Clonar el repositorio

```bash
git clone https://github.com/agarciac5/CarNest.git
cd CarNest
```

---

## 2. Crear archivo `.env`

Crear un archivo `.env` en la raíz del proyecto:

```env
STRIPE_PUBLIC_KEY=pk_test_xxxxxxxxxxxxxxxxx
STRIPE_SECRET_KEY=sk_test_xxxxxxxxxxxxxxxxx
```

Las claves se obtienen desde el Dashboard de Stripe en modo prueba.

---

## 3. Levantar el proyecto

```bash
docker compose up --build
```

Espera a ver el mensaje:

```bash
web-1  | Starting development server at http://0.0.0.0:8000/
```

---

## 4. Ejecutar migraciones

```bash
docker compose exec web python manage.py migrate
```

---

## 5. Compilar traducciones

```bash
docker compose exec web python manage.py makemessages -l en --no-obsolete
docker compose exec web python manage.py compilemessages
```

---

## 6. Crear superusuario (opcional)

```bash
docker compose exec web python manage.py createsuperuser
```

---

# 🗺️ Rutas principales (desarrollo local)

| Ruta | Descripción |
|---|---|
| `http://localhost:8000/es/` | Página de inicio (español) |
| `http://localhost:8000/en/` | Página de inicio (inglés) |
| `http://localhost:8000/es/inventario/` | Catálogo de vehículos |
| `http://localhost:8000/es/usuarios/login/` | Iniciar sesión |
| `http://localhost:8000/es/usuarios/registro/` | Registro de usuario |
| `http://localhost:8000/es/carrito/` | Carrito de compras |
| `http://localhost:8000/es/checkout/` | Pasarela de pago Stripe |
| `http://localhost:8000/es/anuncios/` | Panel de anuncios (solo staff) |
| `http://localhost:8000/es/admin/` | Panel de administración |
| `http://localhost:8000/api/vehiculos/` | API JSON — lista de vehículos |
| `http://localhost:8000/api/vehiculos/<pk>/` | API JSON — detalle de vehículo |
| `http://localhost:8000/api/tipo-cambio/` | API JSON — tasa USD/COP en vivo |
| `http://localhost:8000/api/mis-compras/` | API JSON — compras del usuario |

---

# ✨ Funcionalidades implementadas

## 🛒 Sistema de compras y carrito

- Agregar y eliminar vehículos del carrito
- Persistencia del carrito en sesión
- Validación de disponibilidad antes de comprar
- Historial de compras por usuario
- Protección contra compras duplicadas

---

## 💳 Integración con Stripe

Pasarela de pago implementada usando Stripe Checkout en modo prueba.

### Características

- Pago seguro mediante Stripe
- Uso de claves privadas y públicas mediante variables de entorno
- Confirmación automática del pago exitoso
- Asociación de compras con `PaymentIntent`
- Registro del estado del pago en base de datos
- Soporte para múltiples vehículos en una sola compra

### Tarjetas de prueba Stripe

| Tipo | Número |
|---|---|
| Pago exitoso | `4242 4242 4242 4242` |
| Pago rechazado | `4000 0000 0000 9995` |

Usar:
- Fecha futura cualquiera
- CVV cualquiera
- Código postal cualquiera

---

## 🌎 Internacionalización (i18n)

- Soporte completo en **español** e **inglés**
- Selector de idioma al primer acceso
- Archivos de traducción en `locale/en/` y `locale/es/`
- Sin textos hardcodeados — todo usa `{% trans %}` y `gettext`

---

## 🔌 Servicio web JSON propio

Endpoints REST disponibles sin autenticación (excepto `/api/mis-compras/`):

```bash
curl http://34.27.19.160/api/vehiculos/
curl http://34.27.19.160/api/tipo-cambio/
curl http://34.27.19.160/api/vehiculos/1/
```

---

## 🌐 Consumo de API externa

- Integración con `open.er-api.com` para tipo de cambio USD → COP en tiempo real
- El precio en USD aparece en el detalle de cada vehículo cuando el idioma es inglés
- Caché en memoria de 10 minutos para evitar saturar la API

---

## 🧩 Inversión de dependencias

Una interfaz (`ITipoCambioService`) con múltiples implementaciones:

- `TipoCambioService` — obtiene tasa en vivo desde API externa
- `TipoCambioFijoService` — usa tasa fija hardcodeada
- `TipoCambioConFallback` — intenta API y si falla usa tasa fija

Las vistas no dependen directamente de servicios concretos, usando `core/dependencies.py` como inyector.

---

## 🧪 Pruebas unitarias

```bash
docker compose exec web python manage.py test core --verbosity=2
```

Tests cubriendo:
- Internacionalización
- API JSON
- Inversión de dependencias
- Integración API externa
- Servicios de ventas

---

# 🏗️ Arquitectura de producción (GCP)

```text
Internet
    ↓
Nginx (puerto 80)
    ↓
Gunicorn (puerto 8000)
    ↓
Django (CarNest)
    ↓
PostgreSQL 15
```

---

# ☁️ Despliegue en GCP

## 1. Clonar proyecto

```bash
git clone https://github.com/agarciac5/CarNest.git
cd CarNest
```

---

## 2. Crear variables de entorno

```bash
cp env.prod .env
nano .env
```

Configurar:
- SECRET_KEY
- PostgreSQL
- Stripe Keys
- IP pública

---

## 3. Levantar producción

```bash
docker compose -f docker-compose.prod.yml --env-file .env up --build -d
```

---

# 🛠️ Comandos útiles en producción

## Ver estado

```bash
docker compose -f docker-compose.prod.yml ps
```

---

## Ver logs

```bash
docker compose -f docker-compose.prod.yml logs -f web
```

---

## Reconstruir contenedores

```bash
docker compose -f docker-compose.prod.yml --env-file .env up --build -d
```

---

## Actualizar desde GitHub

```bash
git pull
docker compose -f docker-compose.prod.yml --env-file .env up --build -d
```

---

## Crear superusuario

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
```

---

## Compilar traducciones

```bash
docker compose -f docker-compose.prod.yml exec web python manage.py compilemessages
```

---

# 🔑 Roles de usuario

| Rol | Permisos |
|---|---|
| Usuario normal | Publicar vehículos, comprar vehículos |
| Staff / Admin | Aprobar anuncios y publicar inventario |

---

# 🛠️ Stack tecnológico

| Componente | Tecnología |
|---|---|
| Backend | Python 3.12 / Django 6 |
| Base de datos | PostgreSQL 15 |
| Frontend | Bootstrap 5 |
| Pasarela de pago | Stripe |
| Servidor web | Nginx + Gunicorn |
| Infraestructura | Docker / Docker Compose |
| Nube | Google Cloud Platform |
| Traducciones | Django i18n |
| API externa | open.er-api.com |

---

# 📁 Estructura del proyecto

```text
CarNest/
├── CarNest/
│   ├── settings.py
│   ├── settings_prod.py
│   └── urls.py
├── core/
│   ├── api_views.py
│   ├── dependencies.py
│   ├── protocols.py
│   ├── services.py
│   └── tests.py
├── inventario/
├── usuarios/
├── ventas/
│   ├── stripe_views.py
│   ├── services.py
│   ├── models.py
│   └── middleware.py
├── anuncios/
├── templates/
├── static/
├── locale/
├── docker-compose.yml
├── docker-compose.prod.yml
├── nginx.conf
├── Dockerfile
├── requirements.txt
├── .env
└── manage.py
```

---

# 👥 Equipo

Proyecto desarrollado para la materia de Ingeniería de Software.

Repositorio:
https://github.com/agarciac5/CarNest