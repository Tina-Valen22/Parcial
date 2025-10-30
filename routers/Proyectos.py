from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select, Session
from database import get_session
from models import Proyecto, Empleado
from schemas import ProyectoCreate, ProyectoRead, ProyectoConGerenteYEmpleados
from pydantic import BaseModel

router = APIRouter(prefix="/proyectos", tags=["Proyectos"])

# Crear proyecto con gerente
@router.post("/", response_model=ProyectoRead)
def crear_proyecto(payload: ProyectoCreate, session: Session = Depends(get_session)):
    existente = session.exec(select(Proyecto).where(Proyecto.nombre == payload.nombre)).first()
    if existente:
        raise HTTPException(409, "Ya existe un proyecto con este nombre")

    gerente = session.get(Empleado, payload.gerente_id)
    if not gerente or gerente.estado != "activo":
        raise HTTPException(400, "Gerente no válido o inactivo")

    proyecto = Proyecto.from_orm(payload)
    session.add(proyecto)
    session.commit()
    session.refresh(proyecto)
    return proyecto


# Listar proyectos (filtros por estado, presupuesto fijo)
@router.get("/", response_model=list[ProyectoRead])
def listar_proyectos(
    estado: str | None = None,
    presupuesto: float | None = None,
    session: Session = Depends(get_session)
):
    q = select(Proyecto)
    if estado:
        q = q.where(Proyecto.estado == estado.lower())
    if presupuesto:
        q = q.where(Proyecto.presupuesto == presupuesto)
    return session.exec(q).all()


# Obtener proyecto con gerente y empleados
@router.get("/{id}", response_model=ProyectoConGerenteYEmpleados)
def obtener_proyecto(id: int, session: Session = Depends(get_session)):
    proyecto = session.get(Proyecto, id)
    if not proyecto:
        raise HTTPException(404, "Proyecto no encontrado")
    return proyecto


# Buscar proyecto por nombre
@router.get("/buscar/{nombre}", response_model=ProyectoRead)
def buscar_proyecto(nombre: str, session: Session = Depends(get_session)):
    p = session.exec(select(Proyecto).where(Proyecto.nombre == nombre)).first()
    if not p:
        raise HTTPException(404, "Proyecto no encontrado")
    return p


# signar empleado a proyecto
class AsignarEmpleado(BaseModel):
    empleado_id: int

@router.post("/{id}/asignar")
def asignar_empleado(id: int, datos: AsignarEmpleado, session: Session = Depends(get_session)):
    proyecto = session.get(Proyecto, id)
    empleado = session.get(Empleado, datos.empleado_id)

    if not proyecto or not empleado:
        raise HTTPException(404, "Proyecto o empleado no encontrado")
    if empleado.estado != "activo":
        raise HTTPException(400, "Empleado inactivo")
    if empleado in proyecto.empleados:
        raise HTTPException(409, "Empleado ya asignado a este proyecto")

    proyecto.empleados.append(empleado)
    session.add(proyecto)
    session.commit()
    return {"detail": "Empleado asignado correctamente"}


# Desasigna empleado
@router.post("/{id}/desasignar")
def desasignar_empleado(id: int, datos: AsignarEmpleado, session: Session = Depends(get_session)):
    proyecto = session.get(Proyecto, id)
    if not proyecto:
        raise HTTPException(404, "Proyecto no encontrado")

    proyecto.empleados = [e for e in proyecto.empleados if e.id != datos.empleado_id]
    session.commit()
    return {"detail": "Empleado desasignado correctamente"}


# Elimina proyecto (no borra empleados)
@router.delete("/{id}")
def eliminar_proyecto(id: int, session: Session = Depends(get_session)):
    p = session.get(Proyecto, id)
    if not p:
        raise HTTPException(404, "Proyecto no encontrado")
    p.empleados = []  # Limpia relaciones
    session.delete(p)
    session.commit()
    return {"detail": "Proyecto eliminado correctamente"}

#Listar empleados de un proyecto
@router.get("/{id}/empleados", response_model=list[dict])
def empleados_de_proyecto(id: int, session: Session = Depends(get_session)):
    proyecto = session.get(Proyecto, id)
    if not proyecto:
        raise HTTPException(404, "Proyecto no encontrado")

    empleados = [
        {"id": e.id, "nombre": e.nombre, "especialidad": e.especialidad, "estado": e.estado}
        for e in proyecto.empleados
    ]
    return empleados
