from fastapi import APIRouter, Depends, HTTPException, Query, Body
from typing import List, Optional
from sqlmodel import select, Session
from database import get_session
from models import Proyecto, Empleado
from schemas import ProyectoCreate, ProyectoRead, ProyectoUpdate, ProyectoConGerenteYEmpleados, EmpleadoSimple
from pydantic import BaseModel

router = APIRouter(prefix="/proyectos", tags=["Proyectos"])

@router.post("/", response_model=ProyectoRead, status_code=201)
def crear_proyecto(payload: ProyectoCreate, session: Session = Depends(get_session)):
    existing = session.exec(select(Proyecto).where(Proyecto.nombre == payload.nombre)).first()
    if existing:
        raise HTTPException(status_code=409, detail="Ya existe un proyecto con ese nombre")

    gerente = session.get(Empleado, payload.gerente_id)
    if not gerente:
        raise HTTPException(status_code=400, detail="Gerente indicado no existe")
    if gerente.estado != "activo":
        raise HTTPException(status_code=400, detail="El gerente debe estar en estado 'activo'")

    proyecto = Proyecto.from_orm(payload)
    session.add(proyecto)
    session.commit()
    session.refresh(proyecto)
    return proyecto

@router.get("/", response_model=List[ProyectoRead])
def listar_proyectos(
    estado: Optional[str] = Query(None),
    presupuesto: Optional[float] = Query(None),
    nombre: Optional[str] = Query(None),
    session: Session = Depends(get_session)
):
    statement = select(Proyecto)

    if estado:
        statement = statement.where(Proyecto.estado == estado.lower())
    if presupuesto is not None:
        statement = statement.where(Proyecto.presupuesto == presupuesto)
    if nombre:
        statement = statement.where(Proyecto.nombre.contains(nombre))

    proyectos = session.exec(statement).all()
    return proyectos


@router.get("/buscar/{nombre_proyecto}", response_model=ProyectoRead)
def buscar_proyecto_por_nombre(nombre_proyecto: str, session: Session = Depends(get_session)):
    """
    Busca un proyecto por nombre exacto (sin usar ID).
    """
    proyecto = session.exec(select(Proyecto).where(Proyecto.nombre == nombre_proyecto)).first()
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return proyecto


@router.get("/{proyecto_id}", response_model=ProyectoConGerenteYEmpleados)
def obtener_proyecto_con_detalles(proyecto_id: int, session: Session = Depends(get_session)):
    """
    Obtiene proyecto con su gerente y empleados asignados.
    """
    proyecto = session.get(Proyecto, proyecto_id)
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    gerente = None
    if proyecto.gerente_id:
        g = session.get(Empleado, proyecto.gerente_id)
        if g:
            gerente = EmpleadoSimple(id=g.id, nombre=g.nombre, especialidad=g.especialidad, estado=g.estado)

    empleados_simple = [
        EmpleadoSimple(id=e.id, nombre=e.nombre, especialidad=e.especialidad, estado=e.estado)
        for e in proyecto.empleados
    ]

    return ProyectoConGerenteYEmpleados(
        id=proyecto.id,
        nombre=proyecto.nombre,
        descripcion=proyecto.descripcion,
        presupuesto=float(proyecto.presupuesto),
        estado=proyecto.estado,
        gerente_id=proyecto.gerente_id,
        gerente=gerente,
        empleados=empleados_simple
    )


@router.put("/{proyecto_id}", response_model=ProyectoRead)
def actualizar_proyecto(proyecto_id: int, payload: ProyectoUpdate, session: Session = Depends(get_session)):
    proyecto = session.get(Proyecto, proyecto_id)
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    data = payload.dict(exclude_unset=True)
    if "nombre" in data:
        otro = session.exec(
            select(Proyecto).where(Proyecto.nombre == data["nombre"], Proyecto.id != proyecto_id)
        ).first()
        if otro:
            raise HTTPException(status_code=409, detail="Otro proyecto con ese nombre ya existe")
    if "gerente_id" in data:
        gerente = session.get(Empleado, data["gerente_id"])
        if not gerente:
            raise HTTPException(status_code=400, detail="Gerente indicado no existe")
        if gerente.estado != "activo":
            raise HTTPException(status_code=400, detail="El gerente debe estar en estado 'activo'")

    for k, v in data.items():
        setattr(proyecto, k, v)
    session.add(proyecto)
    session.commit()
    session.refresh(proyecto)
    return proyecto


@router.delete("/{proyecto_id}", status_code=200)
def eliminar_proyecto(proyecto_id: int, session: Session = Depends(get_session)):
    proyecto = session.get(Proyecto, proyecto_id)
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    proyecto.empleados = []
    session.delete(proyecto)
    session.commit()
    return {"detail": "Proyecto eliminado correctamente"}


class AsignarEmpleadoBody(BaseModel):
    empleado_id: int


@router.post("/{proyecto_id}/asignar", status_code=201)
def asignar_empleado(proyecto_id: int, body: AsignarEmpleadoBody, session: Session = Depends(get_session)):
    proyecto = session.get(Proyecto, proyecto_id)
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    empleado = session.get(Empleado, body.empleado_id)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    if empleado.estado != "activo":
        raise HTTPException(status_code=400, detail="Empleado no está en estado 'activo'")
    if any(e.id == empleado.id for e in proyecto.empleados):
        raise HTTPException(status_code=409, detail="Empleado ya asignado al proyecto")

    proyecto.empleados.append(empleado)
    session.add(proyecto)
    session.commit()
    session.refresh(proyecto)
    return {"detail": "Empleado asignado correctamente"}


@router.post("/{proyecto_id}/desasignar", status_code=200)
def desasignar_empleado(proyecto_id: int, body: AsignarEmpleadoBody, session: Session = Depends(get_session)):
    proyecto = session.get(Proyecto, proyecto_id)
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    empleado = session.get(Empleado, body.empleado_id)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    if not any(e.id == empleado.id for e in proyecto.empleados):
        raise HTTPException(status_code=400, detail="Empleado no está asignado a este proyecto")

    proyecto.empleados = [e for e in proyecto.empleados if e.id != empleado.id]
    session.add(proyecto)
    session.commit()
    return {"detail": "Empleado desasignado correctamente"}


@router.get("/empleado/{empleado_id}", response_model=List[ProyectoRead])
def proyectos_de_empleado(empleado_id: int, session: Session = Depends(get_session)):
    empleado = session.get(Empleado, empleado_id)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado.proyectos


@router.get("/{proyecto_id}/empleados", response_model=List[EmpleadoSimple])
def empleados_de_proyecto(proyecto_id: int, session: Session = Depends(get_session)):
    proyecto = session.get(Proyecto, proyecto_id)
    if not proyecto:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    return [
        EmpleadoSimple(id=e.id, nombre=e.nombre, especialidad=e.especialidad, estado=e.estado)
        for e in proyecto.empleados
    ]