"""
Procesador principal de datos.

Coordina la lectura de shapefiles y la generación de datos
agregados para los reportes.
"""
import logging
from datetime import date
from typing import List, Optional, Dict, Any, Tuple
from pathlib import Path

from .shapefile_reader import ShapefileReader
from .field_mapper import FieldMapper
from ..models.crime_record import CrimeRecord
from ..models.mentioned_person import MentionedPerson
from ..models.apprehended import Apprehended
from ..models.report_data import PeriodData, ReportData

logger = logging.getLogger(__name__)


class DataProcessor:
    """
    Procesador central de datos del sistema S.I.D.I.C.
    
    Coordina la lectura de múltiples shapefiles y genera
    los datos necesarios para los reportes.
    """
    
    def __init__(self, field_mapper: Optional[FieldMapper] = None):
        """
        Inicializa el procesador.
        
        Args:
            field_mapper: Mapeador de campos personalizado.
        """
        self.field_mapper = field_mapper or FieldMapper()
        self.reader = ShapefileReader(self.field_mapper)
        
        # Datos cargados
        self._hechos: List[CrimeRecord] = []
        self._mencionados: List[MentionedPerson] = []
        self._aprehendidos: List[Apprehended] = []
        self._jurisdiccion: Any = None
        self._jurisdiccion_nombre: str = ""
        
        # Estado de carga
        self._loaded_files: Dict[str, Dict] = {}
        self._validation_results: Dict[str, Dict] = {}
    
    # ═══════════════════════════════════════════════════════════════════════
    # CARGA DE DATOS
    # ═══════════════════════════════════════════════════════════════════════
    
    def load_hechos(self, path: str) -> Dict[str, Any]:
        """
        Carga el shapefile de hechos delictuales.
        
        Args:
            path: Ruta al archivo .shp
        
        Returns:
            Resultado de la validación y carga.
        """
        logger.info(f"Cargando hechos desde: {path}")
        
        hechos, validation = self.reader.read_hechos(path)
        self._hechos = hechos
        self._loaded_files['hechos'] = {'path': path, 'count': len(hechos)}
        self._validation_results['hechos'] = validation
        
        logger.info(f"Cargados {len(hechos)} hechos delictuales")
        return validation
    
    def load_mencionados(self, path: str) -> Dict[str, Any]:
        """Carga el shapefile de mencionados."""
        logger.info(f"Cargando mencionados desde: {path}")
        
        mencionados, validation = self.reader.read_mencionados(path)
        self._mencionados = mencionados
        self._loaded_files['mencionados'] = {'path': path, 'count': len(mencionados)}
        self._validation_results['mencionados'] = validation
        
        logger.info(f"Cargados {len(mencionados)} mencionados")
        return validation
    
    def load_aprehendidos(self, path: str) -> Dict[str, Any]:
        """Carga el shapefile de aprehendidos."""
        logger.info(f"Cargando aprehendidos desde: {path}")
        
        aprehendidos, validation = self.reader.read_aprehendidos(path)
        self._aprehendidos = aprehendidos
        self._loaded_files['aprehendidos'] = {'path': path, 'count': len(aprehendidos)}
        self._validation_results['aprehendidos'] = validation
        
        logger.info(f"Cargados {len(aprehendidos)} aprehendidos")
        return validation
    
    def load_jurisdiccion(self, path: str) -> Dict[str, Any]:
        """Carga el shapefile de jurisdicción."""
        logger.info(f"Cargando jurisdicción desde: {path}")
        
        geom, validation = self.reader.read_jurisdiccion(path)
        self._jurisdiccion = geom
        self._jurisdiccion_nombre = validation.get('nombre', '')
        self._loaded_files['jurisdiccion'] = {'path': path}
        self._validation_results['jurisdiccion'] = validation
        
        return validation
    
    def load_all(
        self,
        hechos_path: str,
        mencionados_path: Optional[str] = None,
        aprehendidos_path: Optional[str] = None,
        jurisdiccion_path: Optional[str] = None
    ) -> Dict[str, Dict[str, Any]]:
        """
        Carga todos los shapefiles.
        
        Args:
            hechos_path: Ruta al shapefile de hechos (obligatorio)
            mencionados_path: Ruta al shapefile de mencionados
            aprehendidos_path: Ruta al shapefile de aprehendidos
            jurisdiccion_path: Ruta al shapefile de jurisdicción
        
        Returns:
            Diccionario con resultados de validación por archivo.
        """
        results = {}
        
        results['hechos'] = self.load_hechos(hechos_path)
        
        if mencionados_path:
            results['mencionados'] = self.load_mencionados(mencionados_path)
        
        if aprehendidos_path:
            results['aprehendidos'] = self.load_aprehendidos(aprehendidos_path)
        
        if jurisdiccion_path:
            results['jurisdiccion'] = self.load_jurisdiccion(jurisdiccion_path)
        
        return results
    
    # ═══════════════════════════════════════════════════════════════════════
    # ACCESO A DATOS
    # ═══════════════════════════════════════════════════════════════════════
    
    @property
    def hechos(self) -> List[CrimeRecord]:
        """Todos los hechos cargados."""
        return self._hechos
    
    @property
    def mencionados(self) -> List[MentionedPerson]:
        """Todos los mencionados cargados."""
        return self._mencionados
    
    @property
    def aprehendidos(self) -> List[Apprehended]:
        """Todos los aprehendidos cargados."""
        return self._aprehendidos
    
    @property
    def jurisdiccion(self):
        """Geometría de la jurisdicción."""
        return self._jurisdiccion
    
    @property
    def jurisdiccion_nombre(self) -> str:
        """Nombre de la jurisdicción."""
        return self._jurisdiccion_nombre
    
    @property
    def total_hechos(self) -> int:
        """Total de hechos cargados."""
        return len(self._hechos)
    
    @property
    def is_loaded(self) -> bool:
        """Indica si hay datos cargados."""
        return len(self._hechos) > 0
    
    # ═══════════════════════════════════════════════════════════════════════
    # FILTRADO POR PERÍODO
    # ═══════════════════════════════════════════════════════════════════════
    
    def filter_by_period(
        self,
        fecha_inicio: date,
        fecha_fin: date
    ) -> Tuple[List[CrimeRecord], List[MentionedPerson], List[Apprehended]]:
        """
        Filtra todos los datos por período.
        
        Returns:
            Tuple (hechos, mencionados, aprehendidos) del período.
        """
        hechos = [
            h for h in self._hechos
            if h.matches_period(fecha_inicio, fecha_fin)
        ]
        
        mencionados = [
            m for m in self._mencionados
            if m.matches_period(fecha_inicio, fecha_fin)
        ]
        
        aprehendidos = [
            a for a in self._aprehendidos
            if a.matches_period(fecha_inicio, fecha_fin)
        ]
        
        return hechos, mencionados, aprehendidos
    
    def create_period_data(
        self,
        nombre: str,
        fecha_inicio: date,
        fecha_fin: date
    ) -> PeriodData:
        """
        Crea un objeto PeriodData con los datos filtrados.
        
        Args:
            nombre: Nombre identificador del período
            fecha_inicio: Fecha de inicio
            fecha_fin: Fecha de fin
        
        Returns:
            PeriodData con todos los datos del período.
        """
        hechos, mencionados, aprehendidos = self.filter_by_period(
            fecha_inicio, fecha_fin
        )
        
        return PeriodData(
            nombre=nombre,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            hechos=hechos,
            mencionados=mencionados,
            aprehendidos=aprehendidos
        )
    
    # ═══════════════════════════════════════════════════════════════════════
    # GENERACIÓN DE REPORTES
    # ═══════════════════════════════════════════════════════════════════════
    
    def create_report(
        self,
        periodos: List[Tuple[str, date, date]],
        titulo: str = "INFORME DELICTUAL"
    ) -> ReportData:
        """
        Crea un ReportData completo.
        
        Args:
            periodos: Lista de tuplas (nombre, fecha_inicio, fecha_fin)
            titulo: Título del informe
        
        Returns:
            ReportData listo para generar reportes.
        """
        report = ReportData(
            titulo=titulo,
            jurisdiccion=self._jurisdiccion_nombre,
            fecha_generacion=date.today()
        )
        
        for nombre, inicio, fin in periodos:
            period_data = self.create_period_data(nombre, inicio, fin)
            report.agregar_periodo(period_data)
        
        return report
    
    def create_single_period_report(
        self,
        fecha_inicio: date,
        fecha_fin: date,
        titulo: str = "INFORME DELICTUAL"
    ) -> ReportData:
        """
        Crea un reporte de un solo período.
        
        Convenience method para el caso más común.
        """
        from ..utils.date_utils import format_date_range
        
        nombre = format_date_range(fecha_inicio, fecha_fin)
        return self.create_report(
            [(nombre, fecha_inicio, fecha_fin)],
            titulo
        )
    
    def create_comparative_report(
        self,
        periodo1: Tuple[date, date],
        periodo2: Tuple[date, date],
        titulo: str = "INFORME COMPARATIVO"
    ) -> ReportData:
        """
        Crea un reporte comparativo entre dos períodos.
        
        Args:
            periodo1: (fecha_inicio, fecha_fin) del primer período
            periodo2: (fecha_inicio, fecha_fin) del segundo período
        """
        from ..utils.date_utils import format_date_range
        
        nombre1 = format_date_range(periodo1[0], periodo1[1])
        nombre2 = format_date_range(periodo2[0], periodo2[1])
        
        return self.create_report(
            [
                (nombre1, periodo1[0], periodo1[1]),
                (nombre2, periodo2[0], periodo2[1])
            ],
            titulo
        )
    
    # ═══════════════════════════════════════════════════════════════════════
    # ESTADÍSTICAS RÁPIDAS
    # ═══════════════════════════════════════════════════════════════════════
    
    def get_date_range(self) -> Tuple[Optional[date], Optional[date]]:
        """
        Obtiene el rango de fechas de los datos cargados.
        
        Returns:
            (fecha_min, fecha_max) o (None, None) si no hay datos.
        """
        fechas = [h.fecha for h in self._hechos if h.fecha]
        
        if not fechas:
            return None, None
        
        return min(fechas), max(fechas)
    
    def get_summary(self) -> Dict[str, Any]:
        """
        Obtiene un resumen de los datos cargados.
        """
        fecha_min, fecha_max = self.get_date_range()
        
        return {
            'total_hechos': len(self._hechos),
            'total_mencionados': len(self._mencionados),
            'total_aprehendidos': len(self._aprehendidos),
            'fecha_minima': fecha_min,
            'fecha_maxima': fecha_max,
            'jurisdiccion': self._jurisdiccion_nombre,
            'archivos_cargados': list(self._loaded_files.keys()),
            'validaciones': self._validation_results
        }
