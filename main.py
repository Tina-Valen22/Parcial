from fastapi import FastAPI
from database import init_db
from routers import empleados, proyectos

app = FastAPI(
    title="Sistema de Gestión de Proyectos",
    version="1.0.0",
    description="API que gestiona empleados, proyectos y asignaciones."
)

@app.on_event("startup")
def startup():
    init_db()

app.include_router(empleados.router)
app.include_router(proyectos.router)
