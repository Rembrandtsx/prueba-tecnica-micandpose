# API de Gestion de Tareas

---

## Entregables

El proyecto incluye:

- API REST con 6 endpoints
- Base de datos MySQL 8.0
- Procesamiento concurrente de tareas por batch
- Docker Compose configurado
- Pruebas unitarias e integracion (32 tests, 86% cobertura)
- Documentacion Swagger/OpenAPI
- Coleccion de Postman
- Codigo tipado siguiendo PEP8

---

## Inicio Rapido con Docker

### Prerrequisitos

Docker y Docker Compose instalados.

### Pasos

1. Clonar el repositorio

2. Crear archivo `.env` (opcional, tiene valores por defecto):
   ```bash
   # Database Configuration
   DB_HOST=mysql
   DB_PORT=3306
   DB_NAME=task_management
   DB_USER=root
   DB_PASSWORD=changeme

   # Application Configuration
   APP_ENV=development
   APP_DEBUG=true
   APP_PORT=8000
   ```

3. Iniciar los servicios:
   ```bash
   docker compose up -d
   ```

4. Verificar que todo está corriendo:
   ```bash
   docker compose ps
   ```

5. Acceder a la documentacion:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

### Comandos Docker

```bash
# Ver logs de la aplicacion
docker compose logs -f app

# Ver logs de MySQL
docker compose logs -f mysql

# Detener los servicios
docker compose down

# Reconstruir la imagen (después de cambios en código)
docker compose up -d --build

# Reconstruir sin caché (limpieza completa)
docker compose down
docker compose build --no-cache app
docker compose up -d
```

---

## Como ejecutar (desarrollo local sin Docker)

### Prerrequisitos

- Python 3.11+
- MySQL 8.0 instalado y corriendo

### Pasos

1. Crear entorno virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate
   ```

2. Instalar dependencias:
   ```bash
   pip install -r requirements.txt
   ```

3. Configurar base de datos MySQL:
   ```bash
   # Conectar a MySQL
   mysql -u root -p

   # Crear la base de datos
   CREATE DATABASE task_management;

   # Ejecutar script de inicialización
   mysql -u root -p task_management < scripts/init.sql
   ```

4. Crear archivo `.env` con los valores de `.env.example`:
   ```bash
   cp .env.example .env
   # Editar .env con tus credenciales de MySQL
   ```

5. Ejecutar la aplicación:
   ```bash
   uvicorn app.main:app --reload
   ```

6. Acceder a la documentacion:
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

---

## Endpoints de la API

### Gestion de Tareas

| Método | Endpoint | Descripcion |
|--------|----------|-------------|
| POST | `/api/tasks` | Crea una nueva tarea |
| GET | `/api/tasks` | Lista todas las tareas (con paginacion y filtro por status) |
| GET | `/api/tasks/{id}` | Retorna una tarea por su ID |
| PUT | `/api/tasks/{id}` | Actualiza una tarea existente |
| DELETE | `/api/tasks/{id}` | Elimina una tarea |
| POST | `/api/tasks/process-batch` | Procesa múltiples tareas concurrentemente |

### Ejemplos de Uso

#### Crear Tarea
```bash
curl -X POST "http://localhost:8000/api/tasks" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Completar documentacion del proyecto",
    "description": "Escribir documentacion completa",
    "priority": 4
  }'
```

#### Listar Tareas con Paginacion
```bash
curl "http://localhost:8000/api/tasks?skip=0&limit=10&status=pending"
```

#### Actualizar Tarea
```bash
curl -X PUT "http://localhost:8000/api/tasks/1" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Titulo actualizado",
    "status": "in_progress",
    "priority": 5
  }'
```

#### Procesar Tareas por batch
```bash
curl -X POST "http://localhost:8000/api/tasks/process-batch" \
  -H "Content-Type: application/json" \
  -d '{
    "task_ids": [1, 2, 3]
  }'
```

---

## Modelo de Datos: `tasks`

Cada tarea tiene los siguientes campos:

| Campo | Tipo | Descripcion |
|-------|------|-------------|
| `id` | INT (PK) | Clave primaria, auto incremento |
| `title` | VARCHAR(200) | Titulo de la tarea (requerido) |
| `description` | TEXT | Descripcion de la tarea (opcional) |
| `status` | ENUM | Estado: `pending`, `in_progress`, `completed` |
| `priority` | INT | Prioridad de 1 (baja) a 5 (alta) |
| `created_at` | DATETIME | Timestamp de creacion (UTC) |
| `updated_at` | DATETIME | Timestamp de ultima modificacion (UTC) |

---

## Procesamiento batch

El endpoint `/api/tasks/process-batch` procesa multiples tareas de forma concurrente. Acepta una lista de IDs de tareas, procesa cada una de forma asincrona con un delay de 2 segundos, actualiza el status a `completed` y retorna la cantidad de tareas procesadas exitosamente.

Procesar 3 tareas toma aproximadamente 2 segundos (no 6 segundos) porque se ejecutan en paralelo.

---

## Pruebas

### Ejecutar todas las pruebas

```bash
# Con cobertura
pytest tests/ --cov=app --cov-report=term-missing

# Solo ejecutar pruebas
pytest tests/

# Modo verbose
pytest tests/ -v
```

### Ejecutar pruebas especificas

```bash
# Solo pruebas unitarias
pytest tests/unit/

# Solo pruebas de integración
pytest tests/integration/

# Prueba específica
pytest tests/integration/test_endpoints.py::TestCreateEndpoint
```

**Cobertura actual:** 86% con 32 tests (25 unitarios + 7 de integracion). Todos los endpoints estan cubiertos.

---

## Postman

Incluye una coleccion de Postman para pruebas manuales. Importar desde `postman/Task Management API.postman_collection.json`. Configurar variables de entorno: `base_url` (http://localhost:8000) y `task_id`. La coleccion incluye los 6 endpoints organizados en "CRUD Operations" y "Batch Processing".

---

## Stack Tecnologico

| Área | Tecnología |
|------|------------|
| Lenguaje | Python 3.11+ |
| Framework | FastAPI |
| Base de datos | MySQL 8.0 |
| Driver async | asyncmy |
| ORM | SQLAlchemy 2.0 |
| Validacion | Pydantic |
| Pruebas | pytest, pytest-asyncio |
| Contenedorización | Docker Compose |

---

## Documentacion

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json
