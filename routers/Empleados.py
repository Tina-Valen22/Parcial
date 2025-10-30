from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlmodel import select, Session
from database import get_session
from models import Empleado, Proyecto
from schemas import EmpleadoCreate, EmpleadoRead, EmpleadoUpdate, EmpleadoConProyectos, ProyectoSimple

router = APIRouter(prefix="/empleados", tags=["Empleados"])

@router.post("/", response_model=EmpleadoRead, status_code=201)
def crear_empleado(payload: EmpleadoCreate, session: Session = Depends(get_session)):
    empleado = Empleado.from_orm(payload)
    session.add(empleado)
    session.commit()
    session.refresh(empleado)
    return empleado


@router.get("/", response_model=List[EmpleadoRead])
def listar_empleados(
    especialidad: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    nombre: Optional[str] = Query(None),
    session: Session = Depends(get_session)
):
    statement = select(Empleado)
    if especialidad:
        statement = statement.where(Empleado.especialidad == especialidad)
    if estado:
        statement = statement.where(Empleado.estado == estado.lower())
    if nombre:
        statement = statement.where(Empleado.nombre.contains(nombre))
    empleados = session.exec(statement).all()
    return empleados


@router.get("/buscar/{nombre_empleado}", response_model=EmpleadoRead)
def buscar_empleado_por_nombre(nombre_empleado: str, session: Session = Depends(get_session)):

    empleado = session.exec(select(Empleado).where(Empleado.nombre == nombre_empleado)).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado
