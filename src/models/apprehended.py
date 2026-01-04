"""
Modelo de datos para personas aprehendidas.
"""
from dataclasses import dataclass, field
from datetime import date
from typing import Optional
import uuid


@dataclass
class Apprehended:
    """
    Representa una persona aprehendida.
    
    Incluye clasificación según categorías predefinidas.
    """
    
    # Identificación
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    
    # Datos de la persona
    nombre: str = ""
    edad: Optional[int] = None
    sexo: str = ""
    
    # Clasificación
    clasificacion: str = ""
    
    # Datos del hecho
    delito: str = ""
    fecha: Optional[date] = None
    
    # Campos adicionales
    campos_extra: dict = field(default_factory=dict)
    
    # ═══════════════════════════════════════════════════════════════════════
    # PROPIEDADES
    # ═══════════════════════════════════════════════════════════════════════
    
    @property
    def es_menor(self) -> bool:
        """Indica si es menor de edad."""
        if self.edad is not None:
            return self.edad < 18
        if self.clasificacion:
            return "MENOR" in self.clasificacion.upper()
        return False
    
    @property
    def tiene_antecedentes(self) -> bool:
        """Indica si tiene antecedentes."""
        if self.clasificacion:
            return "ANTECEDENTES" in self.clasificacion.upper()
        return False
    
    @property
    def clasificacion_normalizada(self) -> str:
        """Clasificación normalizada a categorías estándar."""
        if not self.clasificacion:
            # Inferir desde edad si está disponible
            if self.edad is not None:
                if self.edad < 18:
                    return "MENOR_PRIMERIZO"
                else:
                    return "MAYOR_PRIMERIZO"
            return "SIN_CLASIFICAR"
        
        clasif_upper = self.clasificacion.upper()
        
        # Determinar edad
        es_menor = "MENOR" in clasif_upper
        es_mayor = "MAYOR" in clasif_upper or not es_menor
        
        # Determinar antecedentes
        con_antecedentes = "ANTECEDENTES" in clasif_upper or "REINCIDENTE" in clasif_upper
        
        if es_menor:
            return "MENOR_CON_ANTECEDENTES" if con_antecedentes else "MENOR_PRIMERIZO"
        else:
            return "MAYOR_CON_ANTECEDENTES" if con_antecedentes else "MAYOR_PRIMERIZO"
    
    @property
    def sexo_normalizado(self) -> str:
        """Sexo normalizado (M/F)."""
        if not self.sexo:
            return "-"
        s = self.sexo.upper().strip()
        if s in ("M", "MASCULINO", "HOMBRE", "VARON"):
            return "M"
        if s in ("F", "FEMENINO", "MUJER"):
            return "F"
        return self.sexo
    
    # ═══════════════════════════════════════════════════════════════════════
    # MÉTODOS
    # ═══════════════════════════════════════════════════════════════════════
    
    def matches_period(self, start: date, end: date) -> bool:
        """Verifica si el aprehendido está dentro de un período."""
        if self.fecha is None:
            return False
        return start <= self.fecha <= end
    
    def to_dict(self) -> dict:
        """Convierte el registro a diccionario."""
        return {
            "id": self.id,
            "nombre": self.nombre,
            "edad": self.edad,
            "sexo": self.sexo_normalizado,
            "clasificacion": self.clasificacion,
            "clasificacion_normalizada": self.clasificacion_normalizada,
            "delito": self.delito,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "es_menor": self.es_menor,
            "tiene_antecedentes": self.tiene_antecedentes,
        }
    
    def to_report_row(self) -> dict:
        """Genera una fila para el cuadro de aprehendidos del reporte."""
        return {
            "Nombre/Alias": self.nombre or "NN",
            "Clasificación": self.clasificacion_normalizada.replace("_", " "),
            "Delito": self.delito,
            "Fecha": self.fecha.strftime("%d/%m/%Y") if self.fecha else "-",
            "Edad": str(self.edad) if self.edad else "-",
            "Sexo": self.sexo_normalizado,
        }
    
    def __str__(self) -> str:
        nombre = self.nombre or "NN"
        return f"{nombre} - {self.clasificacion_normalizada} - {self.delito}"
    
    def __repr__(self) -> str:
        return f"Apprehended(nombre={self.nombre!r}, clasificacion={self.clasificacion!r})"
