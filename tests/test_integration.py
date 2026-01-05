"""
Tests de integración para S.I.D.I.C
Sistema de Información Delictual e Inteligencia Criminal

Pruebas automatizadas que validan cada componente sin depender de red.
Ejecutar con: python -m pytest tests/test_integration.py -v
"""
import sys
import os
import tempfile
import shutil
from pathlib import Path
from datetime import date, time
from typing import List
import unittest

# Agregar el directorio raíz al path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

import geopandas as gpd
import pandas as pd
from shapely.geometry import Point

from src.core.field_mapper import FieldMapper
from src.core.shapefile_reader import ShapefileReader
from src.models.crime_record import CrimeRecord
from src.utils.constants import (
    CategoriaDelito, DELITOS_ROBO, DELITOS_HURTO, DELITOS_TENTATIVA_ROBO,
    DELITOS_TENTATIVA_HURTO, DELITOS_ESTAFA, SIMBOLOS_DELITOS,
    DEFAULT_FIELD_MAPPING, FranjaHoraria
)


class TestFieldMapper(unittest.TestCase):
    """Tests para el mapeador de campos."""
    
    def setUp(self):
        """Configurar el mapper para cada test."""
        self.mapper = FieldMapper.from_file(str(BASE_DIR / 'config' / 'field_mappings.json'))
    
    def test_load_from_json(self):
        """Verificar que el JSON se carga correctamente."""
        self.assertIn('hechos', self.mapper.mapping)
        self.assertIn('mencionados', self.mapper.mapping)
        self.assertIn('aprehendidos', self.mapper.mapping)
    
    def test_hechos_has_required_fields(self):
        """Verificar que hechos tiene los campos requeridos."""
        hechos = self.mapper.mapping.get('hechos', {})
        required = ['fecha', 'delito', 'hora', 'direccion', 'jurisdiccion']
        for field in required:
            self.assertIn(field, hechos, f"Campo requerido faltante: {field}")
    
    def test_detect_truncated_dbf_fields(self):
        """Verificar detección de campos DBF truncados (máx 10 caracteres)."""
        dbf_fields = [
            'ID_N_SRIO', 'JURIS_HECH', 'DPCIA_INT', 'FECHA_HECH', 
            'DIA_HECHO', 'HORA_HECH', 'FRAN_HORAR', 'DELITO', 
            'MODUS_OPER', 'ARMA_UTILI', 'SITUA_CAUS'
        ]
        
        field_map = self.mapper.build_field_map('hechos', dbf_fields)
        
        # Verificar mapeos esperados
        self.assertEqual(field_map.get('nro_sumario'), 'ID_N_SRIO')
        self.assertEqual(field_map.get('jurisdiccion'), 'JURIS_HECH')
        self.assertEqual(field_map.get('fecha'), 'FECHA_HECH')
        self.assertEqual(field_map.get('hora'), 'HORA_HECH')
        self.assertEqual(field_map.get('delito'), 'DELITO')
        self.assertEqual(field_map.get('modus_operandi'), 'MODUS_OPER')
    
    def test_validate_mapping(self):
        """Verificar validación del mapeo."""
        dbf_fields = ['FECHA_HECH', 'DELITO', 'HORA_HECH']
        validation = self.mapper.validate_mapping('hechos', dbf_fields)
        
        self.assertIn('found', validation)
        self.assertIn('missing', validation)
        self.assertIn('valid', validation)
        # Debe ser válido si tiene fecha y delito
        self.assertTrue(validation['valid'])


class TestShapefileReader(unittest.TestCase):
    """Tests para el lector de shapefiles."""
    
    @classmethod
    def setUpClass(cls):
        """Crear shapefile de prueba temporal."""
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_shp_path = os.path.join(cls.temp_dir, 'test_hechos.shp')
        
        # Crear datos de prueba con campos DBF truncados
        data = {
            'ID_N_SRIO': ['001-2025', '002-2025', '003-2025', '004-2025', '005-2025'],
            'JURIS_HECH': ['URO_AMAICHA', 'URO_AMAICHA', 'URO_AMAICHA', 'URO_AMAICHA', 'URO_AMAICHA'],
            'DPCIA_INT': ['CRIA AMAICHA', 'CRIA AMAICHA', 'CRIA AMAICHA', 'CRIA AMAICHA', 'CRIA AMAICHA'],
            'FECHA_HECH': ['01-01-2025', '15-01-2025', '20-01-2025', '25-01-2025', '30-01-2025'],
            'DIA_HECHO': ['MIERCOLES', 'MIERCOLES', 'LUNES', 'SABADO', 'JUEVES'],
            'HORA_HECH': ['10:30', '14:00', '22:15', '03:45', '18:00'],
            'FRAN_HORAR': ['VESPERTINA', 'SIESTA', 'NOCHE', 'MADRUGADA', 'TARDE'],
            'DIREC_HECH': ['Av. San Martin 100', 'Calle Belgrano 200', 'Ruta 307 Km 5', 'Plaza Central', 'B° Norte'],
            'LUGR_HECHO': ['VIA_PUBLICA', 'COMERCIO', 'VIA_PUBLICA', 'VIA_PUBLICA', 'VIVIENDA'],
            'DELITO': ['ROBO AGRAVADO ASALTANTE', 'HURTO PUNGA', 'ROBO ARREBATO', 'TENTATIVA DE ROBO ESCRUCHE', 'HURTO OPORTUNISTA'],
            'MODUS_OPER': ['ASALTANTE', 'PUNGA', 'ARREBATO', 'ESCRUCHE', 'OPORTUNISTA'],
            'VEHIC_UTIL': ['MOTOCICLETA', '{A_PIE}', 'MOTOCICLETA', '{A_PIE}', '{A_PIE}'],
            'ARMA_UTILI': ['{ARMA_BLANCA}', '#NO_CONSTA', '#NO_CONSTA', '#NO_CONSTA', '#NO_CONSTA'],
            'HECH_RESUE': ['01-SIN_RESOLVER', '03-APREHENDIDO', '01-SIN_RESOLVER', '05-IDENTIFICADO', '01-SIN_RESOLVER'],
            'SITUA_CAUS': ['01-PROFUGO', '02-APREHENDIDO', '01-PROFUGO', '03-IDENTIFICADO', '01-PROFUGO'],
            'SEXO_VICTI': ['MASCULINO', 'FEMENINO', 'FEMENINO', 'MASCULINO', 'MASCULINO'],
            'EDAD_VICTI': ['35', '28', '45', '22', '60'],
            'AP_NOM_CAU': ['NN', 'GONZALEZ JUAN', 'NN', 'PEREZ PEDRO', 'NN'],
            'SEXO_CAUS': ['MASCULINO', 'MASCULINO', 'MASCULINO', 'MASCULINO', '#NO_CONSTA'],
            'EDAD_CAUSA': ['25', '30', '20', '18', '#NO_CONSTA'],
            'geometry': [
                Point(-65.9, -26.6),
                Point(-65.91, -26.61),
                Point(-65.92, -26.59),
                Point(-65.89, -26.62),
                Point(-65.88, -26.58)
            ]
        }
        
        gdf = gpd.GeoDataFrame(data, crs="EPSG:4326")
        gdf.to_file(cls.test_shp_path, encoding='utf-8')
    
    @classmethod
    def tearDownClass(cls):
        """Limpiar archivos temporales."""
        shutil.rmtree(cls.temp_dir, ignore_errors=True)
    
    def setUp(self):
        """Configurar reader para cada test."""
        mapper = FieldMapper.from_file(str(BASE_DIR / 'config' / 'field_mappings.json'))
        self.reader = ShapefileReader(mapper)
    
    def test_validate_shapefile(self):
        """Verificar validación de shapefile."""
        validation = self.reader.validate_shapefile(self.test_shp_path)
        
        self.assertTrue(validation['valid'])
        self.assertEqual(validation['records'], 5)
        self.assertEqual(validation['geometry_type'], 'Point')
        self.assertIsNotNone(validation['crs'])
    
    def test_read_hechos(self):
        """Verificar lectura de hechos."""
        records, validation = self.reader.read_hechos(self.test_shp_path)
        
        self.assertTrue(validation['valid'])
        self.assertEqual(len(records), 5)
        
        # Verificar primer registro
        r = records[0]
        self.assertIsInstance(r, CrimeRecord)
        self.assertEqual(r.nro_sumario, '001-2025')
        self.assertEqual(r.delito, 'ROBO AGRAVADO ASALTANTE')
        self.assertIsNotNone(r.fecha)
    
    def test_read_hechos_with_date_filter(self):
        """Verificar filtrado por fechas."""
        fecha_inicio = date(2025, 1, 10)
        fecha_fin = date(2025, 1, 25)
        
        records, validation = self.reader.read_hechos(
            self.test_shp_path,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
        
        # Solo deben incluirse registros entre 10-25 enero
        for r in records:
            if r.fecha:
                self.assertGreaterEqual(r.fecha, fecha_inicio)
                self.assertLessEqual(r.fecha, fecha_fin)


class TestCrimeRecord(unittest.TestCase):
    """Tests para el modelo CrimeRecord."""
    
    def test_categoria_robo(self):
        """Verificar categorización de robos."""
        record = CrimeRecord(
            delito='ROBO AGRAVADO ASALTANTE',
            fecha=date(2025, 1, 1)
        )
        self.assertEqual(record.categoria, CategoriaDelito.ROBO)
    
    def test_categoria_tentativa_robo(self):
        """Verificar categorización de tentativas de robo."""
        record = CrimeRecord(
            delito='TENTATIVA DE ROBO ESCRUCHE',
            fecha=date(2025, 1, 1)
        )
        self.assertEqual(record.categoria, CategoriaDelito.TENTATIVA_ROBO)
    
    def test_categoria_hurto(self):
        """Verificar categorización de hurtos."""
        record = CrimeRecord(
            delito='HURTO PUNGA',
            fecha=date(2025, 1, 1)
        )
        self.assertEqual(record.categoria, CategoriaDelito.HURTO)
    
    def test_categoria_tentativa_hurto(self):
        """Verificar categorización de tentativas de hurto."""
        record = CrimeRecord(
            delito='TENTATIVA DE HURTO MECHERA',
            fecha=date(2025, 1, 1)
        )
        self.assertEqual(record.categoria, CategoriaDelito.TENTATIVA_HURTO)
    
    def test_categoria_estafa(self):
        """Verificar categorización de estafas."""
        record = CrimeRecord(
            delito='ESTAFA CUENTO DEL TIO',
            fecha=date(2025, 1, 1)
        )
        self.assertEqual(record.categoria, CategoriaDelito.ESTAFA)
    
    def test_categoria_otros(self):
        """Verificar categorización de otros delitos."""
        record = CrimeRecord(
            delito='OTRO DELITO NO CLASIFICADO',
            fecha=date(2025, 1, 1)
        )
        self.assertEqual(record.categoria, CategoriaDelito.OTROS)
    
    def test_franja_horaria(self):
        """Verificar cálculo de franja horaria."""
        record = CrimeRecord(
            delito='ROBO',
            fecha=date(2025, 1, 1),
            hora=time(14, 30)  # 14:30 = SIESTA
        )
        self.assertEqual(record.franja_horaria, FranjaHoraria.SIESTA)


class TestConstants(unittest.TestCase):
    """Tests para las constantes del sistema."""
    
    def test_delitos_robo_count(self):
        """Verificar cantidad de delitos de robo."""
        self.assertEqual(len(DELITOS_ROBO), 17)
    
    def test_delitos_tentativa_robo_count(self):
        """Verificar cantidad de tentativas de robo."""
        self.assertEqual(len(DELITOS_TENTATIVA_ROBO), 17)
    
    def test_delitos_hurto_count(self):
        """Verificar cantidad de delitos de hurto."""
        self.assertEqual(len(DELITOS_HURTO), 8)
    
    def test_delitos_tentativa_hurto_count(self):
        """Verificar cantidad de tentativas de hurto."""
        self.assertEqual(len(DELITOS_TENTATIVA_HURTO), 8)
    
    def test_simbolos_delitos(self):
        """Verificar que todos los delitos tienen símbolo."""
        for delito in DELITOS_ROBO:
            self.assertIn(delito, SIMBOLOS_DELITOS, f"Falta símbolo para: {delito}")
        for delito in DELITOS_HURTO:
            self.assertIn(delito, SIMBOLOS_DELITOS, f"Falta símbolo para: {delito}")
    
    def test_default_field_mapping_structure(self):
        """Verificar estructura del mapeo por defecto."""
        self.assertIn('hechos', DEFAULT_FIELD_MAPPING)
        self.assertIn('mencionados', DEFAULT_FIELD_MAPPING)
        self.assertIn('aprehendidos', DEFAULT_FIELD_MAPPING)
        
        # Verificar que hechos tiene los campos truncados DBF
        hechos = DEFAULT_FIELD_MAPPING['hechos']
        self.assertIn('ID_N_SRIO', hechos.get('nro_sumario', []))
        self.assertIn('FECHA_HECH', hechos.get('fecha', []))
        self.assertIn('DELITO', hechos.get('delito', []))
    
    def test_franja_horaria_from_hour(self):
        """Verificar clasificación de franjas horarias."""
        self.assertEqual(FranjaHoraria.from_hour(2), FranjaHoraria.MADRUGADA)
        self.assertEqual(FranjaHoraria.from_hour(7), FranjaHoraria.MANANA)
        self.assertEqual(FranjaHoraria.from_hour(10), FranjaHoraria.VESPERTINA)
        self.assertEqual(FranjaHoraria.from_hour(14), FranjaHoraria.SIESTA)
        self.assertEqual(FranjaHoraria.from_hour(18), FranjaHoraria.TARDE)
        self.assertEqual(FranjaHoraria.from_hour(22), FranjaHoraria.NOCHE)


class TestReportGeneration(unittest.TestCase):
    """Tests para generación de reportes."""
    
    @classmethod
    def setUpClass(cls):
        """Crear datos de prueba."""
        cls.temp_dir = tempfile.mkdtemp()
        cls.test_records = [
            CrimeRecord(
                nro_sumario='001-2025',
                fecha=date(2025, 1, 1),
                hora=time(10, 30),
                delito='ROBO AGRAVADO ASALTANTE',
                modus_operandi='ASALTANTE',
                ambito='VIA_PUBLICA',
                direccion='Av. San Martin 100',
                jurisdiccion='URO_AMAICHA',
                dependencia='CRIA AMAICHA'
            ),
            CrimeRecord(
                nro_sumario='002-2025',
                fecha=date(2025, 1, 15),
                hora=time(14, 0),
                delito='HURTO PUNGA',
                modus_operandi='PUNGA',
                ambito='COMERCIO',
                direccion='Calle Belgrano 200',
                jurisdiccion='URO_AMAICHA',
                dependencia='CRIA AMAICHA'
            ),
        ]
    
    @classmethod
    def tearDownClass(cls):
        """Limpiar archivos temporales."""
        shutil.rmtree(cls.temp_dir, ignore_errors=True)
    
    def test_excel_exporter_import(self):
        """Verificar que el exportador de Excel se puede importar."""
        try:
            from src.reports.excel_exporter import ExcelExporter
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"No se pudo importar ExcelExporter: {e}")
    
    def test_word_exporter_import(self):
        """Verificar que el exportador de Word se puede importar."""
        try:
            from src.reports.word_exporter import WordExporter
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"No se pudo importar WordExporter: {e}")
    
    def test_pdf_exporter_import(self):
        """Verificar que el exportador de PDF se puede importar."""
        try:
            from src.reports.pdf_exporter import PDFExporter
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"No se pudo importar PDFExporter: {e}")
    
    def test_table_generator_import(self):
        """Verificar que el generador de tablas se puede importar."""
        try:
            from src.reports.table_generator import TableGenerator
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"No se pudo importar TableGenerator: {e}")
    
    def test_chart_generator_import(self):
        """Verificar que el generador de gráficos se puede importar."""
        try:
            from src.reports.chart_generator import ChartGenerator
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"No se pudo importar ChartGenerator: {e}")


class TestDataProcessor(unittest.TestCase):
    """Tests para el procesador de datos."""
    
    def test_import(self):
        """Verificar que el procesador de datos se puede importar."""
        try:
            from src.core.data_processor import DataProcessor
            self.assertTrue(True)
        except ImportError as e:
            self.fail(f"No se pudo importar DataProcessor: {e}")


class TestUI(unittest.TestCase):
    """Tests para componentes de la interfaz de usuario."""
    
    def test_main_window_import(self):
        """Verificar que la ventana principal se puede importar."""
        try:
            # Solo importar si PyQt5 está disponible
            import PyQt5
            from src.ui.main_window import MainWindow
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"PyQt5 no disponible: {e}")
    
    def test_widgets_import(self):
        """Verificar que los widgets se pueden importar."""
        try:
            import PyQt5
            from src.ui.widgets.file_selector import FileSelectorWidget
            from src.ui.widgets.period_selector import PeriodSelectorWidget
            self.assertTrue(True)
        except ImportError as e:
            self.skipTest(f"PyQt5 no disponible: {e}")


if __name__ == '__main__':
    # Ejecutar tests
    unittest.main(verbosity=2)
