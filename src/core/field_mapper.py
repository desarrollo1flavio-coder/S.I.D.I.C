"""
Mapeador de campos configurable.

Permite mapear los nombres de campos del shapefile a los campos
internos del sistema, soportando múltiples posibles nombres.
"""
import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from ..utils.constants import DEFAULT_FIELD_MAPPING

logger = logging.getLogger(__name__)


class FieldMapper:
    """
    Mapea campos de shapefiles a campos internos del sistema.
    
    Permite configuración flexible para adaptarse a diferentes
    estructuras de datos de entrada.
    """
    
    def __init__(self, mapping: Optional[Dict] = None):
        """
        Inicializa el mapeador.
        
        Args:
            mapping: Diccionario de mapeo personalizado.
                     Si es None, usa el mapeo por defecto.
        """
        self.mapping = mapping or DEFAULT_FIELD_MAPPING.copy()
        self._cache: Dict[str, Dict[str, str]] = {}
    
    @classmethod
    def from_file(cls, path: str) -> 'FieldMapper':
        """
        Carga el mapeo desde un archivo JSON.
        
        Args:
            path: Ruta al archivo JSON de configuración.
        
        Returns:
            Nueva instancia de FieldMapper.
        """
        try:
            with open(path, 'r', encoding='utf-8') as f:
                mapping = json.load(f)
            return cls(mapping)
        except Exception as e:
            logger.warning(f"Error cargando mapeo desde {path}: {e}. Usando mapeo por defecto.")
            return cls()
    
    def save_to_file(self, path: str) -> bool:
        """
        Guarda el mapeo actual a un archivo JSON.
        
        Args:
            path: Ruta donde guardar el archivo.
        
        Returns:
            True si se guardó correctamente.
        """
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.mapping, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            logger.error(f"Error guardando mapeo: {e}")
            return False
    
    def detect_field(
        self,
        layer_type: str,
        internal_field: str,
        available_fields: List[str]
    ) -> Optional[str]:
        """
        Detecta qué campo del shapefile corresponde a un campo interno.
        
        Args:
            layer_type: Tipo de capa ('hechos', 'mencionados', 'aprehendidos')
            internal_field: Nombre del campo interno (ej: 'fecha', 'delito')
            available_fields: Lista de campos disponibles en el shapefile
        
        Returns:
            Nombre del campo en el shapefile, o None si no se encuentra.
        """
        # Verificar cache
        cache_key = f"{layer_type}:{internal_field}"
        if cache_key in self._cache:
            cached = self._cache[cache_key]
            for field in available_fields:
                if field == cached:
                    return field
        
        # Buscar en el mapeo
        if layer_type not in self.mapping:
            return None
        
        if internal_field not in self.mapping[layer_type]:
            return None
        
        possible_names = self.mapping[layer_type][internal_field]
        
        # Buscar coincidencia exacta (case-insensitive)
        available_upper = {f.upper(): f for f in available_fields}
        
        for name in possible_names:
            name_upper = name.upper()
            if name_upper in available_upper:
                result = available_upper[name_upper]
                self._cache[cache_key] = result
                return result
        
        # Buscar coincidencia parcial
        for name in possible_names:
            name_upper = name.upper()
            for avail_upper, avail_orig in available_upper.items():
                if name_upper in avail_upper or avail_upper in name_upper:
                    self._cache[cache_key] = avail_orig
                    return avail_orig
        
        return None
    
    def build_field_map(
        self,
        layer_type: str,
        available_fields: List[str]
    ) -> Dict[str, Optional[str]]:
        """
        Construye un mapeo completo para una capa.
        
        Args:
            layer_type: Tipo de capa
            available_fields: Campos disponibles en el shapefile
        
        Returns:
            {campo_interno: campo_shapefile o None}
        """
        if layer_type not in self.mapping:
            return {}
        
        result = {}
        for internal_field in self.mapping[layer_type].keys():
            result[internal_field] = self.detect_field(
                layer_type,
                internal_field,
                available_fields
            )
        
        return result
    
    def get_required_fields(self, layer_type: str) -> List[str]:
        """
        Obtiene los campos internos requeridos para una capa.
        
        Args:
            layer_type: Tipo de capa
        
        Returns:
            Lista de nombres de campos internos requeridos.
        """
        if layer_type not in self.mapping:
            return []
        return list(self.mapping[layer_type].keys())
    
    def add_alias(
        self,
        layer_type: str,
        internal_field: str,
        alias: str
    ) -> None:
        """
        Agrega un alias adicional para un campo.
        
        Args:
            layer_type: Tipo de capa
            internal_field: Campo interno
            alias: Nuevo alias a agregar
        """
        if layer_type not in self.mapping:
            self.mapping[layer_type] = {}
        
        if internal_field not in self.mapping[layer_type]:
            self.mapping[layer_type][internal_field] = []
        
        if alias not in self.mapping[layer_type][internal_field]:
            self.mapping[layer_type][internal_field].append(alias)
        
        # Limpiar cache
        cache_key = f"{layer_type}:{internal_field}"
        if cache_key in self._cache:
            del self._cache[cache_key]
    
    def validate_mapping(
        self,
        layer_type: str,
        available_fields: List[str]
    ) -> Dict[str, Any]:
        """
        Valida el mapeo y reporta campos encontrados/faltantes.
        
        Returns:
            {
                'found': {campo_interno: campo_shp},
                'missing': [campos_internos_faltantes],
                'extra': [campos_shp_no_mapeados],
                'valid': bool
            }
        """
        field_map = self.build_field_map(layer_type, available_fields)
        
        found = {k: v for k, v in field_map.items() if v is not None}
        missing = [k for k, v in field_map.items() if v is None]
        
        mapped_fields = set(found.values())
        extra = [f for f in available_fields if f not in mapped_fields and f != 'geometry']
        
        # Campos críticos
        critical = ['fecha', 'delito']
        critical_missing = [c for c in critical if c in missing]
        
        return {
            'found': found,
            'missing': missing,
            'extra': extra,
            'critical_missing': critical_missing,
            'valid': len(critical_missing) == 0
        }
