# CarNest — Onboarding
### *Tu próximo auto, a un clic*

Guía completa para que un desarrollador nuevo pueda entender, configurar y contribuir al proyecto desde cero.

---

## ¿Qué es CarNest?

CarNest es una plataforma web de compra y venta de vehículos usados. Permite a usuarios particulares publicar sus vehículos para revisión, a administradores gestionar el inventario y a compradores explorar, filtrar y adquirir vehículos verificados con pago integrado.

**Slogan:** *Tu próximo auto, a un clic*

---

## Requisitos previos

| Herramienta | Versión mínima | Para qué |
|---|---|---|
| Docker Desktop | 4.x | Correr el proyecto |
| Git | 2.x | Clonar y contribuir |
| VS Code | Cualquiera | Editor recomendado |

No necesitas instalar Python, PostgreSQL ni ninguna otra dependencia — Docker lo maneja todo.

---

## Configuración inicial (5 minutos)

### 1. Clonar el repositorio
```bash
git clone https://github.com/agarciac5/CarNest.git
cd CarNest
```

### 2. Levantar el proyecto
```bash
docker compose up --build
```

Espera a ver:
```
web-1  | Starting development server at http://0.0.0.0:8000/
```

### 3. Compilar traducciones
```bash
docker compose exec web python manage.py makemessages -l en --no-obsolete
docker compose exec web python manage.py compilemessages
```

### 4. Crear superusuario
```bash
docker compose exec web python manage.py createsuperuser
```

Asignar rol admin al superusuario:
```bash
docker compose exec web python manage.py shell -c "from usuarios.models import Usuario; u = Usuario.objects.get(username='TU_USERNAME'); u.rol='admin'; u.is_staff=True; u.is_superuser=True; u.save(); print('OK')"
```

### 5. Abrir la aplicación
```
http://localhost:8000/es/    ← español
http://localhost:8000/       ← inglés
http://localhost:8000/es/admin/  ← panel de admin
```

---

## Estructura del proyecto (lo que necesitas saber)

```
CarNest/
├── core/            ← utilidades compartidas, API JSON, inyector de dependencias
├── inventario/      ← todo lo relacionado con vehículos
├── usuarios/        ← registro y login
├── ventas/          ← carrito, compras, middleware de idioma
├── anuncios/        ← panel de revisión para admins
└── templates/       ← todos los HTMLs
```

Cada app sigue el mismo patrón:
```
app/
├── models.py    ← qué datos guarda
├── services.py  ← lógica de negocio (aquí va el código importante)
├── views.py     ← solo maneja HTTP, llama a services
└── urls.py      ← rutas de la app
```

**Regla de oro:** nunca pongas lógica de negocio en las vistas. Va en `services.py`.

---

## Roles de usuario

| Rol | Cómo crearlo | Qué puede hacer |
|---|---|---|
| Cliente | Registro normal en `/es/usuarios/registro/` | Ver catálogo, comprar, publicar vehículos (van a revisión) |
| Admin/Staff | `createsuperuser` + asignar `rol='admin'` | Todo lo anterior + aprobar/rechazar anuncios, publicar directo al inventario |

---

## Flujo principal del negocio

```
1. Usuario normal se registra
2. Publica un vehículo → va a estado "posteado"
3. Admin ve el vehículo en /es/anuncios/
4. Admin aprueba → vehículo pasa a "en_venta" y aparece en /es/inventario/
5. Comprador agrega al carrito
6. Comprador confirma pago con Stripe (tarjeta test: 4242 4242 4242 4242)
7. Vehículo pasa a "vendido" y aparece en /es/mis-compras/ del comprador
```

---

## Variables de entorno

Crea un archivo `.env` en la raíz (copia de `env.prod`):

```bash
cp env.prod .env
```

Variables importantes:

| Variable | Descripción | Ejemplo |
|---|---|---|
| `POSTGRES_DB` | Nombre de la base de datos | `carnest` |
| `POSTGRES_USER` | Usuario de PostgreSQL | `carnest` |
| `POSTGRES_PASSWORD` | Contraseña de PostgreSQL | `carnest` |
| `DJANGO_SECRET_KEY` | Clave secreta de Django | Generar con `secrets.token_urlsafe(50)` |
| `DJANGO_ALLOWED_HOSTS` | IPs permitidas | `localhost,34.27.19.160` |
| `STRIPE_PUBLIC_KEY` | Clave pública de Stripe | `pk_test_...` |
| `STRIPE_SECRET_KEY` | Clave secreta de Stripe | `sk_test_...` |

---

## Comandos útiles del día a día

```bash
# Levantar el proyecto
docker compose up

# Levantar y reconstruir (después de cambiar requirements.txt)
docker compose up --build

# Apagar
docker compose down

# Apagar y borrar la base de datos (reset completo)
docker compose down -v

# Crear migraciones después de cambiar models.py
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate

# Abrir shell de Django (para debugging)
docker compose exec web python manage.py shell

# Correr tests
docker compose exec web python manage.py test core --verbosity=2

# Ver logs en vivo
docker compose logs -f web

# Compilar traducciones
docker compose exec web python manage.py compilemessages
```

---

## Cómo agregar una funcionalidad nueva

### Ejemplo: agregar un campo al modelo Vehiculo

1. Edita `inventario/models.py`:
```python
color_secundario = models.CharField(max_length=40, blank=True, default='')
```

2. Crea la migración:
```bash
docker compose exec web python manage.py makemigrations
docker compose exec web python manage.py migrate
```

3. Si necesitas mostrarlo en la vista, edita `inventario/services.py` y luego el template correspondiente en `templates/inventario/`.

### Ejemplo: agregar un endpoint a la API JSON

1. Agrega la vista en `core/api_views.py`:
```python
@require_GET
def api_nuevo_endpoint(request):
    data = {...}
    return JsonResponse(data)
```

2. Registra la URL en `core/urls.py`:
```python
path('nuevo/', api_nuevo_endpoint, name='api_nuevo'),
```

---

## Internacionalización — cómo traducir textos nuevos

Si agregas texto nuevo en templates o Python:

**En templates:**
```html
{% load i18n %}
<p>{% trans "Tu texto aquí" %}</p>
```

**En Python:**
```python
from django.utils.translation import gettext as _
mensaje = _('Tu texto aquí')
```

Luego actualiza los archivos de traducción:
```bash
docker compose exec web python manage.py makemessages -l en --no-obsolete
```

Abre `locale/en/LC_MESSAGES/django.po` y rellena el `msgstr ""` vacío con la traducción en inglés. Finalmente compila:
```bash
docker compose exec web python manage.py compilemessages
```

---

## Cómo contribuir

1. Crea una rama desde `development`:
```bash
git checkout development
git pull origin development
git checkout -b feature/nombre-de-tu-feature
```

2. Haz tus cambios y corre los tests:
```bash
docker compose exec web python manage.py test core --verbosity=2
```

3. Commit y push:
```bash
git add .
git commit -m "feat: descripción de tu cambio"
git push origin feature/nombre-de-tu-feature
```

4. Abre un Pull Request hacia `development` en GitHub.

---

## Despliegue en producción (GCP)

Ver `README.md` para instrucciones completas de despliegue.

**Resumen rápido — actualizar producción después de un cambio:**
```bash
# En la VM de GCP (SSH)
cd CarNest
git pull origin main
docker compose -f docker-compose.prod.yml --env-file .env up --build -d
```

---

## Troubleshooting frecuente

| Problema | Causa probable | Solución |
|---|---|---|
| `502 Bad Gateway` | Gunicorn no arrancó | `docker compose logs web` para ver el error |
| `DisallowedHost` | IP no en `ALLOWED_HOSTS` | Agregar IP al `.env` y reconstruir |
| `STATIC_ROOT not set` | Falta config en settings | Agregar `STATIC_ROOT = '/app/staticfiles'` |
| Traducciones no aplican | `.mo` no compilado | `python manage.py compilemessages` |
| `No module named X` | Dependencia nueva | `docker compose up --build` |
| Vehículo da 404 | Estado `posteado`, no `en_venta` | Admin debe aprobarlo en `/es/anuncios/` |

---

## Contacto del equipo

Repositorio: https://github.com/agarciac5/CarNest
Producción: http://34.27.19.160/es/
