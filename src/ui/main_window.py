"""
Ventana principal de S.I.D.I.C.

Interfaz gráfica principal de la aplicación con estilo policial ultramoderno.
"""
import sys
from pathlib import Path
from datetime import date, datetime
from typing import Optional, Dict, Any

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QTabWidget, QStatusBar, QMenuBar, QMenu,
    QMessageBox, QFileDialog, QProgressBar, QFrame, QSplitter,
    QTextEdit, QGroupBox, QCheckBox, QComboBox, QScrollArea
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QAction, QFont, QIcon, QPixmap

from .widgets import DropZoneSelector, PeriodSelector, ComparativePeriodSelector


class ReportGeneratorThread(QThread):
    """
    Hilo para generar reportes en segundo plano.
    
    Signals:
        progress: (int, str) - Porcentaje y mensaje de progreso.
        finished: (bool, str, str) - Éxito, ruta del archivo, mensaje.
        error: (str) - Mensaje de error.
    """
    
    progress = pyqtSignal(int, str)
    finished = pyqtSignal(bool, str, str)
    error = pyqtSignal(str)
    
    def __init__(
        self,
        files: Dict[str, str],
        periods: list,
        options: Dict[str, Any],
        output_path: str
    ):
        super().__init__()
        self.files = files
        self.periods = periods
        self.options = options
        self.output_path = output_path
    
    def run(self):
        """Ejecuta la generación del reporte."""
        try:
            self.progress.emit(5, "Cargando módulos...")
            
            # Agregar path del proyecto para imports
            import sys
            from pathlib import Path
            project_root = str(Path(__file__).parent.parent.parent)
            if project_root not in sys.path:
                sys.path.insert(0, project_root)
            
            from src.core.data_processor import DataProcessor
            from src.core.field_mapper import FieldMapper
            from src.reports.table_generator import TableGenerator
            from src.reports.chart_generator import ChartGenerator
            from src.reports.excel_exporter import ExcelExporter
            from src.reports.word_exporter import WordExporter
            from src.reports.pdf_exporter import PDFExporter
            
            self.progress.emit(10, "Configurando mapeo de campos...")
            
            # Configurar field mapper
            field_mapper = FieldMapper()
            
            self.progress.emit(15, "Cargando shapefiles...")
            
            # Procesar datos
            processor = DataProcessor(field_mapper=field_mapper)
            
            # Cargar cada shapefile
            if self.files.get('hechos'):
                processor.load_hechos(self.files['hechos'])
            if self.files.get('mencionados'):
                processor.load_mencionados(self.files['mencionados'])
            if self.files.get('aprehendidos'):
                processor.load_aprehendidos(self.files['aprehendidos'])
            if self.files.get('jurisdiccion'):
                processor.load_jurisdiccion(self.files['jurisdiccion'])
            
            self.progress.emit(30, "Filtrando por período...")
            
            # Obtener período principal
            start_date, end_date = self.periods[0]
            
            self.progress.emit(40, "Generando reporte...")
            
            # Crear reporte
            if len(self.periods) > 1:
                # Reporte comparativo - crear lista de periodos con nombres
                periodos_formateados = []
                for i, (inicio, fin) in enumerate(self.periods):
                    nombre = f"Período {i + 1}"
                    periodos_formateados.append((nombre, inicio, fin))
                
                report = processor.create_report(
                    periodos_formateados,
                    titulo=self.options.get('titulo', 'Informe Delictual')
                )
            else:
                # Reporte simple
                report = processor.create_single_period_report(
                    start_date,
                    end_date,
                    titulo=self.options.get('titulo', 'Informe Delictual')
                )
            
            self.progress.emit(50, "Generando tablas...")
            
            # Generar tablas
            table_gen = TableGenerator(report)
            tables = table_gen.generar_todas()
            
            self.progress.emit(60, "Generando gráficos...")
            
            # Generar gráficos
            chart_gen = ChartGenerator(report)
            charts = {}
            
            output_dir = Path(self.output_path).parent / "graficos"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            if self.options.get('incluir_graficos', True):
                charts = chart_gen.generar_todos(str(output_dir))
                
                # Convertir a bytes para exportadores
                charts_bytes = {}
                for name, path in charts.items():
                    with open(path, 'rb') as f:
                        charts_bytes[name] = f.read()
                charts = charts_bytes
            
            # Exportar según formato
            output_format = self.options.get('formato', 'excel')
            
            if output_format == 'excel':
                self.progress.emit(75, "Exportando a Excel...")
                
                excel_path = self.output_path
                if not excel_path.endswith('.xlsx'):
                    excel_path += '.xlsx'
                
                exporter = ExcelExporter(report)
                success = exporter.export(excel_path, tables, charts, self.options)
                
                if success:
                    self.finished.emit(True, excel_path, "Reporte Excel generado exitosamente")
                else:
                    self.error.emit("Error al generar el archivo Excel")
            
            elif output_format == 'word':
                self.progress.emit(75, "Exportando a Word...")
                
                word_path = self.output_path
                if not word_path.endswith('.docx'):
                    word_path += '.docx'
                
                exporter = WordExporter(report)
                success = exporter.export(word_path, tables, charts, self.options)
                
                if success:
                    self.finished.emit(True, word_path, "Reporte Word generado exitosamente")
                else:
                    error_detail = exporter.get_last_error() or "Error desconocido"
                    self.error.emit(f"Error al generar el archivo Word: {error_detail}")
            
            elif output_format == 'pdf':
                self.progress.emit(70, "Exportando a Word...")
                
                word_path = str(Path(self.output_path).with_suffix('.docx'))
                
                exporter = WordExporter(report)
                success = exporter.export(word_path, tables, charts, self.options)
                
                if not success:
                    self.error.emit("Error al generar el archivo Word intermedio")
                    return
                
                self.progress.emit(85, "Convirtiendo a PDF...")
                
                pdf_path = self.output_path
                if not pdf_path.endswith('.pdf'):
                    pdf_path += '.pdf'
                
                pdf_exporter = PDFExporter()
                success = pdf_exporter.export(word_path, pdf_path)
                
                if success:
                    self.finished.emit(True, pdf_path, "Reporte PDF generado exitosamente")
                else:
                    self.error.emit(
                        "Error al convertir a PDF. "
                        "Se generó el archivo Word como alternativa."
                    )
            
            elif output_format == 'todos':
                # Generar todos los formatos
                base_path = Path(self.output_path)
                
                self.progress.emit(70, "Exportando a Excel...")
                excel_path = str(base_path.with_suffix('.xlsx'))
                excel_exp = ExcelExporter(report)
                excel_exp.export(excel_path, tables, charts, self.options)
                
                self.progress.emit(80, "Exportando a Word...")
                word_path = str(base_path.with_suffix('.docx'))
                word_exp = WordExporter(report)
                word_exp.export(word_path, tables, charts, self.options)
                
                self.progress.emit(90, "Convirtiendo a PDF...")
                pdf_path = str(base_path.with_suffix('.pdf'))
                pdf_exp = PDFExporter()
                pdf_exp.export(word_path, pdf_path)
                
                self.finished.emit(
                    True,
                    str(base_path.parent),
                    "Todos los formatos generados exitosamente"
                )
            
            self.progress.emit(100, "¡Completado!")
        
        except Exception as e:
            self.error.emit(f"Error durante la generación: {str(e)}")


class MainWindow(QMainWindow):
    """
    Ventana principal de S.I.D.I.C.
    
    Interfaz completa para la generación de informes delictuales.
    """
    
    def __init__(self):
        super().__init__()
        self.generator_thread: Optional[ReportGeneratorThread] = None
        self._setup_window()
        self._setup_menu()
        self._setup_ui()
        self._setup_statusbar()
        self._load_styles()
    
    def _setup_window(self):
        """Configura la ventana principal."""
        self.setWindowTitle("S.I.D.I.C - Sistema de Información Delictual e Inteligencia Criminal")
        self.setMinimumSize(1200, 800)
        
        # Centrar en pantalla
        screen = QApplication.primaryScreen().geometry()
        x = (screen.width() - 1200) // 2
        y = (screen.height() - 800) // 2
        self.setGeometry(x, y, 1200, 800)
    
    def _setup_menu(self):
        """Configura el menú principal."""
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("&Archivo")
        
        action_new = QAction("🆕 Nuevo Reporte", self)
        action_new.setShortcut("Ctrl+N")
        action_new.triggered.connect(self._on_new_report)
        file_menu.addAction(action_new)
        
        action_open = QAction("📂 Abrir Proyecto", self)
        action_open.setShortcut("Ctrl+O")
        action_open.triggered.connect(self._on_open_project)
        file_menu.addAction(action_open)
        
        action_save = QAction("💾 Guardar Proyecto", self)
        action_save.setShortcut("Ctrl+S")
        action_save.triggered.connect(self._on_save_project)
        file_menu.addAction(action_save)
        
        file_menu.addSeparator()
        
        action_exit = QAction("🚪 Salir", self)
        action_exit.setShortcut("Ctrl+Q")
        action_exit.triggered.connect(self.close)
        file_menu.addAction(action_exit)
        
        # Menú Herramientas
        tools_menu = menubar.addMenu("&Herramientas")
        
        action_config = QAction("⚙️ Configuración", self)
        action_config.triggered.connect(self._on_open_config)
        tools_menu.addAction(action_config)
        
        action_fields = QAction("📋 Mapeo de Campos", self)
        action_fields.triggered.connect(self._on_open_field_mapper)
        tools_menu.addAction(action_fields)
        
        # Menú Ayuda
        help_menu = menubar.addMenu("A&yuda")
        
        action_help = QAction("📖 Manual de Usuario", self)
        action_help.setShortcut("F1")
        action_help.triggered.connect(self._on_show_help)
        help_menu.addAction(action_help)
        
        action_about = QAction("ℹ️ Acerca de", self)
        action_about.triggered.connect(self._on_show_about)
        help_menu.addAction(action_about)
    
    def _setup_ui(self):
        """Configura la interfaz de usuario principal."""
        central = QWidget()
        self.setCentralWidget(central)
        
        main_layout = QVBoxLayout(central)
        main_layout.setContentsMargins(16, 16, 16, 16)
        main_layout.setSpacing(16)
        
        # ─────────────────────────────────────────────────────────────────
        # ENCABEZADO
        # ─────────────────────────────────────────────────────────────────
        header = self._create_header()
        main_layout.addWidget(header)
        
        # ─────────────────────────────────────────────────────────────────
        # CONTENIDO PRINCIPAL (TABS)
        # ─────────────────────────────────────────────────────────────────
        self.tabs = QTabWidget()
        
        # Tab: Reporte Simple
        tab_simple = self._create_simple_report_tab()
        self.tabs.addTab(tab_simple, "📊 Reporte Simple")
        
        # Tab: Reporte Comparativo
        tab_comparative = self._create_comparative_report_tab()
        self.tabs.addTab(tab_comparative, "📈 Comparativo")
        
        # Tab: Vista Previa
        tab_preview = self._create_preview_tab()
        self.tabs.addTab(tab_preview, "👁️ Vista Previa")
        
        # Conectar cambio de tab para actualizar opciones
        self.tabs.currentChanged.connect(self._on_tab_changed)
        
        main_layout.addWidget(self.tabs, 1)
        
        # ─────────────────────────────────────────────────────────────────
        # BARRA DE PROGRESO Y BOTONES
        # ─────────────────────────────────────────────────────────────────
        footer = self._create_footer()
        main_layout.addWidget(footer)
    
    def _create_header(self) -> QWidget:
        """Crea el encabezado con logo y título."""
        header = QFrame()
        header.setStyleSheet("""
            QFrame {
                background: qlineargradient(
                    x1: 0, y1: 0, x2: 1, y2: 0,
                    stop: 0 #0a0a12,
                    stop: 0.5 #12121c,
                    stop: 1 #0a0a12
                );
                border: none;
                border-bottom: 2px solid #00d4ff;
                padding: 16px;
            }
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Logo (texto estilizado)
        logo_container = QVBoxLayout()
        
        title = QLabel("S.I.D.I.C")
        title.setObjectName("titleLabel")
        title.setStyleSheet("""
            QLabel {
                color: #00d4ff;
                font-size: 32pt;
                font-weight: bold;
                letter-spacing: 8px;
            }
        """)
        logo_container.addWidget(title)
        
        subtitle = QLabel("Sistema de Información Delictual e Inteligencia Criminal")
        subtitle.setObjectName("subtitleLabel")
        subtitle.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 10pt;
                letter-spacing: 2px;
            }
        """)
        logo_container.addWidget(subtitle)
        
        layout.addLayout(logo_container)
        layout.addStretch()
        
        # Estadísticas rápidas (se actualizan al cargar datos)
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(24)
        
        self.stat_hechos = self._create_stat_card("0", "Hechos")
        stats_layout.addWidget(self.stat_hechos)
        
        self.stat_mencionados = self._create_stat_card("0", "Mencionados")
        stats_layout.addWidget(self.stat_mencionados)
        
        self.stat_aprehendidos = self._create_stat_card("0", "Aprehendidos")
        stats_layout.addWidget(self.stat_aprehendidos)
        
        layout.addLayout(stats_layout)
        
        return header
    
    def _create_stat_card(self, value: str, label: str) -> QFrame:
        """Crea una tarjeta de estadística."""
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #12121c;
                border: 1px solid #333344;
                border-radius: 8px;
                padding: 8px 16px;
            }
            QFrame:hover {
                border-color: #00d4ff;
            }
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(0)
        
        value_label = QLabel(value)
        value_label.setStyleSheet("""
            QLabel {
                color: #00d4ff;
                font-size: 20pt;
                font-weight: bold;
            }
        """)
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label)
        
        text_label = QLabel(label)
        text_label.setStyleSheet("""
            QLabel {
                color: #888888;
                font-size: 9pt;
            }
        """)
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text_label)
        
        # Guardar referencia al valor
        card.value_label = value_label
        
        return card
    
    def _create_simple_report_tab(self) -> QWidget:
        """Crea el tab de reporte simple."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(16)
        
        # Scroll area para el contenido
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(16)
        
        # Selector de archivos (zona drag & drop)
        self.file_selector = DropZoneSelector()
        content_layout.addWidget(self.file_selector)
        
        # Selector de período
        self.period_selector = PeriodSelector()
        content_layout.addWidget(self.period_selector)
        
        # Opciones de exportación
        options_group = QGroupBox("⚙️ OPCIONES DE EXPORTACIÓN")
        options_layout = QVBoxLayout(options_group)
        options_layout.setSpacing(12)
        
        # Formato de salida
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Formato de salida:"))
        
        self.combo_format = QComboBox()
        self.combo_format.addItems([
            "Excel (.xlsx)",
            "Word (.docx)",
            "PDF (.pdf)",
            "Todos los formatos"
        ])
        format_layout.addWidget(self.combo_format)
        format_layout.addStretch()
        options_layout.addLayout(format_layout)
        
        # Checkboxes
        checks_layout = QHBoxLayout()
        
        self.check_graficos = QCheckBox("Incluir gráficos")
        self.check_graficos.setChecked(True)
        checks_layout.addWidget(self.check_graficos)
        
        self.check_cuadro_ref = QCheckBox("Cuadro de referencia")
        self.check_cuadro_ref.setChecked(True)
        checks_layout.addWidget(self.check_cuadro_ref)
        
        self.check_mencionados = QCheckBox("Lista de mencionados")
        self.check_mencionados.setChecked(True)
        checks_layout.addWidget(self.check_mencionados)
        
        self.check_matrices = QCheckBox("Matrices cruzadas")
        self.check_matrices.setChecked(True)
        checks_layout.addWidget(self.check_matrices)
        
        self.check_comparativos = QCheckBox("Cuadros comparativos")
        self.check_comparativos.setChecked(True)
        self.check_comparativos.setEnabled(False)  # Deshabilitado hasta que haya múltiples períodos
        self.check_comparativos.setToolTip("Disponible solo en reportes comparativos con múltiples períodos")
        checks_layout.addWidget(self.check_comparativos)
        
        checks_layout.addStretch()
        options_layout.addLayout(checks_layout)
        
        content_layout.addWidget(options_group)
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab
    
    def _create_comparative_report_tab(self) -> QWidget:
        """Crea el tab de reporte comparativo."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 16, 0, 0)
        layout.setSpacing(16)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content = QWidget()
        content_layout = QVBoxLayout(content)
        content_layout.setSpacing(16)
        
        # Info
        info = QLabel(
            "Los reportes comparativos permiten analizar las variaciones "
            "entre diferentes períodos de tiempo, mostrando tendencias y "
            "porcentajes de cambio."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #888888; padding: 8px;")
        content_layout.addWidget(info)
        
        # Selector de períodos comparativos
        self.comparative_periods = ComparativePeriodSelector()
        content_layout.addWidget(self.comparative_periods)
        
        # Conectar señal para habilitar/deshabilitar checkbox de comparativos
        self.comparative_periods.periods_changed.connect(self._on_periods_changed)
        
        content_layout.addStretch()
        
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        return tab
    
    def _create_preview_tab(self) -> QWidget:
        """Crea el tab de vista previa."""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        layout.setContentsMargins(0, 16, 0, 0)
        
        # Placeholder
        placeholder = QLabel(
            "📋 Vista Previa\n\n"
            "Aquí se mostrará una vista previa del reporte\n"
            "una vez que se carguen los datos."
        )
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("""
            QLabel {
                color: #666666;
                font-size: 14pt;
                padding: 48px;
            }
        """)
        layout.addWidget(placeholder)
        
        return tab
    
    def _create_footer(self) -> QWidget:
        """Crea el pie de página con progreso y botones."""
        footer = QFrame()
        footer.setStyleSheet("""
            QFrame {
                background-color: #0d0d18;
                border: 1px solid #333344;
                border-radius: 8px;
                padding: 12px;
            }
        """)
        
        layout = QVBoxLayout(footer)
        layout.setSpacing(12)
        
        # Barra de progreso
        progress_layout = QHBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        progress_layout.addWidget(self.progress_bar)
        
        self.progress_label = QLabel("")
        self.progress_label.setStyleSheet("color: #00d4ff;")
        self.progress_label.setVisible(False)
        progress_layout.addWidget(self.progress_label)
        
        layout.addLayout(progress_layout)
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(12)
        
        btn_layout.addStretch()
        
        self.btn_preview = QPushButton("👁️ Vista Previa")
        self.btn_preview.setProperty("class", "secondary")
        self.btn_preview.clicked.connect(self._on_preview)
        btn_layout.addWidget(self.btn_preview)
        
        self.btn_generate = QPushButton("🚀 GENERAR REPORTE")
        self.btn_generate.setMinimumWidth(200)
        self.btn_generate.clicked.connect(self._on_generate)
        btn_layout.addWidget(self.btn_generate)
        
        layout.addLayout(btn_layout)
        
        return footer
    
    def _setup_statusbar(self):
        """Configura la barra de estado."""
        self.statusbar = QStatusBar()
        self.setStatusBar(self.statusbar)
        
        self.status_label = QLabel("Listo")
        self.statusbar.addWidget(self.status_label)
        
        self.statusbar.addPermanentWidget(QLabel(f"v1.0.0"))
    
    def _load_styles(self):
        """Carga los estilos QSS."""
        style_path = Path(__file__).parent / "styles" / "police_dark.qss"
        
        if style_path.exists():
            with open(style_path, 'r', encoding='utf-8') as f:
                self.setStyleSheet(f.read())
    
    # ═══════════════════════════════════════════════════════════════════════
    # ACCIONES DEL MENÚ
    # ═══════════════════════════════════════════════════════════════════════
    
    def _on_new_report(self):
        """Inicia un nuevo reporte."""
        # Limpiar formularios
        self.file_selector._on_clear_all()
        self.tabs.setCurrentIndex(0)
        self.status_label.setText("Nuevo reporte iniciado")
    
    def _on_open_project(self):
        """Abre un proyecto guardado."""
        QMessageBox.information(
            self,
            "Próximamente",
            "Esta función estará disponible en futuras versiones."
        )
    
    def _on_save_project(self):
        """Guarda el proyecto actual."""
        QMessageBox.information(
            self,
            "Próximamente",
            "Esta función estará disponible en futuras versiones."
        )
    
    def _on_open_config(self):
        """Abre la configuración."""
        QMessageBox.information(
            self,
            "Próximamente",
            "Esta función estará disponible en futuras versiones."
        )
    
    def _on_open_field_mapper(self):
        """Abre el mapeo de campos."""
        QMessageBox.information(
            self,
            "Próximamente",
            "Esta función estará disponible en futuras versiones."
        )
    
    def _on_show_help(self):
        """Muestra la ayuda."""
        QMessageBox.information(
            self,
            "Ayuda",
            "S.I.D.I.C - Sistema de Información Delictual e Inteligencia Criminal\n\n"
            "1. Seleccione los archivos shapefile de QGIS\n"
            "2. Configure el período de análisis\n"
            "3. Ajuste las opciones de exportación\n"
            "4. Haga clic en 'Generar Reporte'\n\n"
            "Para más información, consulte el manual de usuario."
        )
    
    def _on_show_about(self):
        """Muestra información sobre la aplicación."""
        QMessageBox.about(
            self,
            "Acerca de S.I.D.I.C",
            "<h2>S.I.D.I.C</h2>"
            "<p><b>Sistema de Información Delictual e Inteligencia Criminal</b></p>"
            "<p>Versión 1.0.0</p>"
            "<hr>"
            "<p>Aplicación para el procesamiento de datos geográficos "
            "delictuales provenientes de QGIS 2.14.14 y generación "
            "de informes estadísticos profesionales.</p>"
            "<hr>"
            "<p>Desarrollado con ❤️ para la seguridad ciudadana.</p>"
        )
    
    # ═══════════════════════════════════════════════════════════════════════
    # ACCIONES PRINCIPALES
    # ═══════════════════════════════════════════════════════════════════════
    
    def _on_preview(self):
        """Genera una vista previa."""
        if not self.file_selector.validate():
            return
        
        self.tabs.setCurrentIndex(2)  # Tab de vista previa
        self.status_label.setText("Vista previa generada")
    
    def _on_generate(self):
        """Genera el reporte."""
        # Verificar si hay datos cargados (archivos O datos demo)
        has_files = bool(self.file_selector.get_files())
        has_demo_data = hasattr(self, 'processor') and self.processor is not None and self.processor.is_loaded
        
        if not has_files and not has_demo_data:
            # No hay ningún dato, ofrecer opciones
            msg = QMessageBox(self)
            msg.setIcon(QMessageBox.Icon.Warning)
            msg.setWindowTitle("Sin Datos")
            msg.setText("No hay datos cargados para generar el informe.")
            msg.setInformativeText("Puede cargar archivos shapefile o usar datos de demostración.")
            
            btn_demo = msg.addButton("🎭 Cargar Datos Demo", QMessageBox.ButtonRole.ActionRole)
            btn_cancel = msg.addButton(QMessageBox.StandardButton.Cancel)
            
            msg.exec()
            
            if msg.clickedButton() == btn_demo:
                self._on_load_demo_data()
            return
        
        # Validar archivos (solo si hay archivos seleccionados)
        if has_files and not self.file_selector.validate():
            return
        
        # Validar período según el tab activo
        if self.tabs.currentIndex() == 0:  # Reporte simple
            if not self.period_selector.validate():
                QMessageBox.warning(self, "Error", "El período seleccionado no es válido.")
                return
            periods = [self.period_selector.get_period()]
        else:  # Reporte comparativo
            if not self.comparative_periods.validate():
                QMessageBox.warning(self, "Error", "Los períodos seleccionados no son válidos.")
                return
            periods = self.comparative_periods.get_periods()
        
        # Seleccionar archivo de salida
        format_idx = self.combo_format.currentIndex()
        format_map = {
            0: ('excel', "Excel (*.xlsx)"),
            1: ('word', "Word (*.docx)"),
            2: ('pdf', "PDF (*.pdf)"),
            3: ('todos', "Todos los archivos (*.*)")
        }
        output_format, filter_str = format_map.get(format_idx, ('excel', "Excel (*.xlsx)"))
        
        output_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Reporte",
            str(Path.home() / "Documents" / f"Informe_Delictual_{datetime.now().strftime('%Y%m%d')}"),
            filter_str
        )
        
        if not output_path:
            return
        
        # Configurar opciones
        options = {
            'formato': output_format,
            'incluir_graficos': self.check_graficos.isChecked(),
            'incluir_cuadro_ref': self.check_cuadro_ref.isChecked(),
            'incluir_mencionados': self.check_mencionados.isChecked(),
            'incluir_matrices': self.check_matrices.isChecked(),
            'incluir_comparativos': self.check_comparativos.isChecked() and self.check_comparativos.isEnabled(),
            'titulo': 'Informe Delictual',
            'jurisdiccion': ''
        }
        
        # Iniciar generación
        self._start_generation(
            self.file_selector.get_files(),
            periods,
            options,
            output_path
        )
    
    def _start_generation(
        self,
        files: Dict[str, str],
        periods: list,
        options: Dict[str, Any],
        output_path: str
    ):
        """Inicia la generación del reporte en segundo plano."""
        # Deshabilitar controles
        self.btn_generate.setEnabled(False)
        self.btn_preview.setEnabled(False)
        
        # Mostrar progreso
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.progress_label.setVisible(True)
        self.progress_label.setText("Iniciando...")
        
        # Crear thread
        self.generator_thread = ReportGeneratorThread(
            files, periods, options, output_path
        )
        
        self.generator_thread.progress.connect(self._on_progress)
        self.generator_thread.finished.connect(self._on_generation_finished)
        self.generator_thread.error.connect(self._on_generation_error)
        
        self.generator_thread.start()
    
    def _on_progress(self, value: int, message: str):
        """Actualiza el progreso."""
        self.progress_bar.setValue(value)
        self.progress_label.setText(message)
        self.status_label.setText(message)
    
    def _on_generation_finished(self, success: bool, path: str, message: str):
        """Maneja la finalización de la generación."""
        self.btn_generate.setEnabled(True)
        self.btn_preview.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        if success:
            QMessageBox.information(
                self,
                "Reporte Generado",
                f"{message}\n\nArchivo: {path}"
            )
            self.status_label.setText("✅ " + message)
        else:
            self.status_label.setText("⚠️ Generación completada con advertencias")
    
    def _on_generation_error(self, error: str):
        """Maneja errores de generación con opción de ver detalles."""
        self.btn_generate.setEnabled(True)
        self.btn_preview.setEnabled(True)
        self.progress_bar.setVisible(False)
        self.progress_label.setVisible(False)
        
        # Crear mensaje con detalles expandibles
        msg = QMessageBox(self)
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setWindowTitle("Error en la Generación")
        msg.setText("Ocurrió un error durante la generación del reporte.")
        msg.setInformativeText("Haga clic en 'Mostrar detalles...' para más información.")
        msg.setDetailedText(error)  # Botón "Ver Detalles" automático
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
        
        self.status_label.setText("❌ Error en la generación")
    
    def _on_periods_changed(self, periods: list):
        """
        Actualiza el estado del checkbox de comparativos según los períodos.
        
        Args:
            periods: Lista de tuplas (fecha_inicio, fecha_fin)
        """
        has_multiple = len(periods) > 1
        self.check_comparativos.setEnabled(has_multiple)
        
        if has_multiple:
            self.check_comparativos.setToolTip("Incluir cuadros comparativos entre períodos")
        else:
            self.check_comparativos.setChecked(False)
            self.check_comparativos.setToolTip("Disponible solo en reportes comparativos con múltiples períodos")
    
    def _on_tab_changed(self, index: int):
        """
        Actualiza el estado del checkbox de comparativos según el tab activo.
        
        Args:
            index: Índice del tab activo (0=simple, 1=comparativo)
        """
        if index == 0:  # Tab de reporte simple
            self.check_comparativos.setEnabled(False)
            self.check_comparativos.setChecked(False)
            self.check_comparativos.setToolTip("Disponible solo en reportes comparativos")
        else:  # Tab de reporte comparativo
            # Verificar si hay múltiples períodos
            periods = self.comparative_periods.get_periods()
            has_multiple = len(periods) > 1
            self.check_comparativos.setEnabled(has_multiple)
            if has_multiple:
                self.check_comparativos.setChecked(True)
                self.check_comparativos.setToolTip("Incluir cuadros comparativos entre períodos")


def run_app():
    """Función principal para ejecutar la aplicación."""
    app = QApplication(sys.argv)
    app.setApplicationName("S.I.D.I.C")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("Policia")
    
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    run_app()
