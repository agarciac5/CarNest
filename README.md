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

---

## 🚀 Cómo ejecutar el proyecto (desarrollo local)

### 1. Clonar el repositorio
```bash
git clone https://github.com/agarciac5/CarNest.git
cd CarNest
```

### 2. Levantar el proyecto
```bash
docker compose up --build
```

Espera a ver el mensaje:
```
web-1  | Starting development server at http://0.0.0.0:8000/
```

### 3. Compilar traducciones
```bash
docker compose exec web python manage.py makemessages -l en --no-obsolete
docker compose exec web python manage.py compilemessages
```

### 4. Crear superusuario (opcional)
```bash
docker compose exec web python manage.py createsuperuser
```

---

## 🗺️ Rutas principales (desarrollo local)

| Ruta | Descripción |
|---|---|
| `http://localhost:8000/es/` | Página de inicio (español) |
| `http://localhost:8000/en/` | Página de inicio (inglés) |
| `http://localhost:8000/es/inventario/` | Catálogo de vehículos |
| `http://localhost:8000/es/usuarios/login/` | Iniciar sesión |
| `http://localhost:8000/es/usuarios/registro/` | Registro de usuario |
| `http://localhost:8000/es/carrito/` | Carrito de compras |
| `http://localhost:8000/es/anuncios/` | Panel de anuncios (solo staff) |
| `http://localhost:8000/es/admin/` | Panel de administración |
| `http://localhost:8000/api/vehiculos/` | API JSON — lista de vehículos |
| `http://localhost:8000/api/vehiculos/<pk>/` | API JSON — detalle de vehículo |
| `http://localhost:8000/api/tipo-cambio/` | API JSON — tasa USD/COP en vivo |
| `http://localhost:8000/api/mis-compras/` | API JSON — compras del usuario |

---

## ✨ Funcionalidades implementadas

### Internacionalización (i18n)
- Soporte completo en **español** e **inglés**
- Selector de idioma al primer acceso
- Archivos de traducción en `locale/en/` y `locale/es/`
- Sin textos quemados — todo usa `{% trans %}` y `gettext`

### Servicio web JSON propio
Endpoints REST propios disponibles sin autenticación (excepto `/api/mis-compras/`):
```bash
curl http://34.27.19.160/api/vehiculos/
curl http://34.27.19.160/api/tipo-cambio/
curl http://34.27.19.160/api/vehiculos/1/
```

### Consumo de API externa
- Integración con **open.er-api.com** para tipo de cambio USD → COP en tiempo real
- El precio en USD aparece en el detalle de cada vehículo cuando el idioma es inglés
- Caché en memoria de 10 minutos para no saturar la API

### Inversión de dependencias
Una interfaz (`ITipoCambioService`) con **dos clases concretas**:
- `TipoCambioService` — obtiene tasa en vivo desde la API externa
- `TipoCambioFijoService` — usa tasa fija hardcodeada (fallback sin red)
- `TipoCambioConFallback` — orquesta ambas: intenta API, si falla usa la fija

Las vistas no importan servicios directamente — usan `core/dependencies.py` como inyector, lo que permite sustituir implementaciones en tests.

### Pruebas unitarias
```bash
docker compose exec web python manage.py test core --verbosity=2
```
29 tests cubriendo i18n, API JSON, inversión de dependencias y API externa.

---

## 🏗️ Arquitectura de producción (GCP)

```
Internet
    ↓
Nginx (puerto 80)     ← recibe peticiones HTTP
    ↓
Gunicorn (puerto 8000) ← servidor WSGI para Django
    ↓
Django (CarNest)      ← aplicación web
    ↓
PostgreSQL 15         ← base de datos
```

### Despliegue en GCP
```bash
# En la VM de GCP
git clone https://github.com/agarciac5/CarNest.git
cd CarNest
cp env.prod .env
nano .env  # configurar IP, SECRET_KEY y contraseña
docker compose -f docker-compose.prod.yml --env-file .env up --build -d
```

### Comandos útiles en producción
```bash
# Ver estado
docker compose -f docker-compose.prod.yml ps

# Ver logs
docker compose -f docker-compose.prod.yml logs -f web

# Reconstruir tras cambios
docker compose -f docker-compose.prod.yml --env-file .env up --build -d

# Actualizar desde GitHub
git pull && docker compose -f docker-compose.prod.yml --env-file .env up --build -d

# Crear superusuario
docker compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Compilar traducciones
docker compose -f docker-compose.prod.yml exec web python manage.py compilemessages
```

---

## 🔑 Roles de usuario

| Rol | Permisos |
|---|---|
| Usuario normal | Publicar vehículos (van a revisión), comprar vehículos |
| Staff / Admin | Aprobar o rechazar anuncios, publicar directo al inventario |

---

## 🛠️ Stack tecnológico

| Componente | Tecnología |
|---|---|
| Backend | Python 3.12 / Django 6 |
| Base de datos | PostgreSQL 15 |
| Frontend | Bootstrap 5 |
| Servidor web | Nginx + Gunicorn |
| Infraestructura | Docker / Docker Compose |
| Nube | Google Cloud Platform (Compute Engine) |
| Traducciones | Django i18n (gettext) |
| API externa | open.er-api.com (tipo de cambio) |

---

## 📁 Estructura del proyecto

```
CarNest/
├── CarNest/                  # Configuración principal
│   ├── settings.py           # Configuración desarrollo
│   ├── settings_prod.py      # Configuración producción
│   └── urls.py               # URLs principales
├── core/                     # Utilidades compartidas
│   ├── api_views.py          # Endpoints JSON propios
│   ├── dependencies.py       # Inyector de dependencias
│   ├── protocols.py          # Interfaces (Protocol)
│   ├── services.py           # TipoCambioService (API externa)
│   └── tests.py              # 29 tests unitarios
├── inventario/               # Gestión de vehículos
├── usuarios/                 # Autenticación y registro
├── ventas/                   # Carrito y compras
│   └── middleware.py         # Middleware de idioma
├── anuncios/                 # Revisión de anuncios
├── templates/                # Templates HTML
├── static/                   # CSS e imágenes
├── locale/                   # Traducciones (es, en)
├── docker-compose.yml        # Desarrollo local
├── docker-compose.prod.yml   # Producción GCP
├── nginx.conf                # Configuración Nginx
├── Dockerfile                # Imagen Docker
└── manage.py
```

---

## 👥 Equipo

Proyecto desarrollado para la materia de Ingeniería de Software.
Repositorio: https://github.com/agarciac5/CarNest
