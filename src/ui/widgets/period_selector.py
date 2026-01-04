"""
Widget selector de período.

Permite seleccionar fechas de inicio y fin para el análisis.
"""
from datetime import date, timedelta
from typing import Optional, Tuple

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QDateEdit, QGroupBox,
    QRadioButton, QButtonGroup, QFrame, QSpinBox
)
from PyQt6.QtCore import pyqtSignal, Qt, QDate


class PeriodSelector(QWidget):
    """
    Widget para seleccionar el período de análisis.
    
    Soporta tanto selección manual de fechas como períodos predefinidos.
    
    Signals:
        period_changed: Emitido cuando cambia el período seleccionado.
    """
    
    period_changed = pyqtSignal(date, date)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Grupo principal
        group = QGroupBox("📅 PERÍODO DE ANÁLISIS")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(12)
        
        # Opciones rápidas
        quick_layout = QHBoxLayout()
        quick_layout.setSpacing(8)
        
        quick_label = QLabel("Período rápido:")
        quick_layout.addWidget(quick_label)
        
        self.btn_last_week = QPushButton("Última Semana")
        self.btn_last_week.setProperty("class", "secondary")
        self.btn_last_week.clicked.connect(lambda: self._set_quick_period(7))
        quick_layout.addWidget(self.btn_last_week)
        
        self.btn_last_month = QPushButton("Último Mes")
        self.btn_last_month.setProperty("class", "secondary")
        self.btn_last_month.clicked.connect(lambda: self._set_quick_period(30))
        quick_layout.addWidget(self.btn_last_month)
        
        self.btn_last_quarter = QPushButton("Último Trimestre")
        self.btn_last_quarter.setProperty("class", "secondary")
        self.btn_last_quarter.clicked.connect(lambda: self._set_quick_period(90))
        quick_layout.addWidget(self.btn_last_quarter)
        
        quick_layout.addStretch()
        group_layout.addLayout(quick_layout)
        
        # Separador
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #333344;")
        group_layout.addWidget(separator)
        
        # Fechas manuales
        dates_layout = QGridLayout()
        dates_layout.setSpacing(12)
        
        # Fecha inicio
        dates_layout.addWidget(QLabel("Fecha Inicio:"), 0, 0)
        self.date_start = QDateEdit()
        self.date_start.setCalendarPopup(True)
        self.date_start.setDisplayFormat("dd/MM/yyyy")
        self.date_start.setDate(QDate.currentDate().addDays(-30))
        self.date_start.dateChanged.connect(self._on_date_changed)
        dates_layout.addWidget(self.date_start, 0, 1)
        
        # Fecha fin
        dates_layout.addWidget(QLabel("Fecha Fin:"), 0, 2)
        self.date_end = QDateEdit()
        self.date_end.setCalendarPopup(True)
        self.date_end.setDisplayFormat("dd/MM/yyyy")
        self.date_end.setDate(QDate.currentDate())
        self.date_end.dateChanged.connect(self._on_date_changed)
        dates_layout.addWidget(self.date_end, 0, 3)
        
        # Días totales
        self.label_days = QLabel("30 días")
        self.label_days.setStyleSheet("color: #00d4ff; font-weight: bold;")
        dates_layout.addWidget(self.label_days, 0, 4)
        
        group_layout.addLayout(dates_layout)
        layout.addWidget(group)
        
        # Actualizar días
        self._update_days_label()
    
    def _set_quick_period(self, days: int):
        """Establece un período rápido."""
        end_date = QDate.currentDate()
        start_date = end_date.addDays(-days)
        
        self.date_start.blockSignals(True)
        self.date_end.blockSignals(True)
        
        self.date_start.setDate(start_date)
        self.date_end.setDate(end_date)
        
        self.date_start.blockSignals(False)
        self.date_end.blockSignals(False)
        
        self._on_date_changed()
    
    def _on_date_changed(self):
        """Maneja cambios en las fechas."""
        self._update_days_label()
        
        start = self.get_start_date()
        end = self.get_end_date()
        
        self.period_changed.emit(start, end)
    
    def _update_days_label(self):
        """Actualiza la etiqueta de días."""
        start = self.date_start.date()
        end = self.date_end.date()
        days = start.daysTo(end)
        
        if days < 0:
            self.label_days.setText("⚠️ Fechas inválidas")
            self.label_days.setStyleSheet("color: #ff3b3b; font-weight: bold;")
        elif days == 0:
            self.label_days.setText("1 día")
            self.label_days.setStyleSheet("color: #00d4ff; font-weight: bold;")
        else:
            self.label_days.setText(f"{days + 1} días")
            self.label_days.setStyleSheet("color: #00d4ff; font-weight: bold;")
    
    def get_start_date(self) -> date:
        """Obtiene la fecha de inicio."""
        qdate = self.date_start.date()
        return date(qdate.year(), qdate.month(), qdate.day())
    
    def get_end_date(self) -> date:
        """Obtiene la fecha de fin."""
        qdate = self.date_end.date()
        return date(qdate.year(), qdate.month(), qdate.day())
    
    def get_period(self) -> Tuple[date, date]:
        """Obtiene el período completo."""
        return (self.get_start_date(), self.get_end_date())
    
    def validate(self) -> bool:
        """Valida que el período sea correcto."""
        start = self.date_start.date()
        end = self.date_end.date()
        
        return start.daysTo(end) >= 0


class ComparativePeriodSelector(QWidget):
    """
    Widget para seleccionar períodos comparativos.
    
    Permite comparar hasta 4 períodos simultáneos.
    """
    
    periods_changed = pyqtSignal(list)
    
    def __init__(self, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.period_widgets = []
        self._setup_ui()
    
    def _setup_ui(self):
        """Configura la interfaz de usuario."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        
        # Grupo principal
        group = QGroupBox("📊 PERÍODOS COMPARATIVOS")
        group_layout = QVBoxLayout(group)
        group_layout.setSpacing(12)
        
        # Información
        info = QLabel(
            "Configure hasta 4 períodos para comparar.\n"
            "El primer período será el actual y los siguientes los anteriores."
        )
        info.setStyleSheet("color: #888888;")
        group_layout.addWidget(info)
        
        # Contenedor de períodos
        self.periods_container = QVBoxLayout()
        self.periods_container.setSpacing(8)
        group_layout.addLayout(self.periods_container)
        
        # Agregar 2 períodos por defecto
        self._add_period_row("Período Actual")
        self._add_period_row("Período Anterior")
        
        # Botones
        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(8)
        
        btn_add = QPushButton("➕ Agregar Período")
        btn_add.setProperty("class", "secondary")
        btn_add.clicked.connect(self._on_add_period)
        btn_layout.addWidget(btn_add)
        
        btn_layout.addStretch()
        group_layout.addLayout(btn_layout)
        
        layout.addWidget(group)
    
    def _add_period_row(self, label: str = None):
        """Agrega una fila de período."""
        if len(self.period_widgets) >= 4:
            return
        
        row = QHBoxLayout()
        row.setSpacing(8)
        
        # Número/Etiqueta
        idx = len(self.period_widgets) + 1
        label_text = label or f"Período {idx}"
        lbl = QLabel(f"{idx}. {label_text}")
        lbl.setMinimumWidth(120)
        row.addWidget(lbl)
        
        # Fecha inicio
        date_start = QDateEdit()
        date_start.setCalendarPopup(True)
        date_start.setDisplayFormat("dd/MM/yyyy")
        date_start.dateChanged.connect(self._on_period_changed)
        row.addWidget(date_start)
        
        row.addWidget(QLabel("a"))
        
        # Fecha fin
        date_end = QDateEdit()
        date_end.setCalendarPopup(True)
        date_end.setDisplayFormat("dd/MM/yyyy")
        date_end.dateChanged.connect(self._on_period_changed)
        row.addWidget(date_end)
        
        # Botón eliminar (excepto los primeros 2)
        if len(self.period_widgets) >= 2:
            btn_remove = QPushButton("✕")
            btn_remove.setMaximumWidth(30)
            btn_remove.setProperty("class", "danger")
            btn_remove.clicked.connect(lambda: self._remove_period(row))
            row.addWidget(btn_remove)
        
        row.addStretch()
        
        # Establecer fechas por defecto
        offset = len(self.period_widgets) * 30
        end = QDate.currentDate().addDays(-offset)
        start = end.addDays(-30)
        date_start.setDate(start)
        date_end.setDate(end)
        
        # Guardar referencia
        self.period_widgets.append({
            'layout': row,
            'start': date_start,
            'end': date_end
        })
        
        self.periods_container.addLayout(row)
    
    def _on_add_period(self):
        """Agrega un nuevo período."""
        if len(self.period_widgets) < 4:
            self._add_period_row()
            self._on_period_changed()
    
    def _remove_period(self, layout):
        """Elimina un período."""
        for i, pw in enumerate(self.period_widgets):
            if pw['layout'] == layout:
                # Limpiar widgets del layout
                while layout.count():
                    item = layout.takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
                
                self.periods_container.removeItem(layout)
                self.period_widgets.pop(i)
                break
        
        self._on_period_changed()
    
    def _on_period_changed(self):
        """Maneja cambios en los períodos."""
        periods = self.get_periods()
        self.periods_changed.emit(periods)
    
    def get_periods(self) -> list:
        """Obtiene todos los períodos configurados."""
        periods = []
        
        for pw in self.period_widgets:
            start_qdate = pw['start'].date()
            end_qdate = pw['end'].date()
            
            start = date(start_qdate.year(), start_qdate.month(), start_qdate.day())
            end = date(end_qdate.year(), end_qdate.month(), end_qdate.day())
            
            periods.append((start, end))
        
        return periods
    
    def validate(self) -> bool:
        """Valida todos los períodos."""
        for pw in self.period_widgets:
            start = pw['start'].date()
            end = pw['end'].date()
            
            if start.daysTo(end) < 0:
                return False
        
        return True
