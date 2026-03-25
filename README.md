# CarNest 

Plataforma web de compra y venta de vehículos usados. Permite a usuarios particulares publicar sus vehículos, a la concesionaria gestionar el inventario y a los compradores explorar y adquirir vehículos verificados.

---

## Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop) instalado y corriendo

---

## Cómo ejecutar el proyecto

### 1. Clonar el repositorio
```bash
git clone https://github.com/agarciac5/CarNest.git
cd CarNest
git checkout development
```

### 2. Levantar el proyecto
```bash
docker-compose up --build
```

Espera a ver el mensaje:
```
web-1  | Starting development server at http://0.0.0.0:8000/
```

### 3. Cargar datos de prueba (otra terminal)
```bash
docker-compose exec web python manage.py seed_inventario
```

### 4. Crear superusuario (opcional)
```bash
docker-compose exec web python manage.py createsuperuser
```

---

## Rutas principales

| Ruta | Descripción |
|---|---|
| `http://localhost:8000/` | Página de inicio |
| `http://localhost:8000/inventario/` | Catálogo de vehículos |
| `http://localhost:8000/usuarios/login/` | Iniciar sesión |
| `http://localhost:8000/usuarios/registro/` | Registro de usuario |
| `http://localhost:8000/carrito/` | Carrito de compras |
| `http://localhost:8000/admin/` | Panel de administración |

---

## Usuario de prueba

Generado automáticamente con `seed_inventario`:

| Campo | Valor |
|---|---|
| Usuario | `carnest_demo` |
| Contraseña | `demo12345` |

---

## Comandos útiles
```bash
docker-compose up            # levantar sin reconstruir
docker-compose up --build    # levantar y reconstruir imagen
docker-compose down          # apagar contenedores
docker-compose down -v       # apagar y borrar la base de datos
```

---

## Stack tecnológico

- **Backend:** Python 3 / Django 6
- **Base de datos:** PostgreSQL 16
- **Frontend:** Bootstrap 5
- **Infraestructura:** Docker / Docker Compose

---

## Estructura del proyecto
```
CarNest/
├── CarNest/          # Configuración principal (settings, urls)
├── inventario/       # Gestión de vehículos
├── usuarios/         # Autenticación y registro
├── ventas/           # Módulo de ventas
├── anuncios/         # Módulo de anuncios
├── core/             # Utilidades compartidas
├── templates/        # Templates HTML
├── static/           # Archivos estáticos (CSS, imágenes)
├── docker-compose.yml
├── dockerfile
└── manage.py
```

---

## Documentación

La documentación completa del proyecto está disponible en la [Wiki del repositorio](https://github.com/agarciac5/CarNest/wiki).