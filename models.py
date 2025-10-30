from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship, Column, Table
from pydantic import validator, condecimal, constr
from sqlalchemy import ForeignKey, UniqueConstraint

proyecto_empleado = Table(
    "proyecto_empleado",
    SQLModel.metadata,
    Column("proyecto_id", ForeignKey("proyecto.id"), primary_key=True),
    Column("empleado_id", ForeignKey("empleado.id"), primary_key=True),
)

class EmpleadoBase(SQLModel):
    nombre: constr(min_length=2, max_length=100)
    especialidad: constr(min_length=2, max_length=80)
    salario: condecimal(gt=0)
    estado: constr(min_length=3, max_length=20)

class Empleado(EmpleadoBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    proyectos: List["Proyecto"] = Relationship(back_populates="empleados", link_model=proyecto_empleado)

@validator("estado")
def validar_estado(cls, v):
    estados = {"activo", "inactivo", "suspendido"}
    if v.lower() not in estados:
        raise ValueError(f"Estado inválido. Debe ser uno de {estados}")
    return v.lower()

class ProyectoBase(SQLModel):
    nombre: constr(min_length=2, max_length=120)
    descripcion: Optional[str] = None
    presupuesto: condecimal(gt=0)
    estado: constr(min_length=3, max_length=20)
