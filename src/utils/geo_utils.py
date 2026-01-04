"""
Utilidades geográficas y de geometría.
"""
from typing import Optional, Tuple, Any
import math


def extract_coordinates(geometry: Any) -> Optional[Tuple[float, float]]:
    """
    Extrae coordenadas (lon, lat) de un objeto geometría.
    
    Soporta:
    - shapely Point
    - tuple/list [x, y]
    - dict con keys 'x', 'y' o 'lon', 'lat'
    
    Returns:
        Tuple (longitud, latitud) o None
    """
    if geometry is None:
        return None
    
    # shapely Point
    if hasattr(geometry, 'x') and hasattr(geometry, 'y'):
        return (geometry.x, geometry.y)
    
    # Tuple o List
    if isinstance(geometry, (tuple, list)) and len(geometry) >= 2:
        return (float(geometry[0]), float(geometry[1]))
    
    # Dict
    if isinstance(geometry, dict):
        if 'x' in geometry and 'y' in geometry:
            return (float(geometry['x']), float(geometry['y']))
        if 'lon' in geometry and 'lat' in geometry:
            return (float(geometry['lon']), float(geometry['lat']))
        if 'longitude' in geometry and 'latitude' in geometry:
            return (float(geometry['longitude']), float(geometry['latitude']))
    
    return None


def format_coordinates(lon: float, lat: float, precision: int = 6) -> str:
    """
    Formatea coordenadas para mostrar.
    
    Returns:
        String con formato "lat, lon"
    """
    return f"{lat:.{precision}f}, {lon:.{precision}f}"


def calculate_distance(
    point1: Tuple[float, float],
    point2: Tuple[float, float]
) -> float:
    """
    Calcula la distancia aproximada entre dos puntos en metros.
    Usa la fórmula de Haversine.
    
    Args:
        point1: (lon, lat) del primer punto
        point2: (lon, lat) del segundo punto
    
    Returns:
        Distancia en metros
    """
    R = 6371000  # Radio de la Tierra en metros
    
    lon1, lat1 = math.radians(point1[0]), math.radians(point1[1])
    lon2, lat2 = math.radians(point2[0]), math.radians(point2[1])
    
    dlat = lat2 - lat1
    dlon = lon2 - lon1
    
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def validate_coordinates(lon: float, lat: float) -> bool:
    """
    Valida que las coordenadas estén en rangos válidos.
    
    Returns:
        True si las coordenadas son válidas
    """
    return -180 <= lon <= 180 and -90 <= lat <= 90


def get_bounding_box(
    points: list[Tuple[float, float]]
) -> Optional[Tuple[float, float, float, float]]:
    """
    Calcula el bounding box de una lista de puntos.
    
    Returns:
        Tuple (min_lon, min_lat, max_lon, max_lat) o None si no hay puntos
    """
    if not points:
        return None
    
    lons = [p[0] for p in points]
    lats = [p[1] for p in points]
    
    return (min(lons), min(lats), max(lons), max(lats))
