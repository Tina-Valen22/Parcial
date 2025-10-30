from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select, Session
from typing import List, Optional
from database import get_session
from models import Empleado, Proyecto
from schemas import EmpleadoCreate, EmpleadoUpdate, EmpleadoRead, EmpleadoConProyectos, ProyectoSimple

router = APIRouter(prefix="/empleados", tags=["Empleados"])

@router.post("/", response_model=EmpleadoRead, status_code=201)
def crear_empleado(data: EmpleadoCreate, session: Session = Depends(get_session)):
    empleado = Empleado.from_orm(data)
    session.add(empleado)
    session.commit()
    session.refresh(empleado)
    return empleado

@router.get("/", response_model=List[EmpleadoRead])
def listar_empleados(
    nombre: Optional[str] = Query(None),
    especialidad: Optional[str] = Query(None),
    estado: Optional[str] = Query(None),
    session: Session = Depends(get_session)
):
    query = select(Empleado)
    if nombre:
        query = query.where(Empleado.nombre.contains(nombre))
    if especialidad:
        query = query.where(Empleado.especialidad == especialidad)
    if estado:
        query = query.where(Empleado.estado == estado.lower())
    return session.exec(query).all()

@router.get("/buscar/{nombre_empleado}", response_model=EmpleadoRead)
def buscar_por_nombre(nombre_empleado: str, session: Session = Depends(get_session)):
    empleado = session.exec(select(Empleado).where(Empleado.nombre == nombre_empleado)).first()
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    return empleado

@router.get("/{empleado_id}", response_model=EmpleadoConProyectos)
def obtener_empleado_con_proyectos(empleado_id: int, session: Session = Depends(get_session)):
    empleado = session.get(Empleado, empleado_id)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    proyectos = [ProyectoSimple(id=p.id, nombre=p.nombre, presupuesto=float(p.presupuesto)) for p in empleado.proyectos]
    return EmpleadoConProyectos(**empleado.dict(), proyectos=proyectos)

@router.put("/{empleado_id}", response_model=EmpleadoRead)
def actualizar_empleado(empleado_id: int, data: EmpleadoUpdate, session: Session = Depends(get_session)):
    empleado = session.get(Empleado, empleado_id)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")
    for k, v in data.dict(exclude_unset=True).items():
        setattr(empleado, k, v)
    session.add(empleado)
    session.commit()
    session.refresh(empleado)
    return empleado

@router.delete("/{empleado_id}")
def eliminar_empleado(empleado_id: int, session: Session = Depends(get_session)):
    empleado = session.get(Empleado, empleado_id)
    if not empleado:
        raise HTTPException(status_code=404, detail="Empleado no encontrado")

    proyectos_gerenciados = session.exec(select(Proyecto).where(Proyecto.gerente_id == empleado_id)).all()
    if proyectos_gerenciados:
        raise HTTPException(status_code=409, detail="Empleado es gerente de proyectos activos.")

    empleado.proyectos = []
    session.delete(empleado)
    session.commit()
    return {"detail": "Empleado eliminado correctamente"}