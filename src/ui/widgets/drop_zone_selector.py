"""
Widget selector de archivos shapefile con drag & drop.

Proporciona interfaz de arrastrar y soltar para cargar múltiples shapefiles.
"""
import os
import re
from pathlib import Path
from typing import Dict, Optional, List, Tuple

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTableWidget, QTableWidgetItem, QComboBox, QHeaderView,
    QGroupBox, QFrame, QFileDialog, QMessageBox, QAbstractItemView
)
from PyQt6.QtCore import pyqtSignal, Qt, QMimeData
from PyQt6.QtGui import QDragEnterEvent, QDropEvent, QDragLeaveEvent


class DropZone(QFrame):
    """Zona de arrastrar y soltar archivos."""
    
    files_dropped = pyqtSignal(list)  # Lista de rutas
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setObjectName("dropZone")
        self._setup_ui()
        self._dragging = False
    
    def _setup_ui(self):
        """Configura la interfaz."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 30, 20, 30)
        layout.setSpacing(12)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Icono
        icon_label = QLabel("📥")
        icon_label.setStyleSheet("font-size: 48px;")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_label)
        
        # Texto principal
        self.text_label = QLabel("Arrastra archivos .shp o una carpeta aquí")
        self.text_label.setObjectName("dropZoneText")
        self.text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.text_label)
        
        # Botón examinar
        btn_browse = QPushButton("📂 Examinar")
        btn_browse.setObjectName("dropZoneBrowse")
        btn_browse.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_browse.clicked.connect(self._on_browse)
        layout.addWidget(btn_browse, alignment=Qt.AlignmentFlag.AlignCenter)
        
        # Texto secundario
        hint_label = QLabel("Soporta: .shp, carpetas con shapefiles")
        hint_label.setObjectName("dropZoneHint")
        hint_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(hint_label)
    
    def _on_browse(self):
        """Abre diálogo para seleccionar archivos o carpeta."""
        # Primero preguntar qué quiere seleccionar
        msg = QMessageBox(self)
        msg.setWindowTitle("Seleccionar")
        msg.setText("¿Qué desea seleccionar?")
        btn_files = msg.addButton("Archivos .shp", QMessageBox.ButtonRole.ActionRole)
        btn_folder = msg.addButton("Carpeta", QMessageBox.ButtonRole.ActionRole)
        msg.addButton(QMessageBox.StandardButton.Cancel)
        msg.exec()
        
        clicked = msg.clickedButton()
        
        if clicked == btn_files:
            files, _ = QFileDialog.getOpenFileNames(
                self,
                "Seleccionar archivos shapefile",
                str(Path.home()),
                "Shapefile (*.shp)"
            )
            if files:
                self.files_dropped.emit(files)
        
        elif clicked == btn_folder:
            folder = QFileDialog.getExistingDirectory(
                self,
                "Seleccionar carpeta con shapefiles",
                str(Path.home())
            )
            if folder:
                self.files_dropped.emit([folder])
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Acepta el drag si contiene archivos."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self._dragging = True
            self.setProperty("dragging", True)
            self.style().unpolish(self)
            self.style().polish(self)
    
    def dragLeaveEvent(self, event: QDragLeaveEvent):
        """Restaura el estilo al salir."""
        self._dragging = False
        self.setProperty("dragging", False)
        self.style().unpolish(self)
        self.style().polish(self)
    
    def dropEvent(self, event: QDropEvent):
        """Procesa los archivos soltados."""
        self._dragging = False
        self.setProperty("dragging", False)
        self.style().unpolish(self)
        self.style().polish(self)
        
        paths = []
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path:
                paths.append(path)
        
        if paths:
            self.files_dropped.emit(paths)
            event.acceptProposedAction()


class DropZoneSelector(QWidget):
    """
    Widget para seleccionar archivos shapefile con drag & drop.
    
    Signals:
        files_changed: Emitido cuando cambian los archivos seleccionados.
    """
    
    files_changed = pyqtSignal(dict)
    
    # Definición de los shapefiles requeridos
    REQUIRED_FILES = {
        'hechos': {
            'label': 'Hechos Delictuales',
            'description': 'Shapefile principal con los hechos delictuales',
            'required': True,
            'patterns': ['hecho', 'delito', 'delict']
        },
        'mencionados': {
            'label': 'Mencionados',
            'description': 'Personas mencionadas como posibles autores',
            'required': False,
            'patterns': ['mencionado', 'menc', 'autor']
        },
        'aprehendidos': {
            'label': 'Aprehendidos',
            'description': 'Personas aprehendidas',
            'required': False,
            'patterns': ['aprehendido', 'apreh', 'detenido']
        },
        'jurisdiccion': {
            'label': 'Jurisdicción',
            'description': 'Límites de la jurisdicción',
            'required': False,
            'patterns': ['jurisdic', 'limite', 'zona']
        },
        'puntos_referencia': {
            'label': 'Puntos de Referencia',
            'description': 'Puntos de interés para el mapa',
            'required': False,
            'patterns': ['referencia', 'punto', 'poi']
        }
    }
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.file_paths: Dict[str, str] = {}  # file_id -> path
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Grupo principal
        group = QGroupBox("📁 ARCHIVOS SHAPEFILE")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(12)
        
        # Zona de drop
        self.drop_zone = DropZone()
        self.drop_zone.files_dropped.connect(self._on_files_dropped)
        group_layout.addWidget(self.drop_zone)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #333344;")
        group_layout.addWidget(separator)
        
        # Tabla de archivos
        self.table = QTableWidget()
        self.table.setObjectName("filesTable")
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Archivo", "Tipo", "Estado", ""])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(1, 180)
        self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 50)
        self.table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setVisible(False)
        self.table.setMinimumHeight(150)
        self.table.setMaximumHeight(250)
        group_layout.addWidget(self.table)
        
        # Botón limpiar
        btn_layout = QHBoxLayout()
        btn_clear = QPushButton("🗑️ Limpiar Todo")
        btn_clear.setProperty("class", "secondary")
        btn_clear.clicked.connect(self._on_clear_all)
        btn_layout.addWidget(btn_clear)
        btn_layout.addStretch()
        
        # Indicador de estado general
        self.status_label = QLabel("")
        self.status_label.setObjectName("generalStatus")
        btn_layout.addWidget(self.status_label)
        
        group_layout.addLayout(btn_layout)
        layout.addWidget(group)
        
        # Actualizar estado inicial
        self._update_status()
    
    def _on_files_dropped(self, paths: List[str]):
        """Procesa los archivos/carpetas soltados."""
        shp_files = []
        
        for path in paths:
            p = Path(path)
            
            if p.is_dir():
                # Buscar .shp en la carpeta (no recursivo)
                shp_files.extend(p.glob("*.shp"))
            elif p.suffix.lower() == '.shp':
                shp_files.append(p)
        
        if not shp_files:
            QMessageBox.warning(
                self,
                "Sin Archivos",
                "No se encontraron archivos .shp en la selección."
            )
            return
        
        # Procesar cada archivo
        added = 0
        for shp_path in shp_files:
            file_id = self._detect_file_type(shp_path.stem)
            
            if file_id:
                # Verificar si ya existe un archivo para este tipo
                if file_id in self.file_paths and self.file_paths[file_id]:
                    existing = Path(self.file_paths[file_id]).name
                    reply = QMessageBox.question(
                        self,
                        "Archivo Duplicado",
                        f"Ya existe un archivo asignado a '{self.REQUIRED_FILES[file_id]['label']}':\n\n"
                        f"Actual: {existing}\n"
                        f"Nuevo: {shp_path.name}\n\n"
                        "¿Desea reemplazarlo?",
                        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                    )
                    if reply != QMessageBox.StandardButton.Yes:
                        continue
                
                self._add_file(file_id, str(shp_path))
                added += 1
            else:
                # No se pudo detectar, permitir asignación manual
                self._add_file_unknown(str(shp_path))
                added += 1
        
        if added > 0:
            self._update_status()
            self.files_changed.emit(self.file_paths)
    
    def _detect_file_type(self, filename: str) -> Optional[str]:
        """Detecta el tipo de archivo por su nombre."""
        name_lower = filename.lower()
        
        for file_id, info in self.REQUIRED_FILES.items():
            for pattern in info['patterns']:
                if pattern in name_lower:
                    return file_id
        
        return None
    
    def _validate_shapefile(self, path: str) -> Tuple[bool, str]:
        """
        Valida que el shapefile tenga archivos asociados.
        
        Returns:
            (es_válido, mensaje)
        """
        p = Path(path)
        
        if not p.exists():
            return False, "Archivo no encontrado"
        
        # Verificar archivos requeridos
        dbf = p.with_suffix('.dbf')
        shx = p.with_suffix('.shx')
        
        missing = []
        if not dbf.exists():
            missing.append('.dbf')
        if not shx.exists():
            missing.append('.shx')
        
        if missing:
            return False, f"Falta: {', '.join(missing)}"
        
        return True, "Válido"
    
    def _add_file(self, file_id: str, path: str):
        """Agrega un archivo a la tabla."""
        self.file_paths[file_id] = path
        
        # Buscar si ya existe una fila para este file_id
        row = self._find_row_by_file_id(file_id)
        
        if row is None:
            # Crear nueva fila
            row = self.table.rowCount()
            self.table.insertRow(row)
        
        # Nombre del archivo
        filename = Path(path).name
        item = QTableWidgetItem(filename)
        item.setData(Qt.ItemDataRole.UserRole, file_id)
        item.setToolTip(path)
        self.table.setItem(row, 0, item)
        
        # ComboBox de tipo
        combo = QComboBox()
        combo.setProperty("row", row)
        for fid, info in self.REQUIRED_FILES.items():
            combo.addItem(info['label'], fid)
        
        # Seleccionar el tipo detectado
        index = combo.findData(file_id)
        if index >= 0:
            combo.setCurrentIndex(index)
        
        combo.currentIndexChanged.connect(lambda idx, r=row: self._on_type_changed(r))
        self.table.setCellWidget(row, 1, combo)
        
        # Estado de validación
        is_valid, message = self._validate_shapefile(path)
        status_item = QTableWidgetItem("✅" if is_valid else "⚠️")
        status_item.setToolTip(message)
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.table.setItem(row, 2, status_item)
        
        # Botón eliminar
        btn_remove = QPushButton("🗑️")
        btn_remove.setMaximumWidth(40)
        btn_remove.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_remove.clicked.connect(lambda checked, r=row: self._on_remove_row(r))
        self.table.setCellWidget(row, 3, btn_remove)
    
    def _add_file_unknown(self, path: str):
        """Agrega un archivo sin tipo detectado."""
        # Buscar el primer tipo sin asignar
        for file_id in self.REQUIRED_FILES.keys():
            if file_id not in self.file_paths or not self.file_paths[file_id]:
                self._add_file(file_id, path)
                return
        
        # Todos los tipos están asignados, preguntar cuál reemplazar
        QMessageBox.information(
            self,
            "Tipos Completos",
            f"Todos los tipos ya tienen un archivo asignado.\n\n"
            f"Archivo: {Path(path).name}\n\n"
            "Cambie el tipo de algún archivo existente para reemplazarlo."
        )
    
    def _find_row_by_file_id(self, file_id: str) -> Optional[int]:
        """Busca la fila que contiene un file_id específico."""
        for row in range(self.table.rowCount()):
            item = self.table.item(row, 0)
            if item and item.data(Qt.ItemDataRole.UserRole) == file_id:
                return row
        return None
    
    def _on_type_changed(self, row: int):
        """Maneja el cambio de tipo en el ComboBox."""
        combo = self.table.cellWidget(row, 1)
        if not combo:
            return
        
        new_file_id = combo.currentData()
        item = self.table.item(row, 0)
        if not item:
            return
        
        old_file_id = item.data(Qt.ItemDataRole.UserRole)
        path = item.toolTip()
        
        # Verificar si el nuevo tipo ya está asignado
        if new_file_id != old_file_id and new_file_id in self.file_paths and self.file_paths[new_file_id]:
            existing_row = self._find_row_by_file_id(new_file_id)
            if existing_row is not None:
                reply = QMessageBox.question(
                    self,
                    "Tipo Duplicado",
                    f"Ya existe un archivo asignado a '{self.REQUIRED_FILES[new_file_id]['label']}'.\n\n"
                    "¿Desea reemplazarlo?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply != QMessageBox.StandardButton.Yes:
                    # Restaurar el tipo anterior
                    index = combo.findData(old_file_id)
                    combo.blockSignals(True)
                    combo.setCurrentIndex(index)
                    combo.blockSignals(False)
                    return
                else:
                    # Eliminar la fila existente
                    self._remove_row_internal(existing_row)
        
        # Actualizar file_paths
        if old_file_id in self.file_paths:
            del self.file_paths[old_file_id]
        
        self.file_paths[new_file_id] = path
        item.setData(Qt.ItemDataRole.UserRole, new_file_id)
        
        self._update_status()
        self.files_changed.emit(self.file_paths)
    
    def _on_remove_row(self, row: int):
        """Elimina una fila de la tabla."""
        item = self.table.item(row, 0)
        if item:
            file_id = item.data(Qt.ItemDataRole.UserRole)
            if file_id in self.file_paths:
                del self.file_paths[file_id]
        
        self.table.removeRow(row)
        
        # Actualizar referencias de filas en los botones
        self._update_row_references()
        
        self._update_status()
        self.files_changed.emit(self.file_paths)
    
    def _remove_row_internal(self, row: int):
        """Elimina una fila sin emitir señales."""
        item = self.table.item(row, 0)
        if item:
            file_id = item.data(Qt.ItemDataRole.UserRole)
            if file_id in self.file_paths:
                del self.file_paths[file_id]
        
        self.table.removeRow(row)
        self._update_row_references()
    
    def _update_row_references(self):
        """Actualiza las referencias de fila en combos y botones."""
        for row in range(self.table.rowCount()):
            # Actualizar combo
            combo = self.table.cellWidget(row, 1)
            if combo:
                combo.setProperty("row", row)
            
            # Reconectar botón eliminar
            btn = self.table.cellWidget(row, 3)
            if btn:
                try:
                    btn.clicked.disconnect()
                except:
                    pass
                btn.clicked.connect(lambda checked, r=row: self._on_remove_row(r))
    
    def _on_clear_all(self):
        """Limpia todos los archivos."""
        self.file_paths.clear()
        self.table.setRowCount(0)
        self._update_status()
        self.files_changed.emit(self.file_paths)
    
    def _update_status(self):
        """Actualiza el indicador de estado general."""
        total = len(self.file_paths)
        required_ok = True
        
        for file_id, info in self.REQUIRED_FILES.items():
            if info['required']:
                if file_id not in self.file_paths or not self.file_paths[file_id]:
                    required_ok = False
                    break
                if not Path(self.file_paths[file_id]).exists():
                    required_ok = False
                    break
        
        if total == 0:
            self.status_label.setText("")
        elif required_ok:
            self.status_label.setText(f"✅ {total} archivo(s) cargado(s)")
            self.status_label.setStyleSheet("color: #00ff88;")
        else:
            self.status_label.setText(f"⚠️ Falta: Hechos Delictuales")
            self.status_label.setStyleSheet("color: #ffaa00;")
    
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
                if file_id not in self.file_paths or not self.file_paths[file_id]:
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
