"""
Comparador de períodos.

Genera las comparaciones estadísticas entre múltiples períodos
para los cuadros comparativos del informe.
"""
from dataclasses import dataclass
from typing import Dict, List, Any, Optional
from enum import Enum

from ..models.report_data import PeriodData


class Tendencia(Enum):
    """Tendencia de variación."""
    SUBIO = "subio"
    BAJO = "bajo"
    IGUAL = "igual"
    NUEVO = "nuevo"


@dataclass
class ComparacionItem:
    """Resultado de comparación para un ítem."""
    categoria: str
    valor_periodo_a: int
    valor_periodo_b: int
    diferencia: int
    porcentaje: float
    tendencia: Tendencia
    
    @property
    def tendencia_icono(self) -> str:
        """Icono de tendencia."""
        iconos = {
            Tendencia.SUBIO: "▲",
            Tendencia.BAJO: "▼",
            Tendencia.IGUAL: "─",
            Tendencia.NUEVO: "★"
        }
        return iconos.get(self.tendencia, "")
    
    @property
    def tendencia_color(self) -> str:
        """Color según tendencia (para delitos, subir es malo)."""
        colores = {
            Tendencia.SUBIO: "#FF3B3B",   # Rojo (malo)
            Tendencia.BAJO: "#00FF88",     # Verde (bueno)
            Tendencia.IGUAL: "#808080",    # Gris
            Tendencia.NUEVO: "#FFaa00"     # Naranja
        }
        return colores.get(self.tendencia, "#808080")
    
    @property
    def porcentaje_formateado(self) -> str:
        """Porcentaje formateado con signo."""
        if self.tendencia == Tendencia.NUEVO:
            return "NUEVO"
        signo = "+" if self.porcentaje > 0 else ""
        return f"{signo}{self.porcentaje:.2f}%"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convierte a diccionario."""
        return {
            'categoria': self.categoria,
            'periodo_a': self.valor_periodo_a,
            'periodo_b': self.valor_periodo_b,
            'diferencia': self.diferencia,
            'porcentaje': self.porcentaje,
            'porcentaje_str': self.porcentaje_formateado,
            'tendencia': self.tendencia.value,
            'tendencia_icono': self.tendencia_icono,
            'tendencia_color': self.tendencia_color
        }


class PeriodComparator:
    """
    Comparador de períodos para análisis estadístico.
    
    Genera comparaciones entre dos o más períodos con
    cálculo de variaciones absolutas y porcentuales.
    """
    
    def __init__(
        self,
        periodo_a: PeriodData,
        periodo_b: PeriodData
    ):
        """
        Inicializa el comparador.
        
        Args:
            periodo_a: Período base (anterior)
            periodo_b: Período a comparar (actual)
        """
        self.periodo_a = periodo_a
        self.periodo_b = periodo_b
    
    # ═══════════════════════════════════════════════════════════════════════
    # CÁLCULO DE VARIACIÓN
    # ═══════════════════════════════════════════════════════════════════════
    
    def _calcular_variacion(
        self,
        valor_a: int,
        valor_b: int
    ) -> tuple[int, float, Tendencia]:
        """
        Calcula la variación entre dos valores.
        
        Returns:
            (diferencia, porcentaje, tendencia)
        """
        diferencia = valor_b - valor_a
        
        if valor_a == 0:
            if valor_b > 0:
                return diferencia, 100.0, Tendencia.NUEVO
            else:
                return 0, 0.0, Tendencia.IGUAL
        
        porcentaje = ((valor_b - valor_a) / valor_a) * 100
        
        if diferencia > 0:
            tendencia = Tendencia.SUBIO
        elif diferencia < 0:
            tendencia = Tendencia.BAJO
        else:
            tendencia = Tendencia.IGUAL
        
        return diferencia, round(porcentaje, 2), tendencia
    
    def _comparar_conteos(
        self,
        conteo_a: Dict[str, int],
        conteo_b: Dict[str, int]
    ) -> List[ComparacionItem]:
        """
        Compara dos diccionarios de conteos.
        
        Returns:
            Lista de ComparacionItem ordenada por diferencia descendente.
        """
        todas_claves = sorted(set(conteo_a.keys()) | set(conteo_b.keys()))
        resultados = []
        
        for clave in todas_claves:
            val_a = conteo_a.get(clave, 0)
            val_b = conteo_b.get(clave, 0)
            
            diferencia, porcentaje, tendencia = self._calcular_variacion(val_a, val_b)
            
            resultados.append(ComparacionItem(
                categoria=clave,
                valor_periodo_a=val_a,
                valor_periodo_b=val_b,
                diferencia=diferencia,
                porcentaje=porcentaje,
                tendencia=tendencia
            ))
        
        # Ordenar por valor del período B (actual) descendente
        return sorted(resultados, key=lambda x: -x.valor_periodo_b)
    
    # ═══════════════════════════════════════════════════════════════════════
    # COMPARACIONES ESPECÍFICAS
    # ═══════════════════════════════════════════════════════════════════════
    
    def comparar_delitos(self) -> List[ComparacionItem]:
        """Compara los delitos por tipo."""
        return self._comparar_conteos(
            self.periodo_a.conteo_por_delito(),
            self.periodo_b.conteo_por_delito()
        )
    
    def comparar_categorias(self) -> List[ComparacionItem]:
        """Compara por categoría (ROBOS, HURTOS)."""
        return self._comparar_conteos(
            self.periodo_a.conteo_por_categoria(),
            self.periodo_b.conteo_por_categoria()
        )
    
    def comparar_dias_semana(self) -> List[ComparacionItem]:
        """Compara por día de la semana."""
        return self._comparar_conteos(
            self.periodo_a.conteo_por_dia_semana(),
            self.periodo_b.conteo_por_dia_semana()
        )
    
    def comparar_franjas_horarias(self) -> List[ComparacionItem]:
        """Compara por franja horaria."""
        return self._comparar_conteos(
            self.periodo_a.conteo_por_franja_horaria(),
            self.periodo_b.conteo_por_franja_horaria()
        )
    
    def comparar_movilidad(self) -> List[ComparacionItem]:
        """Compara por medio de movilidad."""
        return self._comparar_conteos(
            self.periodo_a.conteo_por_movilidad(),
            self.periodo_b.conteo_por_movilidad()
        )
    
    def comparar_armas(self) -> List[ComparacionItem]:
        """Compara por arma/medio utilizado."""
        return self._comparar_conteos(
            self.periodo_a.conteo_por_arma(),
            self.periodo_b.conteo_por_arma()
        )
    
    def comparar_ambitos(self) -> List[ComparacionItem]:
        """Compara por ámbito de ocurrencia."""
        return self._comparar_conteos(
            self.periodo_a.conteo_por_ambito(),
            self.periodo_b.conteo_por_ambito()
        )
    
    def comparar_esclarecimiento(self) -> List[ComparacionItem]:
        """Compara por estado de esclarecimiento."""
        return self._comparar_conteos(
            self.periodo_a.conteo_esclarecimiento(),
            self.periodo_b.conteo_esclarecimiento()
        )
    
    def comparar_aprehendidos(self) -> List[ComparacionItem]:
        """Compara clasificación de aprehendidos."""
        return self._comparar_conteos(
            self.periodo_a.conteo_aprehendidos_clasificacion(),
            self.periodo_b.conteo_aprehendidos_clasificacion()
        )
    
    # ═══════════════════════════════════════════════════════════════════════
    # RESUMEN GENERAL
    # ═══════════════════════════════════════════════════════════════════════
    
    def resumen_general(self) -> Dict[str, ComparacionItem]:
        """
        Genera un resumen general de las comparaciones principales.
        
        Returns:
            Diccionario con indicadores clave comparados.
        """
        indicadores = {}
        
        # Total hechos
        diff, pct, tend = self._calcular_variacion(
            self.periodo_a.total_hechos,
            self.periodo_b.total_hechos
        )
        indicadores['total_hechos'] = ComparacionItem(
            categoria="Total Delitos",
            valor_periodo_a=self.periodo_a.total_hechos,
            valor_periodo_b=self.periodo_b.total_hechos,
            diferencia=diff,
            porcentaje=pct,
            tendencia=tend
        )
        
        # Total robos
        cat_a = self.periodo_a.conteo_por_categoria()
        cat_b = self.periodo_b.conteo_por_categoria()
        diff, pct, tend = self._calcular_variacion(
            cat_a.get('ROBOS', 0),
            cat_b.get('ROBOS', 0)
        )
        indicadores['total_robos'] = ComparacionItem(
            categoria="Total Robos",
            valor_periodo_a=cat_a.get('ROBOS', 0),
            valor_periodo_b=cat_b.get('ROBOS', 0),
            diferencia=diff,
            porcentaje=pct,
            tendencia=tend
        )
        
        # Total hurtos
        diff, pct, tend = self._calcular_variacion(
            cat_a.get('HURTOS', 0),
            cat_b.get('HURTOS', 0)
        )
        indicadores['total_hurtos'] = ComparacionItem(
            categoria="Total Hurtos",
            valor_periodo_a=cat_a.get('HURTOS', 0),
            valor_periodo_b=cat_b.get('HURTOS', 0),
            diferencia=diff,
            porcentaje=pct,
            tendencia=tend
        )
        
        # Total aprehendidos
        diff, pct, tend = self._calcular_variacion(
            self.periodo_a.total_aprehendidos,
            self.periodo_b.total_aprehendidos
        )
        indicadores['total_aprehendidos'] = ComparacionItem(
            categoria="Total Aprehendidos",
            valor_periodo_a=self.periodo_a.total_aprehendidos,
            valor_periodo_b=self.periodo_b.total_aprehendidos,
            diferencia=diff,
            porcentaje=pct,
            tendencia=tend
        )
        
        # Total mencionados
        diff, pct, tend = self._calcular_variacion(
            self.periodo_a.total_mencionados,
            self.periodo_b.total_mencionados
        )
        indicadores['total_mencionados'] = ComparacionItem(
            categoria="Total Mencionados",
            valor_periodo_a=self.periodo_a.total_mencionados,
            valor_periodo_b=self.periodo_b.total_mencionados,
            diferencia=diff,
            porcentaje=pct,
            tendencia=tend
        )
        
        # Esclarecidos
        escl_a = self.periodo_a.conteo_esclarecimiento()
        escl_b = self.periodo_b.conteo_esclarecimiento()
        total_escl_a = sum(v for k, v in escl_a.items() if k != 'NO_ESCLARECIDO')
        total_escl_b = sum(v for k, v in escl_b.items() if k != 'NO_ESCLARECIDO')
        diff, pct, tend = self._calcular_variacion(total_escl_a, total_escl_b)
        indicadores['total_esclarecidos'] = ComparacionItem(
            categoria="Hechos Esclarecidos",
            valor_periodo_a=total_escl_a,
            valor_periodo_b=total_escl_b,
            diferencia=diff,
            porcentaje=pct,
            tendencia=tend
        )
        
        return indicadores
    
    def to_comparison_table(self) -> List[Dict[str, Any]]:
        """
        Genera tabla de comparación general para el reporte.
        
        Returns:
            Lista de filas para la tabla comparativa.
        """
        resumen = self.resumen_general()
        
        filas = []
        orden = [
            'total_hechos',
            'total_robos', 
            'total_hurtos',
            'total_esclarecidos',
            'total_aprehendidos',
            'total_mencionados'
        ]
        
        for key in orden:
            if key in resumen:
                item = resumen[key]
                filas.append({
                    'indicador': item.categoria,
                    self.periodo_a.rango_fechas: item.valor_periodo_a,
                    self.periodo_b.rango_fechas: item.valor_periodo_b,
                    'diferencia': f"{'+' if item.diferencia > 0 else ''}{item.diferencia}",
                    'variacion': f"{item.porcentaje_formateado} {item.tendencia_icono}",
                    'color': item.tendencia_color
                })
        
        return filas
