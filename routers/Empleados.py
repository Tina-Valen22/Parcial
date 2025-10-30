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