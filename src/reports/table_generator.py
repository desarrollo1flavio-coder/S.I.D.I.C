"""
Generador de tablas/cuadros para reportes.

Genera todas las tablas estadísticas con formato adecuado
para exportación a Excel y Word.
"""
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import pandas as pd

from ..models.report_data import PeriodData, ReportData
from ..core.period_comparator import PeriodComparator
from ..utils.constants import (
    DIAS_SEMANA,
    FranjaHoraria,
    SIMBOLOS_DELITOS,
    SimboloDelito,
)


@dataclass
class TableConfig:
    """Configuración para generación de tabla."""
    titulo: str
    incluir_porcentaje: bool = True
    incluir_total: bool = True
    incluir_grafico: bool = True
    ordenar_por_valor: bool = True


class TableGenerator:
    """
    Generador de tablas estadísticas para reportes S.I.D.I.C.
    
    Genera todas las tablas necesarias con formato consistente.
    """
    
    def __init__(self, report_data: ReportData):
        """
        Inicializa el generador.
        
        Args:
            report_data: Datos del reporte a generar.
        """
        self.report = report_data
        self.periodo = report_data.periodo_principal
    
    # ═══════════════════════════════════════════════════════════════════════
    # UTILIDADES
    # ═══════════════════════════════════════════════════════════════════════
    
    def _calcular_porcentaje(self, valor: int, total: int) -> float:
        """Calcula porcentaje con manejo de división por cero."""
        if total == 0:
            return 0.0
        return round((valor / total) * 100, 2)
    
    def _format_porcentaje(self, valor: float) -> str:
        """Formatea porcentaje para mostrar."""
        return f"{valor:.2f}%"
    
    def _conteo_a_dataframe(
        self,
        conteo: Dict[str, int],
        columna_nombre: str,
        columna_valor: str,
        ordenar: bool = True
    ) -> pd.DataFrame:
        """
        Convierte un diccionario de conteo a DataFrame.
        """
        items = list(conteo.items())
        if ordenar:
            items = sorted(items, key=lambda x: -x[1])
        
        total = sum(conteo.values())
        
        data = []
        for nombre, valor in items:
            data.append({
                columna_nombre: nombre,
                columna_valor: valor,
                'Porcentaje': self._format_porcentaje(
                    self._calcular_porcentaje(valor, total)
                )
            })
        
        # Agregar fila de total
        data.append({
            columna_nombre: 'TOTAL',
            columna_valor: total,
            'Porcentaje': '100,00%'
        })
        
        return pd.DataFrame(data)
    
    # ═══════════════════════════════════════════════════════════════════════
    # CUADRO DE REFERENCIA
    # ═══════════════════════════════════════════════════════════════════════
    
    def generar_cuadro_referencia(self) -> pd.DataFrame:
        """
        Genera el cuadro de referencia para mapas.
        
        Incluye símbolos, categorías, subtotales y totales.
        """
        if not self.periodo:
            return pd.DataFrame()
        
        filas = self.periodo.cuadro_referencia()
        
        data = []
        for fila in filas:
            tipo = fila['tipo']
            texto = fila['texto']
            cantidad = fila['cantidad']
            
            # Obtener símbolo si es delito
            simbolo = ""
            color = ""
            if tipo == 'delito':
                if texto in SIMBOLOS_DELITOS:
                    sim = SIMBOLOS_DELITOS[texto]
                    simbolo = sim.simbolo
                    color = sim.color
                else:
                    simbolo = "●"
            elif tipo == 'indicacion':
                simbolo = "○"
            elif tipo == 'comisaria':
                simbolo = "Ⓟ"
            
            data.append({
                'Símbolo': simbolo,
                'Tipo': tipo,
                'Descripción': texto.replace('_', ' '),
                'Cantidad': cantidad if cantidad is not None else '',
                'Color': color
            })
        
        return pd.DataFrame(data)
    
    # ═══════════════════════════════════════════════════════════════════════
    # DELITOS CON MODALIDADES
    # ═══════════════════════════════════════════════════════════════════════
    
    def generar_tabla_delitos(self) -> pd.DataFrame:
        """
        Genera tabla de delitos con modalidades.
        """
        if not self.periodo:
            return pd.DataFrame()
        
        conteo = self.periodo.conteo_por_delito()
        
        return self._conteo_a_dataframe(
            conteo,
            'DELITOS CON MODALIDADES',
            self.periodo.rango_fechas
        )
    
    def generar_tabla_delitos_comparativa(self) -> pd.DataFrame:
        """
        Genera tabla comparativa de delitos entre períodos.
        """
        if not self.report.es_comparativo:
            return self.generar_tabla_delitos()
        
        p1 = self.report.periodo_principal
        p2 = self.report.periodo_comparacion
        
        comparator = PeriodComparator(p1, p2)
        comparaciones = comparator.comparar_delitos()
        
        data = []
        total_p1 = p1.total_hechos
        total_p2 = p2.total_hechos
        
        for comp in comparaciones:
            data.append({
                'DELITOS CON MODALIDADES': comp.categoria.replace('_', ' '),
                p1.rango_fechas: comp.valor_periodo_a,
                '%': self._format_porcentaje(
                    self._calcular_porcentaje(comp.valor_periodo_a, total_p1)
                ),
                p2.rango_fechas: comp.valor_periodo_b,
                '% ': self._format_porcentaje(
                    self._calcular_porcentaje(comp.valor_periodo_b, total_p2)
                ),
                'Variación': comp.porcentaje_formateado,
                'Tendencia': comp.tendencia_icono
            })
        
        # Total
        total_comp = comparator.resumen_general()['total_hechos']
        data.append({
            'DELITOS CON MODALIDADES': 'TOTAL DE HECHOS',
            p1.rango_fechas: total_p1,
            '%': '100,00%',
            p2.rango_fechas: total_p2,
            '% ': '100,00%',
            'Variación': total_comp.porcentaje_formateado,
            'Tendencia': total_comp.tendencia_icono
        })
        
        return pd.DataFrame(data)
    
    # ═══════════════════════════════════════════════════════════════════════
    # DÍAS DE LA SEMANA
    # ═══════════════════════════════════════════════════════════════════════
    
    def generar_tabla_dias_semana(self) -> pd.DataFrame:
        """
        Genera tabla de hechos por día de la semana.
        """
        if not self.periodo:
            return pd.DataFrame()
        
        conteo = self.periodo.conteo_por_dia_semana()
        
        # Ordenar por cantidad, no por día
        return self._conteo_a_dataframe(
            conteo,
            'DÍAS DE LA SEMANA EN QUE OCURRIERON LOS HECHOS',
            self.periodo.rango_fechas
        )
    
    # ═══════════════════════════════════════════════════════════════════════
    # FRANJA HORARIA
    # ═══════════════════════════════════════════════════════════════════════
    
    def generar_tabla_franja_horaria(self) -> pd.DataFrame:
        """
        Genera tabla de hechos por franja horaria.
        """
        if not self.periodo:
            return pd.DataFrame()
        
        conteo = self.periodo.conteo_por_franja_horaria()
        
        return self._conteo_a_dataframe(
            conteo,
            'FRANJA HORARIA EN QUE OCURRIERON LOS HECHOS',
            self.periodo.rango_fechas
        )
    
    # ═══════════════════════════════════════════════════════════════════════
    # MOVILIDAD
    # ═══════════════════════════════════════════════════════════════════════
    
    def generar_tabla_movilidad(self) -> pd.DataFrame:
        """
        Genera tabla de medios de movilidad utilizados.
        """
        if not self.periodo:
            return pd.DataFrame()
        
        conteo = self.periodo.conteo_por_movilidad()
        
        return self._conteo_a_dataframe(
            conteo,
            'MEDIOS DE MOVILIDAD UTILIZADOS',
            self.periodo.rango_fechas
        )
    
    # ═══════════════════════════════════════════════════════════════════════
    # ARMAS EN ROBOS AGRAVADOS
    # ═══════════════════════════════════════════════════════════════════════
    
    def generar_tabla_armas(self) -> pd.DataFrame:
        """
        Genera tabla de armas/medios en robos agravados.
        """
        if not self.periodo:
            return pd.DataFrame()
        
        conteo = self.periodo.conteo_por_arma()
        
        if not conteo or sum(conteo.values()) == 0:
            return pd.DataFrame({
                'MEDIOS O ARMAS UTILIZADAS EN ROBOS AGRAVADOS': ['Sin datos'],
                self.periodo.rango_fechas: [0],
                'Porcentaje': ['0,00%']
            })
        
        return self._conteo_a_dataframe(
            conteo,
            'MEDIOS O ARMAS UTILIZADAS EN ROBOS AGRAVADOS',
            self.periodo.rango_fechas
        )
    
    # ═══════════════════════════════════════════════════════════════════════
    # ÁMBITO DE OCURRENCIA
    # ═══════════════════════════════════════════════════════════════════════
    
    def generar_tabla_ambito(self) -> pd.DataFrame:
        """
        Genera tabla de ámbito de ocurrencia delictual.
        """
        if not self.periodo:
            return pd.DataFrame()
        
        conteo = self.periodo.conteo_por_ambito()
        
        return self._conteo_a_dataframe(
            conteo,
            'AMBITO DE OCURRENCIA DELICTUAL',
            self.periodo.rango_fechas
        )
    
    # ═══════════════════════════════════════════════════════════════════════
    # MATRICES (DELITO × DIMENSIÓN)
    # ═══════════════════════════════════════════════════════════════════════
    
    def generar_matriz_delito_dia(self) -> pd.DataFrame:
        """
        Genera matriz de delitos por día de la semana.
        """
        if not self.periodo:
            return pd.DataFrame()
        
        matriz = self.periodo.matriz_delito_dia()
        
        if not matriz:
            return pd.DataFrame()
        
        # Construir DataFrame
        data = []
        for delito, dias in sorted(matriz.items()):
            fila = {'DELITO': delito.replace('_', ' ')}
            total_delito = 0
            for dia in DIAS_SEMANA:
                valor = dias.get(dia, 0)
                fila[dia[:3].upper()] = valor  # LUN, MAR, MIÉ...
                total_delito += valor
            fila['TOTAL DELITO'] = total_delito
            data.append(fila)
        
        # Fila de totales por día
        fila_total = {'DELITO': 'TOTAL POR DÍA'}
        total_general = 0
        for dia in DIAS_SEMANA:
            total_dia = sum(dias.get(dia, 0) for dias in matriz.values())
            fila_total[dia[:3].upper()] = total_dia
            total_general += total_dia
        fila_total['TOTAL DELITO'] = total_general
        data.append(fila_total)
        
        return pd.DataFrame(data)
    
    def generar_matriz_delito_franja(self) -> pd.DataFrame:
        """
        Genera matriz de delitos por franja horaria.
        """
        if not self.periodo:
            return pd.DataFrame()
        
        matriz = self.periodo.matriz_delito_franja()
        
        if not matriz:
            return pd.DataFrame()
        
        # Nombres cortos de franjas
        franjas_cortas = {
            f.display_name: f.nombre[:6].upper()
            for f in FranjaHoraria
        }
        
        data = []
        for delito, franjas in sorted(matriz.items()):
            fila = {'DELITO': delito.replace('_', ' ')}
            total_delito = 0
            for franja_full, franja_corta in franjas_cortas.items():
                valor = franjas.get(franja_full, 0)
                fila[franja_corta] = valor
                total_delito += valor
            fila['TOTAL'] = total_delito
            data.append(fila)
        
        # Fila de totales
        fila_total = {'DELITO': 'TOTAL POR FRANJA'}
        total_general = 0
        for franja_full, franja_corta in franjas_cortas.items():
            total_franja = sum(franjas.get(franja_full, 0) for franjas in matriz.values())
            fila_total[franja_corta] = total_franja
            total_general += total_franja
        fila_total['TOTAL'] = total_general
        data.append(fila_total)
        
        return pd.DataFrame(data)
    
    # ═══════════════════════════════════════════════════════════════════════
    # MENCIONADOS
    # ═══════════════════════════════════════════════════════════════════════
    
    def generar_tabla_mencionados(self) -> pd.DataFrame:
        """
        Genera tabla de personas mencionadas.
        """
        if not self.periodo or not self.periodo.mencionados:
            return pd.DataFrame({
                '#': ['-'],
                'Alias': ['Sin mencionados en el período'],
                'Delito': ['-'],
                'Dirección': ['-'],
                'Fecha': ['-'],
                'Hora': ['-'],
                'Datos': ['-']
            })
        
        data = []
        for i, m in enumerate(self.periodo.mencionados, 1):
            row = m.to_report_row()
            row['#'] = i
            data.append(row)
        
        # Reordenar columnas
        df = pd.DataFrame(data)
        cols = ['#', 'Alias', 'Delito', 'Dirección del Hecho', 'Fecha', 'Hora', 'Datos Filiatorios']
        return df[[c for c in cols if c in df.columns]]
    
    # ═══════════════════════════════════════════════════════════════════════
    # APREHENDIDOS
    # ═══════════════════════════════════════════════════════════════════════
    
    def generar_tabla_aprehendidos(self) -> pd.DataFrame:
        """
        Genera tabla de personas aprehendidas.
        """
        if not self.periodo or not self.periodo.aprehendidos:
            return pd.DataFrame({
                '#': ['-'],
                'Nombre/Alias': ['Sin aprehendidos en el período'],
                'Clasificación': ['-'],
                'Delito': ['-'],
                'Fecha': ['-'],
                'Edad': ['-'],
                'Sexo': ['-']
            })
        
        data = []
        for i, a in enumerate(self.periodo.aprehendidos, 1):
            row = a.to_report_row()
            row['#'] = i
            data.append(row)
        
        df = pd.DataFrame(data)
        cols = ['#', 'Nombre/Alias', 'Clasificación', 'Delito', 'Fecha', 'Edad', 'Sexo']
        return df[[c for c in cols if c in df.columns]]
    
    def generar_tabla_aprehendidos_clasificacion(self) -> pd.DataFrame:
        """
        Genera resumen de aprehendidos por clasificación.
        """
        if not self.periodo:
            return pd.DataFrame()
        
        conteo = self.periodo.conteo_aprehendidos_clasificacion()
        
        return self._conteo_a_dataframe(
            conteo,
            'CLASIFICACIÓN',
            'CANTIDAD'
        )
    
    # ═══════════════════════════════════════════════════════════════════════
    # ESCLARECIMIENTO
    # ═══════════════════════════════════════════════════════════════════════
    
    def generar_tabla_esclarecimiento(self) -> pd.DataFrame:
        """
        Genera tabla de índice de esclarecimiento.
        """
        if not self.periodo:
            return pd.DataFrame()
        
        conteo = self.periodo.conteo_esclarecimiento()
        
        return self._conteo_a_dataframe(
            conteo,
            'ESTADO DE ESCLARECIMIENTO',
            'CANTIDAD'
        )
    
    # ═══════════════════════════════════════════════════════════════════════
    # CUADRO COMPARATIVO GENERAL
    # ═══════════════════════════════════════════════════════════════════════
    
    def generar_tabla_comparativa_general(self) -> pd.DataFrame:
        """
        Genera cuadro comparativo general entre períodos.
        """
        if not self.report.es_comparativo:
            return pd.DataFrame()
        
        comparator = PeriodComparator(
            self.report.periodo_principal,
            self.report.periodo_comparacion
        )
        
        filas = comparator.to_comparison_table()
        return pd.DataFrame(filas)
    
    # ═══════════════════════════════════════════════════════════════════════
    # GENERAR TODAS LAS TABLAS
    # ═══════════════════════════════════════════════════════════════════════
    
    def generar_todas(self) -> Dict[str, pd.DataFrame]:
        """
        Genera todas las tablas del reporte.
        
        Returns:
            Diccionario {nombre_tabla: DataFrame}
        """
        tablas = {
            'cuadro_referencia': self.generar_cuadro_referencia(),
            'delitos': self.generar_tabla_delitos() if not self.report.es_comparativo 
                       else self.generar_tabla_delitos_comparativa(),
            'dias_semana': self.generar_tabla_dias_semana(),
            'franja_horaria': self.generar_tabla_franja_horaria(),
            'movilidad': self.generar_tabla_movilidad(),
            'armas': self.generar_tabla_armas(),
            'ambito': self.generar_tabla_ambito(),
            'matriz_delito_dia': self.generar_matriz_delito_dia(),
            'matriz_delito_franja': self.generar_matriz_delito_franja(),
            'mencionados': self.generar_tabla_mencionados(),
            'aprehendidos': self.generar_tabla_aprehendidos(),
            'aprehendidos_clasificacion': self.generar_tabla_aprehendidos_clasificacion(),
            'esclarecimiento': self.generar_tabla_esclarecimiento(),
        }
        
        if self.report.es_comparativo:
            tablas['comparativa_general'] = self.generar_tabla_comparativa_general()
        
        return tablas
