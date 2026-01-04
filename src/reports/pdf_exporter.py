"""
Exportador a PDF.

Convierte documentos Word a PDF.
"""
from pathlib import Path
from typing import Optional
import subprocess
import platform

try:
    from docx2pdf import convert
    HAS_DOCX2PDF = True
except ImportError:
    HAS_DOCX2PDF = False


class PDFExporter:
    """
    Exportador de documentos Word a PDF.
    
    Utiliza docx2pdf (requiere Microsoft Word en Windows)
    o LibreOffice en otros sistemas.
    """
    
    def __init__(self):
        """Inicializa el exportador."""
        self.system = platform.system()
    
    def export(self, docx_path: str, pdf_path: Optional[str] = None) -> bool:
        """
        Convierte un archivo Word a PDF.
        
        Args:
            docx_path: Ruta al archivo .docx
            pdf_path: Ruta de salida para el PDF. 
                      Si no se especifica, usa el mismo nombre con extensión .pdf
        
        Returns:
            True si se convirtió correctamente.
        """
        docx_path = Path(docx_path)
        
        if not docx_path.exists():
            print(f"Archivo no encontrado: {docx_path}")
            return False
        
        if pdf_path is None:
            pdf_path = docx_path.with_suffix('.pdf')
        else:
            pdf_path = Path(pdf_path)
        
        # Crear directorio si no existe
        pdf_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Intentar con docx2pdf primero (Windows con Word)
        if HAS_DOCX2PDF and self.system == 'Windows':
            return self._convert_with_docx2pdf(str(docx_path), str(pdf_path))
        
        # Intentar con LibreOffice
        return self._convert_with_libreoffice(str(docx_path), str(pdf_path))
    
    def _convert_with_docx2pdf(self, docx_path: str, pdf_path: str) -> bool:
        """Convierte usando docx2pdf (Windows + Word)."""
        try:
            convert(docx_path, pdf_path)
            return Path(pdf_path).exists()
        except Exception as e:
            print(f"Error con docx2pdf: {e}")
            # Intentar con LibreOffice como fallback
            return self._convert_with_libreoffice(docx_path, pdf_path)
    
    def _convert_with_libreoffice(self, docx_path: str, pdf_path: str) -> bool:
        """Convierte usando LibreOffice."""
        # Buscar LibreOffice
        libreoffice_paths = []
        
        if self.system == 'Windows':
            libreoffice_paths = [
                r"C:\Program Files\LibreOffice\program\soffice.exe",
                r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            ]
        elif self.system == 'Darwin':  # macOS
            libreoffice_paths = [
                "/Applications/LibreOffice.app/Contents/MacOS/soffice",
            ]
        else:  # Linux
            libreoffice_paths = [
                "/usr/bin/libreoffice",
                "/usr/bin/soffice",
            ]
        
        soffice = None
        for path in libreoffice_paths:
            if Path(path).exists():
                soffice = path
                break
        
        if not soffice:
            print("LibreOffice no encontrado. Por favor instale LibreOffice para generar PDF.")
            return False
        
        try:
            # Convertir
            output_dir = str(Path(pdf_path).parent)
            
            result = subprocess.run(
                [
                    soffice,
                    '--headless',
                    '--convert-to', 'pdf',
                    '--outdir', output_dir,
                    docx_path
                ],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode != 0:
                print(f"Error LibreOffice: {result.stderr}")
                return False
            
            # LibreOffice genera el archivo con el mismo nombre
            generated_pdf = Path(output_dir) / (Path(docx_path).stem + '.pdf')
            
            # Renombrar si es necesario
            if str(generated_pdf) != pdf_path and generated_pdf.exists():
                generated_pdf.rename(pdf_path)
            
            return Path(pdf_path).exists()
        
        except subprocess.TimeoutExpired:
            print("Timeout al convertir a PDF")
            return False
        except Exception as e:
            print(f"Error al convertir a PDF: {e}")
            return False
    
    def is_available(self) -> bool:
        """
        Verifica si la conversión a PDF está disponible.
        
        Returns:
            True si hay algún método disponible para convertir.
        """
        if HAS_DOCX2PDF and self.system == 'Windows':
            return True
        
        # Verificar LibreOffice
        if self.system == 'Windows':
            paths = [
                r"C:\Program Files\LibreOffice\program\soffice.exe",
                r"C:\Program Files (x86)\LibreOffice\program\soffice.exe",
            ]
        elif self.system == 'Darwin':
            paths = ["/Applications/LibreOffice.app/Contents/MacOS/soffice"]
        else:
            paths = ["/usr/bin/libreoffice", "/usr/bin/soffice"]
        
        return any(Path(p).exists() for p in paths)
