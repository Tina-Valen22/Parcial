from typing import List, Optional
from sqlmodel import SQLModel, Field
from pydantic import validator, condecimal, constr

class EmpleadoCreate(SQLModel):
    nombre: constr(min_length=2, max_length=100)
    especialidad: constr(min_length=2, max_length=80)
    salario: condecimal(gt=0)
    estado: constr(min_length=3, max_length=20)

    @validator("estado")
    def estado_ok(cls, v):
        return v.lower()
    
class EmpleadoUpdate(SQLModel):
    nombre: Optional[constr(min_length=2, max_length=100)]
    especialidad: Optional[constr(min_length=2, max_length=80)]
    salario: Optional[condecimal(gt=0)]
    estado: Optional[constr(min_length=3, max_length=20)]

    @validator("estado")
    def estado_ok(cls, v):
        return v.lower()

class EmpleadoRead(SQLModel):
    id: int
    nombre: str
    especialidad: str
    salario: float
    estado: str
