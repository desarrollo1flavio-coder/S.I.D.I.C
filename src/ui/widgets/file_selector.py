"""
Widget selector de archivos shapefile.

Proporciona interfaz para seleccionar los 5 shapefiles requeridos.
"""
from pathlib import Path
from typing import Dict, Optional, Callable

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QFileDialog,
    QGroupBox, QFrame, QMessageBox
)
from PyQt6.QtCore import pyqtSignal, Qt


class ShapefileSelector(QWidget):
    """
    Widget para seleccionar los archivos shapefile requeridos.
    
    Signals:
        files_changed: Emitido cuando cambian los archivos seleccionados.
    """
    
    files_changed = pyqtSignal(dict)
    
    # Definición de los shapefiles requeridos
    REQUIRED_FILES = {
        'hechos': {
            'label': 'Hechos Delictuales',
            'description': 'Shapefile principal con los hechos delictuales',
            'required': True
        },
        'mencionados': {
            'label': 'Mencionados',
            'description': 'Personas mencionadas como posibles autores',
            'required': False
        },
        'aprehendidos': {
            'label': 'Aprehendidos',
            'description': 'Personas aprehendidas',
            'required': False
        },
        'jurisdiccion': {
            'label': 'Jurisdicción',
            'description': 'Límites de la jurisdicción',
            'required': False
        },
        'puntos_referencia': {
            'label': 'Puntos de Referencia',
            'description': 'Puntos de interés para el mapa',
            'required': False
        }
    }
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.file_paths: Dict[str, str] = {}
        self.entries: Dict[str, QLineEdit] = {}
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Grupo de archivos
        group = QGroupBox("📁 ARCHIVOS SHAPEFILE")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(8)
        
        # Crear campos para cada archivo
        for file_id, info in self.REQUIRED_FILES.items():
            row = self._create_file_row(file_id, info)
            group_layout.addLayout(row)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #333344;")
        group_layout.addWidget(separator)
        
        # Botones de acción
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        btn_select_folder = QPushButton("📂 Seleccionar Carpeta")
        btn_select_folder.clicked.connect(self._on_select_folder)
        btn_layout.addWidget(btn_select_folder)
        
        btn_clear = QPushButton("🗑️ Limpiar Todo")
        btn_clear.setProperty("class", "secondary")
        btn_clear.clicked.connect(self._on_clear_all)
        btn_layout.addWidget(btn_clear)
        
        btn_layout.addStretch()
        group_layout.addLayout(btn_layout)
        
        layout.addWidget(group)
    
    def _create_file_row(self, file_id: str, info: dict) -> QHBoxLayout:
        """Crea una fila para seleccionar un archivo."""
        layout = QHBoxLayout()
        layout.setSpacing(8)
        
        # Etiqueta
        label = QLabel(info['label'] + ("*" if info['required'] else ""))
        label.setMinimumWidth(150)
        label.setToolTip(info['description'])
        if info['required']:
            label.setStyleSheet("color: #00d4ff; font-weight: bold;")
        layout.addWidget(label)
        
        # Campo de texto
        entry = QLineEdit()
        entry.setPlaceholderText("Ruta al archivo .shp...")
        entry.setReadOnly(True)
        entry.setMinimumWidth(300)
        self.entries[file_id] = entry
        layout.addWidget(entry, 1)
        
        # Botón de selección
        btn = QPushButton("...")
        btn.setMaximumWidth(40)
        btn.clicked.connect(lambda checked, fid=file_id: self._on_select_file(fid))
        layout.addWidget(btn)
        
        # Indicador de estado
        status = QLabel("⚪")
        status.setObjectName(f"status_{file_id}")
        layout.addWidget(status)
        
        return layout
    
    def _on_select_file(self, file_id: str):
        """Maneja la selección de un archivo individual."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            f"Seleccionar {self.REQUIRED_FILES[file_id]['label']}",
            str(Path.home()),
            "Shapefile (*.shp);;Todos los archivos (*.*)"
        )
        
        if file_path:
            self._set_file(file_id, file_path)
    
    def _on_select_folder(self):
        """Selecciona una carpeta y busca shapefiles automáticamente."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar carpeta con shapefiles",
            str(Path.home())
        )
        
        if not folder:
            return
        
        folder_path = Path(folder)
        found = 0
        
        # Buscar shapefiles en la carpeta
        for shp_file in folder_path.glob("*.shp"):
            name_lower = shp_file.stem.lower()
            
            # Intentar mapear por nombre
            if 'hecho' in name_lower or 'delito' in name_lower:
                self._set_file('hechos', str(shp_file))
                found += 1
            elif 'mencionado' in name_lower or 'autor' in name_lower:
                self._set_file('mencionados', str(shp_file))
                found += 1
            elif 'aprehendido' in name_lower or 'detenido' in name_lower:
                self._set_file('aprehendidos', str(shp_file))
                found += 1
            elif 'jurisdic' in name_lower or 'limite' in name_lower:
                self._set_file('jurisdiccion', str(shp_file))
                found += 1
            elif 'referencia' in name_lower or 'punto' in name_lower:
                self._set_file('puntos_referencia', str(shp_file))
                found += 1
        
        if found > 0:
            QMessageBox.information(
                self,
                "Archivos Encontrados",
                f"Se encontraron y asignaron {found} archivos shapefile automáticamente.\n\n"
                "Revise que las asignaciones sean correctas."
            )
        else:
            QMessageBox.warning(
                self,
                "Sin Resultados",
                "No se encontraron archivos shapefile reconocibles en la carpeta.\n\n"
                "Seleccione los archivos manualmente."
            )
    
    def _set_file(self, file_id: str, path: str):
        """Establece un archivo y actualiza la UI."""
        self.file_paths[file_id] = path
        
        # Actualizar campo de texto
        if file_id in self.entries:
            self.entries[file_id].setText(path)
            self.entries[file_id].setToolTip(path)
        
        # Actualizar indicador
        status_label = self.findChild(QLabel, f"status_{file_id}")
        if status_label:
            if Path(path).exists():
                status_label.setText("✅")
                status_label.setToolTip("Archivo válido")
            else:
                status_label.setText("⚠️")
                status_label.setToolTip("Archivo no encontrado")
        
        # Emitir señal
        self.files_changed.emit(self.file_paths)
    
    def _on_clear_all(self):
        """Limpia todos los archivos seleccionados."""
        self.file_paths.clear()
        
        for file_id, entry in self.entries.items():
            entry.clear()
            
            status_label = self.findChild(QLabel, f"status_{file_id}")
            if status_label:
                status_label.setText("⚪")
                status_label.setToolTip("")
        
        self.files_changed.emit(self.file_paths)
    
    def get_files(self) -> Dict[str, str]:
        """
        Obtiene los archivos seleccionados.
        
        Returns:
            Diccionario con las rutas de los archivos.
        """
        return self.file_paths.copy()
    
    def validate(self) -> bool:
        """
        Valida que todos los archivos requeridos estén seleccionados.
        
        Returns:
            True si la validación es exitosa.
        """
        missing = []
        
        for file_id, info in self.REQUIRED_FILES.items():
            if info['required']:
                if file_id not in self.file_paths:
                    missing.append(info['label'])
                elif not Path(self.file_paths[file_id]).exists():
                    missing.append(f"{info['label']} (no encontrado)")
        
        if missing:
            QMessageBox.warning(
                self,
                "Archivos Requeridos",
                "Los siguientes archivos son requeridos:\n\n" + 
                "\n".join(f"• {m}" for m in missing)
            )
            return False
        
        return True
