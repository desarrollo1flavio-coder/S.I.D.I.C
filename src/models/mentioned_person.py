"""
Modelo de datos para personas mencionadas ("Un tal...").
"""
from dataclasses import dataclass, field
from datetime import date, time
from typing import Optional
import uuid


@dataclass
class MentionedPerson:
    """
    Representa una persona mencionada como posible autor material.
    
    Estos son los "Un tal..." que aparecen en las denuncias pero
    que no fueron aprehendidos.
    """
    
    # Identificación
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    
    # Datos de la persona
    alias: str = ""
    datos_filiatorios: str = ""
    
    # Datos del hecho asociado
    delito: str = ""
    fecha: Optional[date] = None
    hora: Optional[time] = None
    direccion_hecho: str = ""
    
    # Campos adicionales
    campos_extra: dict = field(default_factory=dict)
    
    # ═══════════════════════════════════════════════════════════════════════
    # PROPIEDADES
    # ═══════════════════════════════════════════════════════════════════════
    
    @property
    def fecha_hora_str(self) -> str:
        """Fecha y hora formateadas."""
        partes = []
        if self.fecha:
            partes.append(self.fecha.strftime("%d/%m/%Y"))
        if self.hora:
            partes.append(self.hora.strftime("%H:%M"))
        return " ".join(partes) if partes else "Sin fecha/hora"
    
    @property
    def alias_formateado(self) -> str:
        """Alias con comillas y formato 'UN TAL'."""
        if not self.alias:
            return "SIN IDENTIFICAR"
        return f'UN TAL "{self.alias.upper()}"'
    
    # ═══════════════════════════════════════════════════════════════════════
    # MÉTODOS
    # ═══════════════════════════════════════════════════════════════════════
    
    def matches_period(self, start: date, end: date) -> bool:
        """Verifica si el mencionado está dentro de un período."""
        if self.fecha is None:
            return False
        return start <= self.fecha <= end
    
    def to_dict(self) -> dict:
        """Convierte el registro a diccionario."""
        return {
            "id": self.id,
            "alias": self.alias,
            "alias_formateado": self.alias_formateado,
            "datos_filiatorios": self.datos_filiatorios,
            "delito": self.delito,
            "fecha": self.fecha.isoformat() if self.fecha else None,
            "hora": self.hora.strftime("%H:%M") if self.hora else None,
            "direccion_hecho": self.direccion_hecho,
        }
    
    def to_report_row(self) -> dict:
        """Genera una fila para el cuadro de mencionados del reporte."""
        return {
            "Alias": self.alias_formateado,
            "Delito": self.delito,
            "Dirección del Hecho": self.direccion_hecho,
            "Fecha": self.fecha.strftime("%d/%m/%Y") if self.fecha else "-",
            "Hora": self.hora.strftime("%H:%M") if self.hora else "-",
            "Datos Filiatorios": self.datos_filiatorios or "-",
        }
    
    def __str__(self) -> str:
        return f'{self.alias_formateado}, mencionado en {self.delito}'
    
    def __repr__(self) -> str:
        return f"MentionedPerson(alias={self.alias!r}, delito={self.delito!r})"
