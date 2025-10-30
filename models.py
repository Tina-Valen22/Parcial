from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from pydantic import validator, condecimal, constr

# Tabla intermedia (Relación N:M)
class ProyectoEmpleadoLink(SQLModel, table=True):
    proyecto_id: Optional[int] = Field(default=None, foreign_key="proyecto.id", primary_key=True)
    empleado_id: Optional[int] = Field(default=None, foreign_key="empleado.id", primary_key=True)

# Modelo de Empleado
class EmpleadoBase(SQLModel):
    nombre: constr(min_length=2, max_length=100)
    especialidad: constr(min_length=2, max_length=80)
    salario: condecimal(gt=0)
    estado: constr(min_length=3, max_length=20)


class Empleado(EmpleadoBase, table=True):
    __tablename__ = "empleado"

    id: Optional[int] = Field(default=None, primary_key=True)
    proyectos: List["Proyecto"] = Relationship(
        back_populates="empleados",
        link_model=ProyectoEmpleadoLink
    )

    @validator("estado")
    def validar_estado(cls, v):
        estados = {"activo", "inactivo", "suspendido"}
        if v.lower() not in estados:
            raise ValueError(f"Estado inválido. Debe ser uno de {estados}")
        return v.lower()

# Modelo de Proyecto
class ProyectoBase(SQLModel):
    nombre: constr(min_length=2, max_length=120)
    descripcion: Optional[constr(max_length=500)] = None
    presupuesto: condecimal(gt=0)
    estado: constr(min_length=3, max_length=20)


class Proyecto(ProyectoBase, table=True):
    __tablename__ = "proyecto"

    id: Optional[int] = Field(default=None, primary_key=True)
    gerente_id: Optional[int] = Field(default=None, foreign_key="empleado.id")

    gerente: Optional[Empleado] = Relationship()
    empleados: List[Empleado] = Relationship(
        back_populates="proyectos",
        link_model=ProyectoEmpleadoLink
    )

    @validator("estado")
    def validar_estado(cls, v):
        estados = {"planificado", "en_progreso", "finalizado", "cancelado"}
        if v.lower() not in estados:
            raise ValueError(f"Estado inválido. Debe ser uno de {estados}")
        return v.lower()
