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
                config = json.load(f)
            
            # Verificar si el JSON tiene la nueva estructura con "mappings"
            if "mappings" in config:
                # Nueva estructura: extraer source_fields de cada campo
                mapping = {}
                for layer_type, fields in config["mappings"].items():
                    mapping[layer_type] = {}
                    for field_name, field_config in fields.items():
                        if isinstance(field_config, dict) and "source_fields" in field_config:
                            mapping[layer_type][field_name] = field_config["source_fields"]
                        elif isinstance(field_config, list):
                            # Compatibilidad con formato antiguo
                            mapping[layer_type][field_name] = field_config
                return cls(mapping)
            else:
                # Formato antiguo: usar directamente
                return cls(config)
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
        
        # Nota: Se eliminó la búsqueda parcial porque causaba falsos positivos
        # con los nombres de campo DBF truncados (10 caracteres máx)
        
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


# ═══════════════════════════════════════════════════════════════════════════════
# NORMALIZADOR DE DELITOS
# ═══════════════════════════════════════════════════════════════════════════════

# Cache de aliases cargados
_delito_aliases_cache: Optional[Dict[str, str]] = None


def _load_delito_aliases() -> Dict[str, str]:
    """Carga los aliases de delitos desde field_mappings.json."""
    global _delito_aliases_cache
    
    if _delito_aliases_cache is not None:
        return _delito_aliases_cache
    
    _delito_aliases_cache = {}
    
    try:
        # Buscar archivo de configuración
        config_paths = [
            Path(__file__).parent.parent.parent / "config" / "field_mappings.json",
            Path("config/field_mappings.json"),
            Path("field_mappings.json"),
        ]
        
        for config_path in config_paths:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                
                if "delito_aliases" in config:
                    # Ignorar comentarios (claves que empiezan con _)
                    _delito_aliases_cache = {
                        k.upper(): v.upper()
                        for k, v in config["delito_aliases"].items()
                        if not k.startswith("_")
                    }
                break
                
    except Exception as e:
        logger.warning(f"Error cargando aliases de delitos: {e}")
    
    return _delito_aliases_cache


def normalizar_delito(delito: Optional[str]) -> str:
    """
    Normaliza el nombre de un delito a su forma canónica.
    
    Aplica:
    1. Conversión a mayúsculas
    2. Limpieza de espacios extra
    3. Mapeo de aliases conocidos
    4. Normalización de caracteres especiales
    
    Args:
        delito: Nombre del delito como viene del shapefile
    
    Returns:
        Nombre normalizado del delito
    
    Example:
        >>> normalizar_delito("robo agr. asaltante")
        "ROBO AGRAVADO ASALTANTE"
        >>> normalizar_delito("  HURTO  PUNGA  ")
        "HURTO PUNGA"
    """
    if not delito:
        return ""
    
    # Limpiar y normalizar
    delito_clean = delito.strip().upper()
    
    # Eliminar espacios múltiples
    import re
    delito_clean = re.sub(r'\s+', ' ', delito_clean)
    
    # Reemplazar caracteres especiales comunes
    delito_clean = delito_clean.replace('–', '-')  # En-dash to hyphen
    delito_clean = delito_clean.replace('—', '-')  # Em-dash to hyphen
    delito_clean = delito_clean.replace('Í', 'I')
    delito_clean = delito_clean.replace('Ó', 'O')
    delito_clean = delito_clean.replace('Á', 'A')
    delito_clean = delito_clean.replace('É', 'E')
    delito_clean = delito_clean.replace('Ú', 'U')
    delito_clean = delito_clean.replace('Ñ', 'N')  # Para búsquedas, mantener Ñ puede ser problema
    
    # Cargar aliases
    aliases = _load_delito_aliases()
    
    # Buscar en aliases
    if delito_clean in aliases:
        return aliases[delito_clean]
    
    # Si no hay alias, devolver limpio
    return delito_clean


def obtener_simbolo_delito(delito: str) -> Optional['SimboloDelito']:
    """
    Obtiene el símbolo correspondiente a un delito.
    
    Primero normaliza el nombre del delito y luego busca en SIMBOLOS_DELITOS.
    
    Args:
        delito: Nombre del delito (puede estar sin normalizar)
    
    Returns:
        SimboloDelito si existe, None si no se encuentra
    """
    from ..utils.constants import SIMBOLOS_DELITOS
    
    # Normalizar el delito
    delito_normalizado = normalizar_delito(delito)
    
    # Buscar en el diccionario
    if delito_normalizado in SIMBOLOS_DELITOS:
        return SIMBOLOS_DELITOS[delito_normalizado]
    
    # Intentar búsqueda parcial para casos edge
    for key, simbolo in SIMBOLOS_DELITOS.items():
        if key in delito_normalizado or delito_normalizado in key:
            return simbolo
    
    return None
