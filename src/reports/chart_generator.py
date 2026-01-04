"""
Generador de gráficos de barras.

Genera gráficos con estilo policial para los reportes.
"""
from __future__ import annotations

import io
from typing import Dict, List, Optional, Tuple, Any, TYPE_CHECKING
from pathlib import Path

if TYPE_CHECKING:
    from matplotlib.figure import Figure
    from matplotlib.axes import Axes

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as mpatches
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False
    plt = None
    np = None

from ..models.report_data import PeriodData, ReportData
from ..core.period_comparator import PeriodComparator
from ..utils.constants import (
    CHART_CONFIG,
    COLORES_DELITOS,
    ColoresPolicial,
    DIAS_SEMANA,
    FranjaHoraria,
)


class ChartGenerator:
    """
    Generador de gráficos de barras con estilo policial.
    
    Genera gráficos simples y comparativos para el reporte.
    """
    
    def __init__(self, report_data: ReportData, style: str = 'policial'):
        """
        Inicializa el generador.
        
        Args:
            report_data: Datos del reporte.
            style: Estilo de gráficos ('policial', 'clasico', 'moderno')
        """
        if not HAS_MATPLOTLIB:
            raise ImportError("matplotlib no está instalado")
        
        self.report = report_data
        self.periodo = report_data.periodo_principal
        self.style = style
        
        # Configurar estilo
        self._setup_style()
    
    def _setup_style(self):
        """Configura el estilo de matplotlib."""
        plt.style.use('default')
        
        # Configuración general
        plt.rcParams['figure.facecolor'] = 'white'
        plt.rcParams['axes.facecolor'] = 'white'
        plt.rcParams['axes.edgecolor'] = '#333333'
        plt.rcParams['axes.labelcolor'] = '#333333'
        plt.rcParams['xtick.color'] = '#333333'
        plt.rcParams['ytick.color'] = '#333333'
        plt.rcParams['font.family'] = 'sans-serif'
        plt.rcParams['font.sans-serif'] = ['Segoe UI', 'Arial', 'Helvetica']
    
    def _get_bar_color(self, index: int = 0) -> str:
        """Obtiene color para barra."""
        colores = ['#4169E1', '#32CD32', '#FF6347', '#FFD700', '#9370DB', '#20B2AA']
        return colores[index % len(colores)]
    
    def _add_value_labels(self, ax, bars, fontsize: int = 9):
        """Agrega etiquetas de valor sobre las barras."""
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax.annotate(
                    f'{int(height)}',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 3),
                    textcoords="offset points",
                    ha='center',
                    va='bottom',
                    fontsize=fontsize,
                    fontweight='bold'
                )
    
    def _create_figure(
        self,
        figsize: Tuple[float, float] = None
    ) -> Tuple['Figure', 'Axes']:
        """Crea figura y ejes."""
        figsize = figsize or CHART_CONFIG['figure_size']
        fig, ax = plt.subplots(figsize=figsize, dpi=CHART_CONFIG['dpi'])
        return fig, ax
    
    def _finalize_chart(
        self,
        fig: 'Figure',
        ax: 'Axes',
        title: str,
        xlabel: str = '',
        ylabel: str = 'Cantidad',
        rotate_labels: bool = True
    ):
        """Finaliza configuración del gráfico."""
        ax.set_title(title, fontsize=14, fontweight='bold', pad=15, color='#CC0000')
        ax.set_xlabel(xlabel, fontsize=10)
        ax.set_ylabel(ylabel, fontsize=10)
        
        if rotate_labels:
            plt.xticks(rotation=45, ha='right')
        
        ax.yaxis.grid(True, linestyle='--', alpha=0.3)
        ax.set_axisbelow(True)
        
        # Ajustar márgenes
        plt.tight_layout()
    
    # ═══════════════════════════════════════════════════════════════════════
    # GRÁFICOS SIMPLES
    # ═══════════════════════════════════════════════════════════════════════
    
    def grafico_delitos(self) -> 'Figure':
        """
        Genera gráfico de barras de delitos con modalidades.
        """
        if not self.periodo:
            return None
        
        conteo = self.periodo.conteo_por_delito()
        if not conteo:
            return None
        
        # Ordenar por cantidad
        items = sorted(conteo.items(), key=lambda x: -x[1])
        categorias = [item[0].replace('_', ' ') for item in items]
        valores = [item[1] for item in items]
        
        fig, ax = self._create_figure()
        bars = ax.bar(categorias, valores, color='#4169E1', edgecolor='#000000', linewidth=0.5)
        
        self._add_value_labels(ax, bars)
        self._finalize_chart(fig, ax, 'GRÁFICA DE DELITOS CON MODALIDADES')
        
        return fig
    
    def grafico_dias_semana(self) -> 'Figure':
        """
        Genera gráfico de barras de días de la semana.
        """
        if not self.periodo:
            return None
        
        conteo = self.periodo.conteo_por_dia_semana()
        items = sorted(conteo.items(), key=lambda x: -x[1])
        categorias = [item[0] for item in items]
        valores = [item[1] for item in items]
        
        fig, ax = self._create_figure()
        bars = ax.bar(categorias, valores, color='#4169E1', edgecolor='#000000', linewidth=0.5)
        
        self._add_value_labels(ax, bars)
        self._finalize_chart(fig, ax, 'GRÁFICA DE DÍAS DE LA SEMANA EN QUE OCURRIERON LOS HECHOS')
        
        return fig
    
    def grafico_franja_horaria(self) -> 'Figure':
        """
        Genera gráfico de barras de franja horaria.
        """
        if not self.periodo:
            return None
        
        conteo = self.periodo.conteo_por_franja_horaria()
        items = sorted(conteo.items(), key=lambda x: -x[1])
        categorias = [item[0] for item in items]
        valores = [item[1] for item in items]
        
        fig, ax = self._create_figure()
        bars = ax.bar(categorias, valores, color='#4169E1', edgecolor='#000000', linewidth=0.5)
        
        self._add_value_labels(ax, bars)
        self._finalize_chart(fig, ax, 'GRÁFICA DE FRANJA HORARIA EN QUE OCURRIERON LOS HECHOS')
        
        return fig
    
    def grafico_movilidad(self) -> 'Figure':
        """
        Genera gráfico de barras de medios de movilidad.
        """
        if not self.periodo:
            return None
        
        conteo = self.periodo.conteo_por_movilidad()
        items = sorted(conteo.items(), key=lambda x: -x[1])
        categorias = [item[0].replace('_', ' ') for item in items]
        valores = [item[1] for item in items]
        
        fig, ax = self._create_figure()
        bars = ax.bar(categorias, valores, color='#4169E1', edgecolor='#000000', linewidth=0.5)
        
        self._add_value_labels(ax, bars)
        self._finalize_chart(fig, ax, 'GRÁFICA DE MEDIOS DE MOVILIDAD UTILIZADOS')
        
        return fig
    
    def grafico_armas(self) -> 'Figure':
        """
        Genera gráfico de barras de armas en robos agravados.
        """
        if not self.periodo:
            return None
        
        conteo = self.periodo.conteo_por_arma()
        if not conteo or sum(conteo.values()) == 0:
            return None
        
        items = sorted(conteo.items(), key=lambda x: -x[1])
        categorias = [item[0].replace('_', ' ') for item in items]
        valores = [item[1] for item in items]
        
        fig, ax = self._create_figure()
        bars = ax.bar(categorias, valores, color='#4169E1', edgecolor='#000000', linewidth=0.5)
        
        self._add_value_labels(ax, bars)
        self._finalize_chart(fig, ax, 'GRÁFICA MEDIOS O ARMAS UTILIZADAS EN ROBOS AGRAVADOS')
        
        return fig
    
    def grafico_ambito(self) -> 'Figure':
        """
        Genera gráfico de barras de ámbito de ocurrencia.
        """
        if not self.periodo:
            return None
        
        conteo = self.periodo.conteo_por_ambito()
        items = sorted(conteo.items(), key=lambda x: -x[1])
        categorias = [item[0].replace('_', ' ') for item in items]
        valores = [item[1] for item in items]
        
        fig, ax = self._create_figure()
        bars = ax.bar(categorias, valores, color='#4169E1', edgecolor='#000000', linewidth=0.5)
        
        self._add_value_labels(ax, bars)
        self._finalize_chart(fig, ax, 'GRÁFICA DE ÁMBITO DE OCURRENCIA DELICTUAL')
        
        return fig
    
    # ═══════════════════════════════════════════════════════════════════════
    # GRÁFICOS MATRICIALES (BARRAS AGRUPADAS)
    # ═══════════════════════════════════════════════════════════════════════
    
    def grafico_delito_dia(self) -> 'Figure':
        """
        Genera gráfico de barras agrupadas: delitos por día.
        """
        if not self.periodo:
            return None
        
        matriz = self.periodo.matriz_delito_dia()
        if not matriz:
            return None
        
        delitos = sorted(matriz.keys())
        dias = DIAS_SEMANA
        
        n_delitos = len(delitos)
        n_dias = len(dias)
        
        fig, ax = self._create_figure(figsize=(12, 6))
        
        x = np.arange(n_delitos)
        width = 0.8 / n_dias
        
        # Asignar colores a cada delito
        colores_dias = ['#FF0000', '#00FF00', '#0000FF', '#800080', '#FF8C00', '#00CED1', '#FFD700']
        
        for i, dia in enumerate(dias):
            valores = [matriz[delito].get(dia, 0) for delito in delitos]
            offset = (i - n_dias/2 + 0.5) * width
            bars = ax.bar(x + offset, valores, width, label=dia, color=colores_dias[i % len(colores_dias)])
            
            # Etiquetas solo si hay valor
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(
                        f'{int(height)}',
                        xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0, 1),
                        textcoords="offset points",
                        ha='center',
                        va='bottom',
                        fontsize=7
                    )
        
        ax.set_xticks(x)
        ax.set_xticklabels([d.replace('_', '\n') for d in delitos], fontsize=8)
        ax.legend(title='Días', bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8)
        
        self._finalize_chart(fig, ax, 'GRÁFICA DE HECHOS POR DÍAS DE LAS SEMANA', rotate_labels=False)
        plt.subplots_adjust(right=0.85)
        
        return fig
    
    def grafico_delito_franja(self) -> 'Figure':
        """
        Genera gráfico de barras agrupadas: delitos por franja horaria.
        """
        if not self.periodo:
            return None
        
        matriz = self.periodo.matriz_delito_franja()
        if not matriz:
            return None
        
        delitos = sorted(matriz.keys())
        franjas = [f.display_name for f in FranjaHoraria]
        franjas_cortas = [f.nombre[:6] for f in FranjaHoraria]
        
        n_delitos = len(delitos)
        n_franjas = len(franjas)
        
        fig, ax = self._create_figure(figsize=(12, 6))
        
        x = np.arange(n_delitos)
        width = 0.8 / n_franjas
        
        colores_franjas = ['#1E90FF', '#32CD32', '#FFD700', '#FF8C00', '#FF4500', '#9400D3']
        
        for i, (franja_full, franja_corta) in enumerate(zip(franjas, franjas_cortas)):
            valores = [matriz[delito].get(franja_full, 0) for delito in delitos]
            offset = (i - n_franjas/2 + 0.5) * width
            bars = ax.bar(x + offset, valores, width, label=franja_corta, color=colores_franjas[i % len(colores_franjas)])
            
            for bar in bars:
                height = bar.get_height()
                if height > 0:
                    ax.annotate(
                        f'{int(height)}',
                        xy=(bar.get_x() + bar.get_width()/2, height),
                        xytext=(0, 1),
                        textcoords="offset points",
                        ha='center',
                        va='bottom',
                        fontsize=7
                    )
        
        ax.set_xticks(x)
        ax.set_xticklabels([d.replace('_', '\n') for d in delitos], fontsize=8)
        ax.legend(title='Franjas', bbox_to_anchor=(1.02, 1), loc='upper left', fontsize=8)
        
        self._finalize_chart(fig, ax, 'GRÁFICA DE HECHOS POR FRANJAS HORARIAS', rotate_labels=False)
        plt.subplots_adjust(right=0.85)
        
        return fig
    
    # ═══════════════════════════════════════════════════════════════════════
    # GRÁFICOS COMPARATIVOS
    # ═══════════════════════════════════════════════════════════════════════
    
    def grafico_comparativo_delitos(self) -> 'Figure':
        """
        Genera gráfico comparativo de delitos entre períodos.
        """
        if not self.report.es_comparativo:
            return self.grafico_delitos()
        
        p1 = self.report.periodo_principal
        p2 = self.report.periodo_comparacion
        
        comparator = PeriodComparator(p1, p2)
        comparaciones = comparator.comparar_delitos()
        
        categorias = [c.categoria.replace('_', ' ') for c in comparaciones]
        valores_p1 = [c.valor_periodo_a for c in comparaciones]
        valores_p2 = [c.valor_periodo_b for c in comparaciones]
        
        fig, ax = self._create_figure(figsize=(12, 6))
        
        x = np.arange(len(categorias))
        width = 0.35
        
        bars1 = ax.bar(x - width/2, valores_p1, width, label=p1.rango_fechas[:20], color='#4169E1')
        bars2 = ax.bar(x + width/2, valores_p2, width, label=p2.rango_fechas[:20], color='#FF6347')
        
        self._add_value_labels(ax, bars1, fontsize=8)
        self._add_value_labels(ax, bars2, fontsize=8)
        
        ax.set_xticks(x)
        ax.set_xticklabels(categorias, fontsize=9)
        ax.legend()
        
        self._finalize_chart(fig, ax, 'GRÁFICA COMPARATIVA DE DELITOS')
        
        return fig
    
    # ═══════════════════════════════════════════════════════════════════════
    # EXPORTACIÓN
    # ═══════════════════════════════════════════════════════════════════════
    
    def save_chart(
        self,
        fig: 'Figure',
        path: str,
        format: str = 'png'
    ) -> bool:
        """
        Guarda un gráfico en archivo.
        
        Args:
            fig: Figura de matplotlib
            path: Ruta de destino
            format: Formato ('png', 'jpg', 'pdf', 'svg')
        
        Returns:
            True si se guardó correctamente.
        """
        try:
            Path(path).parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(path, format=format, dpi=150, bbox_inches='tight')
            plt.close(fig)
            return True
        except Exception as e:
            print(f"Error guardando gráfico: {e}")
            return False
    
    def chart_to_bytes(self, fig: 'Figure', format: str = 'png') -> bytes:
        """
        Convierte un gráfico a bytes (para insertar en Excel/Word).
        """
        buf = io.BytesIO()
        fig.savefig(buf, format=format, dpi=150, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig)
        return buf.read()
    
    def generar_todos(self, output_dir: str) -> Dict[str, str]:
        """
        Genera y guarda todos los gráficos.
        
        Args:
            output_dir: Directorio de salida.
        
        Returns:
            Diccionario {nombre: ruta_archivo}
        """
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        graficos = {}
        
        charts = [
            ('delitos', self.grafico_delitos if not self.report.es_comparativo 
                        else self.grafico_comparativo_delitos),
            ('dias_semana', self.grafico_dias_semana),
            ('franja_horaria', self.grafico_franja_horaria),
            ('movilidad', self.grafico_movilidad),
            ('armas', self.grafico_armas),
            ('ambito', self.grafico_ambito),
            ('delito_dia', self.grafico_delito_dia),
            ('delito_franja', self.grafico_delito_franja),
        ]
        
        for nombre, func in charts:
            try:
                fig = func()
                if fig:
                    path = output_path / f"{nombre}.png"
                    if self.save_chart(fig, str(path)):
                        graficos[nombre] = str(path)
            except Exception as e:
                print(f"Error generando gráfico {nombre}: {e}")
        
        return graficos
