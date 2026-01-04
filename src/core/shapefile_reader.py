"""
Lector y validador de archivos Shapefile.

Utiliza geopandas para leer archivos .shp y convertirlos
a los modelos internos del sistema.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Any, TYPE_CHECKING
from datetime import date

if TYPE_CHECKING:
    from pandas import Series as PdSeries

try:
    import geopandas as gpd
    import pandas as pd
    HAS_GEOPANDAS = True
except ImportError:
    HAS_GEOPANDAS = False
    gpd = None
    pd = None

from .field_mapper import FieldMapper
from ..models.crime_record import CrimeRecord
from ..models.mentioned_person import MentionedPerson
from ..models.apprehended import Apprehended
from ..utils.date_utils import parse_date, parse_time
from ..utils.geo_utils import extract_coordinates

logger = logging.getLogger(__name__)


class ShapefileValidationError(Exception):
    """Error de validación de shapefile."""
    pass


class ShapefileReader:
    """
    Lector de archivos Shapefile con validación y conversión a modelos.
    
    Soporta lectura de:
    - Hechos delictuales
    - Mencionados
    - Aprehendidos
    - Jurisdicción (polígono)
    """
    
    def __init__(self, field_mapper: Optional[FieldMapper] = None):
        """
        Inicializa el lector.
        
        Args:
            field_mapper: Mapeador de campos. Si es None, usa el por defecto.
        """
        if not HAS_GEOPANDAS:
            raise ImportError(
                "geopandas no está instalado. "
                "Instálalo con: pip install geopandas"
            )
        
        self.field_mapper = field_mapper or FieldMapper()
        self._loaded_data: Dict[str, Any] = {}
    
    # ═══════════════════════════════════════════════════════════════════════
    # VALIDACIÓN
    # ═══════════════════════════════════════════════════════════════════════
    
    def validate_shapefile(self, path: str) -> Dict[str, Any]:
        """
        Valida un archivo shapefile.
        
        Args:
            path: Ruta al archivo .shp
        
        Returns:
            Diccionario con información de validación:
            {
                'valid': bool,
                'path': str,
                'records': int,
                'fields': list,
                'geometry_type': str,
                'crs': str,
                'errors': list,
                'warnings': list
            }
        """
        result = {
            'valid': True,
            'path': path,
            'records': 0,
            'fields': [],
            'geometry_type': None,
            'crs': None,
            'errors': [],
            'warnings': []
        }
        
        path_obj = Path(path)
        
        # Verificar que existe
        if not path_obj.exists():
            result['valid'] = False
            result['errors'].append(f"Archivo no encontrado: {path}")
            return result
        
        # Verificar extensión
        if path_obj.suffix.lower() != '.shp':
            result['warnings'].append(
                f"Extensión inesperada: {path_obj.suffix}. Se esperaba .shp"
            )
        
        # Verificar archivos asociados
        required_extensions = ['.dbf', '.shx']
        optional_extensions = ['.prj', '.cpg']
        
        for ext in required_extensions:
            assoc_file = path_obj.with_suffix(ext)
            if not assoc_file.exists():
                result['valid'] = False
                result['errors'].append(f"Archivo requerido faltante: {assoc_file.name}")
        
        for ext in optional_extensions:
            assoc_file = path_obj.with_suffix(ext)
            if not assoc_file.exists():
                result['warnings'].append(f"Archivo opcional faltante: {assoc_file.name}")
        
        if not result['valid']:
            return result
        
        # Intentar leer el shapefile
        try:
            gdf = gpd.read_file(path)
            
            result['records'] = len(gdf)
            result['fields'] = list(gdf.columns)
            
            if 'geometry' in gdf.columns:
                result['fields'].remove('geometry')
                if not gdf.geometry.empty:
                    result['geometry_type'] = gdf.geometry.geom_type.iloc[0]
            
            if gdf.crs:
                result['crs'] = str(gdf.crs)
            else:
                result['warnings'].append("Sin sistema de referencia (CRS) definido")
            
            # Verificar registros sin geometría
            null_geom = gdf.geometry.isna().sum()
            if null_geom > 0:
                result['warnings'].append(
                    f"{null_geom} registros sin geometría"
                )
            
            if result['records'] == 0:
                result['warnings'].append("El shapefile está vacío")
        
        except Exception as e:
            result['valid'] = False
            result['errors'].append(f"Error leyendo shapefile: {str(e)}")
        
        return result
    
    # ═══════════════════════════════════════════════════════════════════════
    # LECTURA DE HECHOS
    # ═══════════════════════════════════════════════════════════════════════
    
    def read_hechos(
        self,
        path: str,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> Tuple[List[CrimeRecord], Dict[str, Any]]:
        """
        Lee un shapefile de hechos delictuales.
        
        Args:
            path: Ruta al archivo .shp
            fecha_inicio: Filtrar desde esta fecha (opcional)
            fecha_fin: Filtrar hasta esta fecha (opcional)
        
        Returns:
            Tuple (lista de CrimeRecord, info de validación)
        """
        validation = self.validate_shapefile(path)
        if not validation['valid']:
            return [], validation
        
        # Mapear campos
        field_map = self.field_mapper.build_field_map('hechos', validation['fields'])
        validation['field_mapping'] = field_map
        
        # Verificar campos críticos
        map_validation = self.field_mapper.validate_mapping('hechos', validation['fields'])
        if not map_validation['valid']:
            validation['warnings'].append(
                f"Campos críticos faltantes: {map_validation['critical_missing']}"
            )
        
        # Leer datos
        gdf = gpd.read_file(path)
        records = []
        
        for idx, row in gdf.iterrows():
            try:
                record = self._row_to_crime_record(row, field_map)
                
                # Filtrar por período si se especifica
                if fecha_inicio and record.fecha and record.fecha < fecha_inicio:
                    continue
                if fecha_fin and record.fecha and record.fecha > fecha_fin:
                    continue
                
                records.append(record)
            
            except Exception as e:
                logger.warning(f"Error procesando fila {idx}: {e}")
                validation['warnings'].append(f"Fila {idx}: {str(e)}")
        
        validation['processed_records'] = len(records)
        return records, validation
    
    def _row_to_crime_record(
        self,
        row: 'PdSeries',
        field_map: Dict[str, Optional[str]]
    ) -> CrimeRecord:
        """Convierte una fila del GeoDataFrame a CrimeRecord."""
        
        def get_value(internal_field: str) -> Any:
            shp_field = field_map.get(internal_field)
            if shp_field and shp_field in row.index:
                val = row[shp_field]
                if pd.isna(val):
                    return None
                return val
            return None
        
        # Extraer coordenadas
        coords = None
        if hasattr(row, 'geometry') and row.geometry is not None:
            coords = extract_coordinates(row.geometry)
        
        # Campos extra (no mapeados)
        mapped_fields = set(v for v in field_map.values() if v)
        campos_extra = {
            k: v for k, v in row.items()
            if k not in mapped_fields and k != 'geometry' and not pd.isna(v)
        }
        
        return CrimeRecord(
            fecha=parse_date(get_value('fecha')),
            hora=parse_time(get_value('hora')),
            delito=str(get_value('delito') or '').upper().strip(),
            ambito=str(get_value('ambito') or '').upper().strip(),
            movilidad=str(get_value('movilidad') or '').upper().strip(),
            arma_medio=str(get_value('arma') or '').upper().strip(),
            esclarecido=str(get_value('esclarecido') or '').upper().strip(),
            direccion=str(get_value('direccion') or '').strip(),
            coordenadas=coords,
            geometry=row.geometry if hasattr(row, 'geometry') else None,
            campos_extra=campos_extra
        )
    
    # ═══════════════════════════════════════════════════════════════════════
    # LECTURA DE MENCIONADOS
    # ═══════════════════════════════════════════════════════════════════════
    
    def read_mencionados(
        self,
        path: str,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> Tuple[List[MentionedPerson], Dict[str, Any]]:
        """
        Lee un shapefile de personas mencionadas.
        
        Returns:
            Tuple (lista de MentionedPerson, info de validación)
        """
        validation = self.validate_shapefile(path)
        if not validation['valid']:
            return [], validation
        
        field_map = self.field_mapper.build_field_map('mencionados', validation['fields'])
        validation['field_mapping'] = field_map
        
        gdf = gpd.read_file(path)
        records = []
        
        for idx, row in gdf.iterrows():
            try:
                record = self._row_to_mentioned(row, field_map)
                
                if fecha_inicio and record.fecha and record.fecha < fecha_inicio:
                    continue
                if fecha_fin and record.fecha and record.fecha > fecha_fin:
                    continue
                
                records.append(record)
            
            except Exception as e:
                logger.warning(f"Error procesando fila {idx}: {e}")
                validation['warnings'].append(f"Fila {idx}: {str(e)}")
        
        validation['processed_records'] = len(records)
        return records, validation
    
    def _row_to_mentioned(
        self,
        row: 'PdSeries',
        field_map: Dict[str, Optional[str]]
    ) -> MentionedPerson:
        """Convierte una fila a MentionedPerson."""
        
        def get_value(internal_field: str) -> Any:
            shp_field = field_map.get(internal_field)
            if shp_field and shp_field in row.index:
                val = row[shp_field]
                if pd.isna(val):
                    return None
                return val
            return None
        
        return MentionedPerson(
            alias=str(get_value('alias') or '').strip(),
            datos_filiatorios=str(get_value('datos') or '').strip(),
            delito=str(get_value('delito') or '').upper().strip(),
            fecha=parse_date(get_value('fecha')),
            hora=parse_time(get_value('hora')),
            direccion_hecho=str(get_value('direccion') or '').strip(),
        )
    
    # ═══════════════════════════════════════════════════════════════════════
    # LECTURA DE APREHENDIDOS
    # ═══════════════════════════════════════════════════════════════════════
    
    def read_aprehendidos(
        self,
        path: str,
        fecha_inicio: Optional[date] = None,
        fecha_fin: Optional[date] = None
    ) -> Tuple[List[Apprehended], Dict[str, Any]]:
        """
        Lee un shapefile de personas aprehendidas.
        
        Returns:
            Tuple (lista de Apprehended, info de validación)
        """
        validation = self.validate_shapefile(path)
        if not validation['valid']:
            return [], validation
        
        field_map = self.field_mapper.build_field_map('aprehendidos', validation['fields'])
        validation['field_mapping'] = field_map
        
        gdf = gpd.read_file(path)
        records = []
        
        for idx, row in gdf.iterrows():
            try:
                record = self._row_to_apprehended(row, field_map)
                
                if fecha_inicio and record.fecha and record.fecha < fecha_inicio:
                    continue
                if fecha_fin and record.fecha and record.fecha > fecha_fin:
                    continue
                
                records.append(record)
            
            except Exception as e:
                logger.warning(f"Error procesando fila {idx}: {e}")
                validation['warnings'].append(f"Fila {idx}: {str(e)}")
        
        validation['processed_records'] = len(records)
        return records, validation
    
    def _row_to_apprehended(
        self,
        row: 'PdSeries',
        field_map: Dict[str, Optional[str]]
    ) -> Apprehended:
        """Convierte una fila a Apprehended."""
        
        def get_value(internal_field: str) -> Any:
            shp_field = field_map.get(internal_field)
            if shp_field and shp_field in row.index:
                val = row[shp_field]
                if pd.isna(val):
                    return None
                return val
            return None
        
        edad_val = get_value('edad')
        edad = None
        if edad_val is not None:
            try:
                edad = int(float(edad_val))
            except (ValueError, TypeError):
                pass
        
        return Apprehended(
            nombre=str(get_value('nombre') or '').strip(),
            edad=edad,
            sexo=str(get_value('sexo') or '').strip(),
            clasificacion=str(get_value('clasificacion') or '').upper().strip(),
            delito=str(get_value('delito') or '').upper().strip(),
            fecha=parse_date(get_value('fecha')),
        )
    
    # ═══════════════════════════════════════════════════════════════════════
    # LECTURA DE JURISDICCIÓN
    # ═══════════════════════════════════════════════════════════════════════
    
    def read_jurisdiccion(self, path: str) -> Tuple[Optional[Any], Dict[str, Any]]:
        """
        Lee un shapefile de jurisdicción (polígono).
        
        Returns:
            Tuple (geometría del polígono, info de validación)
        """
        validation = self.validate_shapefile(path)
        if not validation['valid']:
            return None, validation
        
        gdf = gpd.read_file(path)
        
        if len(gdf) == 0:
            validation['warnings'].append("Shapefile de jurisdicción vacío")
            return None, validation
        
        # Tomar el primer polígono
        geometry = gdf.geometry.iloc[0]
        
        # Extraer nombre si existe
        nombre_fields = ['NOMBRE', 'NAME', 'JURISD', 'COMISARIA']
        for field in nombre_fields:
            if field in gdf.columns:
                validation['nombre'] = gdf[field].iloc[0]
                break
        
        return geometry, validation
