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

