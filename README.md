# Sistema de Gestión de Proyectos

Proyecto desarrollado con **FastAPI + SQLModel + Pydantic**, para la materia **Desarrollo de Software**.  
Permite gestionar **empleados y proyectos** dentro de una empresa consultora, cumpliendo todas las reglas de negocio y requerimientos del parcial.

---

## Descripción General

El sistema permite:
- Registrar **empleados** (nombre, especialidad, salario, estado).
- Registrar **proyectos** (nombre, descripción, presupuesto, estado, gerente).
- **Asignar y desasignar empleados** a proyectos.
- Consultar:
  - Empleados de un proyecto.
  - Proyectos de un empleado.
- Buscar empleados y proyectos **por nombre** (sin usar el ID).
- Filtrar por estado, especialidad o presupuesto exacto.
- Respetar las reglas de negocio establecidas.

---

## Tecnologías Utilizadas

- **FastAPI** → Framework principal para la API.
- **SQLModel** → ORM que combina SQLAlchemy + Pydantic.
- **SQLite** → Base de datos ligera (local).
- **Pydantic** → Validación de datos de entrada/salida.
- **Python-dotenv** → Manejo de variables de entorno.
- **Uvicorn** → Servidor ASGI para ejecutar la app.

---

## Estructura del Proyecto

proyectos_app/
│
├── main.py
├── database.py
├── models.py
├── schemas.py
├── routers/
│ ├── empleados.py
│ └── proyectos.py
├── requirements.txt
├── .gitignore
├── .env.example
└── README.md