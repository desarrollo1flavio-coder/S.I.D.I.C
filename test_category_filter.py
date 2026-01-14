"""
Script de prueba para verificar el filtrado por categorías de delitos.
"""
import sys
from pathlib import Path

# Agregar el directorio raíz al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.models.crime_record import CrimeRecord
from src.core.data_processor import DataProcessor
from src.utils.constants import CategoriaDelito
from datetime import date

def test_category_filtering():
    """Prueba el filtrado por categorías."""
    
    # Crear registros de prueba
    test_hechos = [
        CrimeRecord(delito="ROBO AGRAVADO ASALTANTE", fecha=date(2024, 1, 15)),
        CrimeRecord(delito="HURTO PUNGA", fecha=date(2024, 1, 16)),
        CrimeRecord(delito="ESTAFA CUENTO DEL TIO", fecha=date(2024, 1, 17)),
        CrimeRecord(delito="TENTATIVA DE ROBO ARREBATO", fecha=date(2024, 1, 18)),
        CrimeRecord(delito="OTRO DELITO", fecha=date(2024, 1, 19)),
    ]
    
    print("=" * 60)
    print("TEST DE FILTRADO POR CATEGORÍAS")
    print("=" * 60)
    
    # Verificar categorización
    print("\n1. Verificando categorización automática:")
    print("-" * 60)
    for hecho in test_hechos:
        print(f"   Delito: {hecho.delito:40} -> {hecho.categoria.value}")
    
    # Crear procesador y probar filtrado
    processor = DataProcessor()
    
    # Test 1: Filtrar solo ROBOS
    print("\n2. Test: Filtrar solo ROBOS")
    print("-" * 60)
    categorias = ['ROBOS', 'TENTATIVA DE ROBOS']
    filtered = processor.filter_by_categories(test_hechos, categorias)
    print(f"   Categorías incluidas: {categorias}")
    print(f"   Total original: {len(test_hechos)}")
    print(f"   Total filtrado: {len(filtered)}")
    for hecho in filtered:
        print(f"   - {hecho.delito}")
    
    # Test 2: Filtrar solo ESTAFAS
    print("\n3. Test: Filtrar solo ESTAFAS")
    print("-" * 60)
    categorias = ['ESTAFAS']
    filtered = processor.filter_by_categories(test_hechos, categorias)
    print(f"   Categorías incluidas: {categorias}")
    print(f"   Total filtrado: {len(filtered)}")
    for hecho in filtered:
        print(f"   - {hecho.delito}")
    
    # Test 3: Excluir ESTAFAS (incluir todo menos estafas)
    print("\n4. Test: Excluir ESTAFAS (incluir ROBOS, HURTOS, OTROS)")
    print("-" * 60)
    categorias = ['ROBOS', 'TENTATIVA DE ROBOS', 'HURTOS', 'TENTATIVA DE HURTOS', 'OTROS DELITOS']
    filtered = processor.filter_by_categories(test_hechos, categorias)
    print(f"   Categorías incluidas: {categorias}")
    print(f"   Total filtrado: {len(filtered)}")
    for hecho in filtered:
        print(f"   - {hecho.delito}")
    
    # Test 4: Lista vacía (debe incluir todos)
    print("\n5. Test: Lista vacía (debe incluir todos)")
    print("-" * 60)
    categorias = []
    filtered = processor.filter_by_categories(test_hechos, categorias)
    print(f"   Categorías incluidas: {categorias}")
    print(f"   Total filtrado: {len(filtered)}")
    
    print("\n" + "=" * 60)
    print("✓ Tests completados exitosamente")
    print("=" * 60)

if __name__ == "__main__":
    test_category_filtering()
