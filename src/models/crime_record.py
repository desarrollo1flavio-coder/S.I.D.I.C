"""
Modelo de datos para un hecho delictual.
"""
from dataclasses import dataclass, field
from datetime import date, time, datetime
from typing import Optional, Tuple, Any
import uuid

from ..utils.constants import (
    FranjaHoraria,
    CategoriaDelito,
    DELITOS_ROBO,
    DELITOS_HURTO,
    DELITOS_ROBO_AGRAVADO,
)
from ..utils.date_utils import get_franja_horaria, get_dia_semana


@dataclass
class CrimeRecord:
    """
    Representa un hecho delictual individual.
    
    Contiene toda la información extraída de un registro del shapefile
    de hechos delictuales.
    """
    
    # Identificación
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    
    # Datos temporales
    fecha: Optional[date] = None
    hora: Optional[time] = None
    
    # Clasificación del delito
    delito: str = ""
    ambito: str = ""
    
    # Medios utilizados
    movilidad: str = ""
    arma_medio: str = ""
    
    # Estado
    esclarecido: str = ""
    
    # Ubicación
    direccion: str = ""
    coordenadas: Optional[Tuple[float, float]] = None  # (lon, lat)
    
    # Geometría original (para exportación)
    geometry: Any = None
    
    # Campos adicionales del shapefile
    campos_extra: dict = field(default_factory=dict)
    
    # ═══════════════════════════════════════════════════════════════════════
    # PROPIEDADES CALCULADAS
    # ═══════════════════════════════════════════════════════════════════════
    
    @property
    def datetime(self) -> Optional[datetime]:
        """Combina fecha y hora en un datetime."""
        if self.fecha and self.hora:
            return datetime.combine(self.fecha, self.hora)
        return None
    
    @property
    def dia_semana(self) -> Optional[str]:
        """Nombre del día de la semana."""
        return get_dia_semana(self.fecha)
    
    @property
    def franja_horaria(self) -> Optional[FranjaHoraria]:
        """Franja horaria del hecho."""
        return get_franja_horaria(self.hora)
    
    @property
    def franja_horaria_nombre(self) -> str:
        """Nombre de la franja horaria con rango."""
        franja = self.franja_horaria
        return franja.display_name if franja else "#NO_CONSTA"
    
    @property
    def categoria(self) -> CategoriaDelito:
        """Categoría del delito (ROBO, HURTO, OTROS)."""
        delito_upper = self.delito.upper()
        
        for patron in DELITOS_ROBO:
            if patron in delito_upper or delito_upper in patron:
                return CategoriaDelito.ROBO
        
        for patron in DELITOS_HURTO:
            if patron in delito_upper or delito_upper in patron:
                return CategoriaDelito.HURTO
        
        return CategoriaDelito.OTROS
    
    @property
    def es_robo_agravado(self) -> bool:
        """Indica si el delito es un robo agravado."""
        delito_upper = self.delito.upper()
        return any(
            patron in delito_upper or delito_upper in patron
            for patron in DELITOS_ROBO_AGRAVADO
        )
    
    @property
    def es_esclarecido(self) -> bool:
        """Indica si el hecho fue esclarecido (total o parcialmente)."""
        if not self.esclarecido:
            return False
        escl_upper = self.esclarecido.upper()
        return "SI" in escl_upper or "PARCIAL" in escl_upper or "TOTAL" in escl_upper
    
    @property
    def tipo_esclarecimiento(self) -> str:
        """Tipo de esclarecimiento (TOTAL, PARCIAL, NO)."""
        if not self.esclarecido:
            return "NO_ESCLARECIDO"
        escl_upper = self.esclarecido.upper()
        if "TOTAL" in escl_upper:
            return "ESCLARECIDO_TOTALMENTE"
        if "PARCIAL" in escl_upper:
            return "ESCLARECIDO_PARCIALMENTE"
        if "SI" in escl_upper:
            return "ESCLARECIDO"
        return "NO_ESCLARECIDO"
    
    # ═══════════════════════════════════════════════════════════════════════
    # MÉTODOS
    # ═══════════════════════════════════════════════════════════════════════
    
    def matches_period(self, start: date, end: date) -> bool:
        """Verifica si el hecho está dentro de un período."""
        if self.fecha is None:
            return False
        return start <= self.fecha <= end
    
    def to_dict(self) -> dict:
        """Convierte el registro a diccionario."""
        return {
            "id": self.id,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "hora": self.hora.strftime("%H:%M") if self.hora else None,
            "dia_semana": self.dia_semana,
            "franja_horaria": self.franja_horaria_nombre,
            "delito": self.delito,
            "categoria": self.categoria.value,
            "ambito": self.ambito,
            "movilidad": self.movilidad,
            "arma_medio": self.arma_medio,
            "esclarecido": self.esclarecido,
            "direccion": self.direccion,
            "coordenadas": self.coordenadas,
            "es_robo_agravado": self.es_robo_agravado,
        }
    
    def __str__(self) -> str:
        fecha_str = self.fecha.strftime("%d/%m/%Y") if self.fecha else "S/F"
        hora_str = self.hora.strftime("%H:%M") if self.hora else "S/H"
        return f"[{self.id}] {self.delito} - {fecha_str} {hora_str} - {self.direccion}"
    
    def __repr__(self) -> str:
        return f"CrimeRecord(id={self.id!r}, delito={self.delito!r}, fecha={self.fecha})"
