"""
Script de prueba para verificar que el filtrado por categorías funciona sin errores.
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.models.crime_record import CrimeRecord
from src.models.mentioned_person import MentionedPerson
from src.models.apprehended import Apprehended
from src.core.data_processor import DataProcessor
from datetime import date

def test_category_filtering_with_related_data():
    """Prueba el filtrado por categorías con mencionados y aprehendidos."""
    
    print("=" * 70)
    print("TEST DE FILTRADO POR CATEGORÍAS CON DATOS RELACIONADOS")
    print("=" * 70)
    
    # Crear procesador
    processor = DataProcessor()
    
    # Simular datos cargados
    processor._hechos = [
        CrimeRecord(
            delito="ROBO AGRAVADO ASALTANTE", 
            fecha=date(2024, 1, 15),
            nro_sumario="SUM-001"
        ),
        CrimeRecord(
            delito="HURTO PUNGA", 
            fecha=date(2024, 1, 16),
            nro_sumario="SUM-002"
        ),
        CrimeRecord(
            delito="ESTAFA CUENTO DEL TIO", 
            fecha=date(2024, 1, 17),
            nro_sumario="SUM-003"
        ),
        CrimeRecord(
            delito="TENTATIVA DE ROBO ARREBATO", 
            fecha=date(2024, 1, 18),
            nro_sumario="SUM-004"
        ),
    ]
    
    processor._mencionados = [
        MentionedPerson(alias="Juan Pérez", fecha=date(2024, 1, 15)),
        MentionedPerson(alias="María García", fecha=date(2024, 1, 17)),
        MentionedPerson(alias="Carlos López", fecha=date(2024, 1, 18)),
    ]
    
    processor._aprehendidos = [
        Apprehended(nombre="Pedro Sánchez", fecha=date(2024, 1, 15)),
        Apprehended(nombre="Ana Martínez", fecha=date(2024, 1, 16)),
    ]
    
    print("\n1. Datos de prueba:")
    print("-" * 70)
    print(f"   Hechos totales: {len(processor._hechos)}")
    print(f"   Mencionados totales: {len(processor._mencionados)}")
    print(f"   Aprehendidos totales: {len(processor._aprehendidos)}")
    
    # Test 1: Sin filtrado de categorías (None)
    print("\n2. Test: Sin filtrado de categorías (comportamiento original)")
    print("-" * 70)
    try:
        period_data = processor.create_period_data(
            "Período de prueba",
            date(2024, 1, 1),
            date(2024, 1, 31),
            categorias_incluidas=None
        )
        print(f"   ✓ Hechos: {len(period_data.hechos)}")
        print(f"   ✓ Mencionados: {len(period_data.mencionados)}")
        print(f"   ✓ Aprehendidos: {len(period_data.aprehendidos)}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 2: Filtrar solo ROBOS (excluir estafas)
    print("\n3. Test: Filtrar solo ROBOS (excluir estafas y hurtos)")
    print("-" * 70)
    try:
        period_data = processor.create_period_data(
            "Período de prueba",
            date(2024, 1, 1),
            date(2024, 1, 31),
            categorias_incluidas=['ROBOS', 'TENTATIVA DE ROBOS']
        )
        print(f"   ✓ Hechos filtrados: {len(period_data.hechos)}")
        for h in period_data.hechos:
            print(f"      - {h.delito} ({h.categoria.value})")
        print(f"   ✓ Mencionados (sin filtrar): {len(period_data.mencionados)}")
        print(f"   ✓ Aprehendidos (sin filtrar): {len(period_data.aprehendidos)}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 3: Excluir ESTAFAS
    print("\n4. Test: Excluir ESTAFAS")
    print("-" * 70)
    try:
        period_data = processor.create_period_data(
            "Período de prueba",
            date(2024, 1, 1),
            date(2024, 1, 31),
            categorias_incluidas=['ROBOS', 'TENTATIVA DE ROBOS', 'HURTOS', 
                                'TENTATIVA DE HURTOS', 'OTROS DELITOS']
        )
        print(f"   ✓ Hechos (sin estafas): {len(period_data.hechos)}")
        for h in period_data.hechos:
            print(f"      - {h.delito} ({h.categoria.value})")
        print(f"   ✓ Mencionados: {len(period_data.mencionados)}")
        print(f"   ✓ Aprehendidos: {len(period_data.aprehendidos)}")
        
        # Verificar que no hay estafas
        tiene_estafas = any(h.categoria.value == 'ESTAFAS' for h in period_data.hechos)
        if tiene_estafas:
            print("   ✗ ERROR: Se encontraron estafas cuando deberían estar filtradas")
            return False
        else:
            print("   ✓ Verificado: No hay estafas en los resultados")
            
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 4: Crear reporte completo
    print("\n5. Test: Crear reporte completo con filtrado")
    print("-" * 70)
    try:
        report = processor.create_single_period_report(
            date(2024, 1, 1),
            date(2024, 1, 31),
            titulo="Informe de Prueba",
            categorias_incluidas=['ROBOS', 'TENTATIVA DE ROBOS', 'HURTOS', 
                                'TENTATIVA DE HURTOS', 'OTROS DELITOS']
        )
        print(f"   ✓ Reporte creado exitosamente")
        print(f"   ✓ Períodos: {len(report.periodos)}")
        print(f"   ✓ Hechos en período principal: {len(report.periodo_principal.hechos)}")
    except Exception as e:
        print(f"   ✗ Error al crear reporte: {e}")
        return False
    
    print("\n" + "=" * 70)
    print("✓ TODOS LOS TESTS PASARON EXITOSAMENTE")
    print("=" * 70)
    print("\nNota: Mencionados y aprehendidos no se filtran por categoría")
    print("      porque no existe campo de relación directa con los hechos.")
    print("      Solo se filtran por período temporal.")
    return True

if __name__ == "__main__":
    success = test_category_filtering_with_related_data()
    sys.exit(0 if success else 1)
