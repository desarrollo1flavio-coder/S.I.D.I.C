"""
S.I.D.I.C - Sistema de Información Delictual e Inteligencia Criminal

Punto de entrada principal de la aplicación.
"""
import sys
import os
from pathlib import Path

# Agregar el directorio src al path
src_dir = Path(__file__).parent
if str(src_dir) not in sys.path:
    sys.path.insert(0, str(src_dir))


def check_dependencies():
    """Verifica que las dependencias estén instaladas."""
    missing = []
    
    try:
        import PyQt6
    except ImportError:
        missing.append("PyQt6")
    
    try:
        import pandas
    except ImportError:
        missing.append("pandas")
    
    try:
        import geopandas
    except ImportError:
        missing.append("geopandas")
    
    try:
        import matplotlib
    except ImportError:
        missing.append("matplotlib")
    
    try:
        import openpyxl
    except ImportError:
        missing.append("openpyxl")
    
    if missing:
        print("=" * 60)
        print("ERROR: Faltan dependencias requeridas")
        print("=" * 60)
        print("\nPor favor instale las siguientes dependencias:")
        print()
        for dep in missing:
            print(f"  pip install {dep}")
        print()
        print("O instale todas con:")
        print()
        print("  pip install -r requirements.txt")
        print("=" * 60)
        sys.exit(1)


def main():
    """Función principal."""
    print()
    print("═" * 60)
    print("  S.I.D.I.C")
    print("  Sistema de Información Delictual e Inteligencia Criminal")
    print("═" * 60)
    print()
    
    # Verificar dependencias
    print("Verificando dependencias...")
    check_dependencies()
    print("✅ Todas las dependencias están instaladas")
    print()
    
    # Iniciar aplicación
    print("Iniciando interfaz gráfica...")
    print()
    
    from ui.main_window import run_app
    run_app()


def main_cli():
    """Punto de entrada para uso por línea de comandos."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='S.I.D.I.C - Sistema de Información Delictual e Inteligencia Criminal',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python main.py                    # Inicia la interfaz gráfica
  python main.py --gui              # Inicia la interfaz gráfica
  python main.py --cli --help       # Muestra ayuda del modo CLI
  
  python main.py --cli \\
    --hechos "C:/datos/hechos.shp" \\
    --inicio 2024-01-01 \\
    --fin 2024-01-31 \\
    --salida "C:/reportes/informe.xlsx"
        """
    )
    
    parser.add_argument(
        '--gui',
        action='store_true',
        help='Iniciar interfaz gráfica (por defecto)'
    )
    
    parser.add_argument(
        '--cli',
        action='store_true',
        help='Modo línea de comandos'
    )
    
    parser.add_argument(
        '--hechos',
        type=str,
        help='Ruta al shapefile de hechos delictuales'
    )
    
    parser.add_argument(
        '--mencionados',
        type=str,
        help='Ruta al shapefile de mencionados (opcional)'
    )
    
    parser.add_argument(
        '--aprehendidos',
        type=str,
        help='Ruta al shapefile de aprehendidos (opcional)'
    )
    
    parser.add_argument(
        '--inicio',
        type=str,
        help='Fecha de inicio (formato: YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--fin',
        type=str,
        help='Fecha de fin (formato: YYYY-MM-DD)'
    )
    
    parser.add_argument(
        '--salida',
        type=str,
        help='Ruta del archivo de salida'
    )
    
    parser.add_argument(
        '--formato',
        type=str,
        choices=['excel', 'word', 'pdf', 'todos'],
        default='excel',
        help='Formato de salida (default: excel)'
    )
    
    parser.add_argument(
        '--jurisdiccion',
        type=str,
        default='',
        help='Nombre de la jurisdicción'
    )
    
    parser.add_argument(
        '--titulo',
        type=str,
        default='Informe Delictual',
        help='Título del informe'
    )
    
    args = parser.parse_args()
    
    # Verificar dependencias
    check_dependencies()
    
    if args.cli:
        # Modo CLI
        if not args.hechos:
            parser.error("--hechos es requerido en modo CLI")
        if not args.inicio or not args.fin:
            parser.error("--inicio y --fin son requeridos en modo CLI")
        if not args.salida:
            parser.error("--salida es requerido en modo CLI")
        
        run_cli(args)
    else:
        # Modo GUI (por defecto)
        from ui.main_window import run_app
        run_app()


def run_cli(args):
    """Ejecuta el procesamiento en modo CLI."""
    from datetime import datetime
    from core.data_processor import DataProcessor
    from core.field_mapper import FieldMapper
    from reports.table_generator import TableGenerator
    from reports.chart_generator import ChartGenerator
    from reports.excel_exporter import ExcelExporter
    from reports.word_exporter import WordExporter
    from reports.pdf_exporter import PDFExporter
    
    print()
    print("═" * 60)
    print("  PROCESANDO...")
    print("═" * 60)
    print()
    
    try:
        # Parsear fechas
        fecha_inicio = datetime.strptime(args.inicio, '%Y-%m-%d').date()
        fecha_fin = datetime.strptime(args.fin, '%Y-%m-%d').date()
        
        print(f"📁 Cargando shapefile: {args.hechos}")
        
        # Procesar
        field_mapper = FieldMapper()
        processor = DataProcessor(
            hechos_path=args.hechos,
            mencionados_path=args.mencionados,
            aprehendidos_path=args.aprehendidos,
            field_mapper=field_mapper
        )
        
        print(f"📅 Período: {fecha_inicio} a {fecha_fin}")
        
        report = processor.create_report(
            fecha_inicio,
            fecha_fin,
            titulo=args.titulo,
            jurisdiccion=args.jurisdiccion
        )
        
        print(f"📊 Generando tablas...")
        table_gen = TableGenerator(report)
        tables = table_gen.generar_todas()
        
        print(f"📈 Generando gráficos...")
        chart_gen = ChartGenerator(report)
        
        output_dir = Path(args.salida).parent / "graficos"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        chart_paths = chart_gen.generar_todos(str(output_dir))
        
        # Cargar gráficos como bytes
        charts = {}
        for name, path in chart_paths.items():
            with open(path, 'rb') as f:
                charts[name] = f.read()
        
        # Exportar
        print(f"💾 Exportando a {args.formato}...")
        
        output_path = Path(args.salida)
        
        if args.formato == 'excel' or args.formato == 'todos':
            excel_path = str(output_path.with_suffix('.xlsx'))
            exporter = ExcelExporter(report)
            exporter.export(excel_path, tables, charts)
            print(f"   ✅ Excel: {excel_path}")
        
        if args.formato == 'word' or args.formato == 'todos':
            word_path = str(output_path.with_suffix('.docx'))
            exporter = WordExporter(report)
            exporter.export(word_path, tables, charts)
            print(f"   ✅ Word: {word_path}")
        
        if args.formato == 'pdf' or args.formato == 'todos':
            word_path = str(output_path.with_suffix('.docx'))
            
            # Generar Word si no existe
            if args.formato == 'pdf':
                exporter = WordExporter(report)
                exporter.export(word_path, tables, charts)
            
            pdf_path = str(output_path.with_suffix('.pdf'))
            pdf_exporter = PDFExporter()
            
            if pdf_exporter.export(word_path, pdf_path):
                print(f"   ✅ PDF: {pdf_path}")
            else:
                print(f"   ⚠️ PDF: No se pudo generar (Word disponible)")
        
        print()
        print("═" * 60)
        print("  ✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("═" * 60)
        print()
    
    except Exception as e:
        print()
        print("═" * 60)
        print(f"  ❌ ERROR: {e}")
        print("═" * 60)
        print()
        sys.exit(1)


if __name__ == '__main__':
    # Usar main() para GUI simple o main_cli() para soporte CLI
    if len(sys.argv) > 1 and '--cli' in sys.argv:
        main_cli()
    else:
        main()
