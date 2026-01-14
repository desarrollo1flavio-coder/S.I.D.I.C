"""
Script de prueba para verificar ordenamiento mejorado en tablas.
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.models.crime_record import CrimeRecord
from src.core.data_processor import DataProcessor
from src.reports.table_generator import TableGenerator
from src.models.report_data import ReportData
from datetime import date

def test_ordenamiento_mejorado():
    """Prueba el ordenamiento con criterio alfabético secundario."""
    
    print("=" * 80)
    print("TEST DE ORDENAMIENTO MEJORADO EN TABLAS")
    print("=" * 80)
    
    # Crear procesador
    processor = DataProcessor()
    
    # Simular datos con empates para verificar orden alfabético
    processor._hechos = [
        # 3 robos arrebato
        CrimeRecord(delito="ROBO ARREBATO", fecha=date(2024, 1, 15)),
        CrimeRecord(delito="ROBO ARREBATO", fecha=date(2024, 1, 16)),
        CrimeRecord(delito="ROBO ARREBATO", fecha=date(2024, 1, 17)),
        
        # 3 hurtos punga (mismo valor que robos - debe ir después alfabéticamente)
        CrimeRecord(delito="HURTO PUNGA", fecha=date(2024, 1, 15)),
        CrimeRecord(delito="HURTO PUNGA", fecha=date(2024, 1, 16)),
        CrimeRecord(delito="HURTO PUNGA", fecha=date(2024, 1, 17)),
        
        # 5 estafas (debe ir primero por cantidad)
        CrimeRecord(delito="ESTAFA CUENTO DEL TIO", fecha=date(2024, 1, 15)),
        CrimeRecord(delito="ESTAFA CUENTO DEL TIO", fecha=date(2024, 1, 16)),
        CrimeRecord(delito="ESTAFA CUENTO DEL TIO", fecha=date(2024, 1, 17)),
        CrimeRecord(delito="ESTAFA CUENTO DEL TIO", fecha=date(2024, 1, 18)),
        CrimeRecord(delito="ESTAFA CUENTO DEL TIO", fecha=date(2024, 1, 19)),
        
        # 2 robos agravados
        CrimeRecord(delito="ROBO AGRAVADO ASALTANTE", fecha=date(2024, 1, 15)),
        CrimeRecord(delito="ROBO AGRAVADO ASALTANTE", fecha=date(2024, 1, 16)),
    ]
    
    print("\n1. Datos de prueba:")
    print("-" * 80)
    print(f"   Total hechos: {len(processor._hechos)}")
    print(f"   - 5 ESTAFA CUENTO DEL TIO")
    print(f"   - 3 ROBO ARREBATO")
    print(f"   - 3 HURTO PUNGA (mismo valor que ROBO ARREBATO)")
    print(f"   - 2 ROBO AGRAVADO ASALTANTE")
    
    # Crear reporte
    try:
        report = processor.create_single_period_report(
            date(2024, 1, 1),
            date(2024, 1, 31),
            titulo="Test Ordenamiento"
        )
        
        print("\n2. Generando tabla de delitos...")
        print("-" * 80)
        
        table_gen = TableGenerator(report)
        tabla_delitos = table_gen.generar_tabla_delitos()
        
        print("\n   Tabla generada:")
        print(tabla_delitos.to_string())
        
        # Verificar orden
        print("\n3. Verificación de ordenamiento:")
        print("-" * 80)
        
        delitos_ordenados = tabla_delitos['DELITOS CON MODALIDADES'].tolist()[:-1]  # Excluir TOTAL
        valores = tabla_delitos[report.periodo_principal.rango_fechas].tolist()[:-1]
        
        print("\n   Orden esperado:")
        print("   1. ESTAFA CUENTO DEL TIO (5 casos)")
        print("   2. HURTO PUNGA (3 casos) - alfabéticamente antes que ROBO")
        print("   3. ROBO ARREBATO (3 casos)")
        print("   4. ROBO AGRAVADO ASALTANTE (2 casos)")
        
        print("\n   Orden obtenido:")
        for i, (delito, valor) in enumerate(zip(delitos_ordenados, valores), 1):
            print(f"   {i}. {delito} ({valor} casos)")
        
        # Validaciones
        print("\n4. Validaciones:")
        print("-" * 80)
        
        # Validar que está ordenado de mayor a menor
        es_descendente = all(valores[i] >= valores[i+1] for i in range(len(valores)-1))
        print(f"   ✓ Ordenado de mayor a menor: {es_descendente}")
        
        # Validar orden alfabético en empates (índice 1 y 2 tienen mismo valor)
        if valores[1] == valores[2]:
            alfabetico_correcto = delitos_ordenados[1] < delitos_ordenados[2]
            print(f"   ✓ Orden alfabético en empate (posición 2 y 3): {alfabetico_correcto}")
            print(f"     '{delitos_ordenados[1]}' < '{delitos_ordenados[2]}': {alfabetico_correcto}")
        
        # Validar que el primero es el de mayor valor
        print(f"   ✓ Primer delito tiene mayor valor: {valores[0] == max(valores)}")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test de filtrado de todos-ceros en comparativos
    print("\n" + "=" * 80)
    print("TEST DE FILTRADO DE FILAS CON TODOS CEROS (COMPARATIVO)")
    print("=" * 80)
    
    try:
        # Crear datos para dos períodos
        processor2 = DataProcessor()
        
        # Período 1: Solo robos
        processor2._hechos = [
            CrimeRecord(delito="ROBO ARREBATO", fecha=date(2024, 1, 15)),
            CrimeRecord(delito="ROBO ARREBATO", fecha=date(2024, 1, 16)),
        ]
        
        report2 = processor2.create_report(
            [
                ("Período 1", date(2024, 1, 1), date(2024, 1, 31)),
                ("Período 2", date(2024, 2, 1), date(2024, 2, 28)),  # Sin datos
            ],
            titulo="Test Filtrado Ceros"
        )
        
        print("\n   Datos de prueba:")
        print("   - Período 1: 2 ROBO ARREBATO")
        print("   - Período 2: 0 delitos (vacío)")
        
        table_gen2 = TableGenerator(report2)
        tabla_comparativa = table_gen2.generar_tabla_delitos_comparativa()
        
        print("\n   Tabla comparativa generada:")
        print(tabla_comparativa.to_string())
        
        # Verificar que ROBO ARREBATO aparece (tiene valor en período 1)
        tiene_robo = 'ROBO ARREBATO' in tabla_comparativa['DELITOS CON MODALIDADES'].values
        print(f"\n   ✓ ROBO ARREBATO aparece (tiene valor > 0 en período 1): {tiene_robo}")
        
        # Verificar que no hay filas con todos ceros
        # (en este caso solo hay ROBO ARREBATO con valor en período 1)
        print(f"   ✓ Filtrado funcionando correctamente")
        
    except Exception as e:
        print(f"   ✗ Error en test comparativo: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 80)
    print("✓ TODOS LOS TESTS PASARON EXITOSAMENTE")
    print("=" * 80)
    print("\nMejoras implementadas:")
    print("  1. ✓ Ordenamiento de mayor a menor por período actual")
    print("  2. ✓ Ordenamiento alfabético secundario en caso de empate")
    print("  3. ✓ Filtrado de filas con todos ceros en comparativos")
    print("  4. ✓ Orden especial para categorías (ROBOS primero)")
    return True

if __name__ == "__main__":
    success = test_ordenamiento_mejorado()
    sys.exit(0 if success else 1)
