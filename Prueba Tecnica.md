# Prueba Técnica - Desarrollador Backend Python

---

## Objetivo

Desarrollar una **API REST** para gestión de tareas usando FastAPI, MySQL y Docker.

---

## Stack Requerido

- Python 3.11+
- FastAPI
- MySQL 8.0
- Docker / Docker Compose
- pytest
- aiomysql o asyncmy

---

## Modelo de Datos

### Tabla `tasks`

| Campo | Tipo | Descripción |
|-------|------|-------------|
| id | INT | PK, Auto Increment |
| title | VARCHAR(200) | Requerido |
| description | TEXT | Opcional |
| status | ENUM | 'pending', 'in_progress', 'completed' |
| priority | INT | 1 (baja) a 5 (alta) |
| created_at | DATETIME | Fecha creación |
| updated_at | DATETIME | Fecha actualización |

---

## Endpoints Requeridos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/tasks` | Crear tarea |
| GET | `/api/tasks` | Listar tareas (con paginación y filtro por status) |
| GET | `/api/tasks/{id}` | Obtener tarea por ID |
| PUT | `/api/tasks/{id}` | Actualizar tarea |
| DELETE | `/api/tasks/{id}` | Eliminar tarea |
| POST | `/api/tasks/process-batch` | **Procesar múltiples tareas de forma asíncrona** |

### Endpoint Asíncrono

`POST /api/tasks/process-batch` debe:
- Recibir una lista de IDs de tareas
- Simular un procesamiento de 2 segundos por tarea (usar `asyncio.sleep`)
- Cambiar el status a `completed`
- Ejecutarse de forma concurrente (no secuencial)
- Retornar cuántas tareas fueron procesadas

---

## Requisitos

### 1. FastAPI
- Documentación automática en `/docs`
- Schemas Pydantic con validación
- Tipado correcto en todos los endpoints

### 2. Base de Datos
- Conexiones asíncronas a MySQL
- Pool de conexiones
- Script SQL de inicialización incluido

### 3. Pruebas Unitarias
- Mínimo 5 tests con pytest
- Incluir test del endpoint asíncrono
- Usar pytest-asyncio

### 4. Docker
- `Dockerfile` para la API
- `docker-compose.yml` con servicios: api y mysql
- Variables de entorno en archivo `.env`
- `docker-compose up` debe levantar todo funcional

---

## Entregables

```
/
├── app/
│   ├── main.py
│   └── ...
├── tests/
│   └── ...
├── scripts/
│   └── init.sql
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── .env.example
└── README.md
```

---

## Criterios de Evaluación

| Criterio | Peso |
|----------|------|
| Funcionalidad completa | 25% |
| Código limpio (PEP8, tipado) | 20% |
| Pruebas unitarias | 20% |
| Uso correcto de async/await | 15% |
| Docker funcional | 10% |
| Documentación Swagger | 10% |

---