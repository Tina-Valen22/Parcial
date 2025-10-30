# routers/empleados.py
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, Session
from database import get_session
from models import Empleado, Proyecto
from schemas import EmpleadoCreate, EmpleadoRead, EmpleadoConProyectos
from pydantic import BaseModel

router = APIRouter(prefix="/empleados", tags=["Empleados"])

# Crear emplead
@router.post("/", response_model=EmpleadoRead)
def crear_empleado(payload: EmpleadoCreate, session: Session = Depends(get_session)):
    empleado = Empleado.from_orm(payload)
    session.add(empleado)
    session.commit()
    session.refresh(empleado)
    return empleado


# Listar emmpleados (con filtros)
@router.get("/", response_model=list[EmpleadoRead])
def listar_empleados(
    especialidad: str | None = None,
    estado: str | None = None,
    session: Session = Depends(get_session)
):
    q = select(Empleado)
    if especialidad:
        q = q.where(Empleado.especialidad.contains(especialidad))
    if estado:
        q = q.where(Empleado.estado == estado.lower())
    return session.exec(q).all()


# Buscar empleado por nombre
@router.get("/buscar/{nombre_empleado}", response_model=EmpleadoRead)
def buscar_empleado(nombre_empleado: str, session: Session = Depends(get_session)):
    emp = session.exec(select(Empleado).where(Empleado.nombre == nombre_empleado)).first()
    if not emp:
        raise HTTPException(404, "Empleado no encontrado")
    return emp


# Obtener empleado y sus proyectos
@router.get("/{id}", response_model=EmpleadoConProyectos)
def obtener_empleado(id: int, session: Session = Depends(get_session)):
    emp = session.get(Empleado, id)
    if not emp:
        raise HTTPException(404, "Empleado no encontrado")
    return emp


# Actualizar empleado
class EmpleadoUpdate(BaseModel):
    nombre: str | None = None
    especialidad: str | None = None
    salario: float | None = None
    estado: str | None = None

@router.put("/{id}", response_model=EmpleadoRead)
def actualizar_empleado(id: int, datos: EmpleadoUpdate, session: Session = Depends(get_session)):
    empleado = session.get(Empleado, id)
    if not empleado:
        raise HTTPException(404, "Empleado no encontrado")

    for campo, valor in datos.dict(exclude_unset=True).items():
        setattr(empleado, campo, valor)

    session.add(empleado)
    session.commit()
    session.refresh(empleado)
    return empleado


# Eliminar empleado (con validación de proyectos)
@router.delete("/{id}")
def eliminar_empleado(id: int, session: Session = Depends(get_session)):
    emp = session.get(Empleado, id)
    if not emp:
        raise HTTPException(404, "Empleado no encontrado")

    proyectos_gerenciados = session.exec(select(Proyecto).where(Proyecto.gerente_id == id)).all()
    if proyectos_gerenciados:
        raise HTTPException(
            409,
            "Este empleado es gerente de proyectos, reasigne o elimine esos proyectos antes de borrarlo."
        )

    emp.proyectos = []  # Desasigna de todos los proyectos
    session.delete(emp)
    session.commit()
    return {"detail": "Empleado eliminado correctamente"}

# Listar proyectos de un empleado
@router.get("/{id}/proyectos", response_model=list[dict])
def proyectos_de_empleado(id: int, session: Session = Depends(get_session)):
    empleado = session.get(Empleado, id)
    if not empleado:
        raise HTTPException(404, "Empleado no encontrado")

    proyectos = [
        {"id": p.id, "nombre": p.nombre, "presupuesto": p.presupuesto, "estado": p.estado}
        for p in empleado.proyectos
    ]
    return proyectos
