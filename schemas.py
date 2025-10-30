from sqlmodel import SQLModel
from typing import Optional, List
from pydantic import constr, condecimal

class EmpleadoCreate(SQLModel):
    nombre: constr(min_length=2, max_length=100)
    especialidad: constr(min_length=2, max_length=80)
    salario: condecimal(gt=0)
    estado: constr(min_length=3, max_length=20)

class EmpleadoUpdate(SQLModel):
    nombre: Optional[str]
    especialidad: Optional[str]
    salario: Optional[float]
    estado: Optional[str]

class EmpleadoRead(SQLModel):
    id: int
    nombre: str
    especialidad: str
    salario: float
    estado: str


class ProyectoCreate(SQLModel):
    nombre: constr(min_length=2, max_length=120)
    descripcion: Optional[str] = None
    presupuesto: condecimal(gt=0)
    estado: constr(min_length=3, max_length=20)
    gerente_id: int

class ProyectoUpdate(SQLModel):
    nombre: Optional[str]
    descripcion: Optional[str]
    presupuesto: Optional[float]
    estado: Optional[str]
    gerente_id: Optional[int]

class ProyectoRead(SQLModel):
    id: int
    nombre: str
    descripcion: Optional[str]
    presupuesto: float
    estado: str
    gerente_id: Optional[int]

class EmpleadoSimple(SQLModel):
    id: int
    nombre: str
    especialidad: str
    estado: str

class ProyectoSimple(SQLModel):
    id: int
    nombre: str
    presupuesto: float

class EmpleadoConProyectos(EmpleadoRead):
    proyectos: List[ProyectoSimple] = []

class ProyectoConGerenteYEmpleados(ProyectoRead):
    gerente: Optional[EmpleadoSimple] = None
    empleados: List[EmpleadoSimple] = []
