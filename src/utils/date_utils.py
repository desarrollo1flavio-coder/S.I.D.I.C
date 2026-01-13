"""
Utilidades para manejo de fechas y horas.
"""
from datetime import datetime, date, time
from typing import Optional, Tuple, Union
import re

from .constants import FranjaHoraria, WEEKDAY_TO_NAME


def parse_date(value: Union[str, datetime, date, None]) -> Optional[date]:
    """
    Convierte un valor a objeto date.
    
    Soporta formatos:
    - dd/mm/yyyy
    - dd-mm-yyyy
    - yyyy-mm-dd
    - yyyy/mm/dd
    - datetime object
    - date object
    """
    if value is None:
        return None
    
    if isinstance(value, datetime):
        return value.date()
    
    if isinstance(value, date):
        return value
    
    if isinstance(value, str):
        value = value.strip()
        
        # Formatos comunes
        formats = [
            "%d/%m/%Y",
            "%d-%m-%Y",
            "%Y-%m-%d",
            "%Y/%m/%d",
            "%d/%m/%y",
            "%d-%m-%y",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt).date()
            except ValueError:
                continue
        
        # Intentar extraer fecha con regex
        match = re.search(r'(\d{1,2})[/-](\d{1,2})[/-](\d{2,4})', value)
        if match:
            day, month, year = match.groups()
            if len(year) == 2:
                year = "20" + year if int(year) < 50 else "19" + year
            try:
                return date(int(year), int(month), int(day))
            except ValueError:
                pass
    
    return None


def parse_time(value: Union[str, datetime, time, None]) -> Optional[time]:
    """
    Convierte un valor a objeto time.
    
    Soporta formatos:
    - HH:MM
    - HH:MM:SS
    - HH.MM
    - H:MM
    """
    if value is None:
        return None
    
    if isinstance(value, datetime):
        return value.time()
    
    if isinstance(value, time):
        return value
    
    if isinstance(value, str):
        value = value.strip()
        
        # Reemplazar punto por dos puntos
        value = value.replace(".", ":")
        
        formats = [
            "%H:%M",
            "%H:%M:%S",
            "%I:%M %p",
            "%I:%M:%S %p",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(value, fmt).time()
            except ValueError:
                continue
        
        # Intentar extraer hora con regex
        match = re.search(r'(\d{1,2})[:\.](\d{2})', value)
        if match:
            hour, minute = match.groups()
            try:
                return time(int(hour), int(minute))
            except ValueError:
                pass
    
    return None


def get_franja_horaria(hora: Union[time, int, str, None]) -> Optional[FranjaHoraria]:
    """
    Obtiene la franja horaria correspondiente a una hora.
    
    Args:
        hora: Puede ser time, int (hora 0-23), o string
    
    Returns:
        FranjaHoraria correspondiente o None
    """
    if hora is None:
        return None
    
    if isinstance(hora, str):
        hora = parse_time(hora)
        if hora is None:
            return None
    
    if isinstance(hora, time):
        hour = hora.hour
    elif isinstance(hora, int):
        hour = hora
    else:
        return None
    
    return FranjaHoraria.from_hour(hour)


def get_dia_semana(fecha: Union[date, datetime, str, None]) -> Optional[str]:
    """
    Obtiene el nombre del día de la semana para una fecha.
    
    Returns:
        Nombre del día (LUNES, MARTES, etc.) o None
    """
    if fecha is None:
        return None
    
    if isinstance(fecha, str):
        fecha = parse_date(fecha)
        if fecha is None:
            return None
    
    if isinstance(fecha, datetime):
        fecha = fecha.date()
    
    return WEEKDAY_TO_NAME.get(fecha.weekday())


def format_date_range(start: date, end: date) -> str:
    """
    Formatea un rango de fechas para mostrar.
    
    Ejemplo: "1 AL 22 DE DICIEMBRE 2025"
    """
    months = [
        "ENERO", "FEBRERO", "MARZO", "ABRIL", "MAYO", "JUNIO",
        "JULIO", "AGOSTO", "SEPTIEMBRE", "OCTUBRE", "NOVIEMBRE", "DICIEMBRE"
    ]
    
    if start.month == end.month and start.year == end.year:
        return f"{start.day} AL {end.day} DE {months[start.month - 1]} {start.year}"
    elif start.year == end.year:
        return f"{start.day} DE {months[start.month - 1]} AL {end.day} DE {months[end.month - 1]} {end.year}"
    else:
        return f"{start.day} DE {months[start.month - 1]} {start.year} AL {end.day} DE {months[end.month - 1]} {end.year}"


def is_date_in_range(fecha: date, start: date, end: date) -> bool:
    """Verifica si una fecha está dentro de un rango (inclusive)."""
    return start <= fecha <= end


def formato_fecha_abreviada(fecha: date) -> str:
    """
    Formatea una fecha de forma abreviada para etiquetas de gráficos.
    
    Ejemplo: date(2025, 12, 14) -> "Dic'25"
    
    Args:
        fecha: Fecha a formatear
    
    Returns:
        String con formato "Mes'AA" (ej: "Dic'25")
    """
    meses_abrev = [
        "Ene", "Feb", "Mar", "Abr", "May", "Jun",
        "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"
    ]
    
    mes = meses_abrev[fecha.month - 1]
    año = str(fecha.year)[-2:]  # Últimos 2 dígitos
    
    return f"{mes}'{año}"


def formato_rango_abreviado(start: date, end: date) -> str:
    """
    Formatea un rango de fechas de forma abreviada.
    
    Ejemplo: "14 Dic - 13 Ene'26"
    
    Args:
        start: Fecha de inicio
        end: Fecha de fin
    
    Returns:
        String con rango abreviado
    """
    meses_abrev = [
        "Ene", "Feb", "Mar", "Abr", "May", "Jun",
        "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"
    ]
    
    if start.year == end.year and start.month == end.month:
        return f"{start.day}-{end.day} {meses_abrev[end.month - 1]}'{str(end.year)[-2:]}"
    elif start.year == end.year:
        return f"{start.day} {meses_abrev[start.month - 1]} - {end.day} {meses_abrev[end.month - 1]}'{str(end.year)[-2:]}"
    else:
        return f"{start.day} {meses_abrev[start.month - 1]}'{str(start.year)[-2:]} - {end.day} {meses_abrev[end.month - 1]}'{str(end.year)[-2:]}"
