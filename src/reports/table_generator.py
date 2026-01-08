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
    # CUADRO DE REFERENCIA (Layout 2 columnas: Consumados | Tentativas)
    # ═══════════════════════════════════════════════════════════════════════
    
    def generar_cuadro_referencia(self) -> pd.DataFrame:
        """
        Genera el cuadro de referencia para mapas.
        
        Incluye símbolos, categorías, subtotales y totales.
        Layout: 2 columnas (Consumados | Tentativas) como la imagen de referencia.
        """
        if not self.periodo:
            return pd.DataFrame()
        
        filas = self.periodo.cuadro_referencia()
        
        data = []
        for fila in filas:
            tipo = fila['tipo']
            texto = fila['texto']
            cantidad = fila['cantidad']
            
            # Normalizar el delito antes de buscar
            from ..core.field_mapper import normalizar_delito
            texto_normalizado = normalizar_delito(texto)
            
            # Obtener símbolo si es delito
            simbolo = ""
            color = ""
            if tipo == 'delito':
                if texto_normalizado in SIMBOLOS_DELITOS:
                    sim = SIMBOLOS_DELITOS[texto_normalizado]
                    simbolo = sim.simbolo
                    color = sim.color
                elif texto in SIMBOLOS_DELITOS:
                    sim = SIMBOLOS_DELITOS[texto]
                    simbolo = sim.simbolo
                    color = sim.color
                else:
                    simbolo = "●"
                    color = "#888888"
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
    
    def generar_cuadro_referencia_doble_columna(self) -> pd.DataFrame:
        """
        Genera el cuadro de referencia con layout de 2 columnas.
        
        Columna izquierda: Delitos consumados
        Columna derecha: Tentativas correspondientes
        
        Returns:
            DataFrame con columnas:
            - Símbolo_Consumado, Delito_Consumado, Cant_Consumado, Color_Consumado
            - Símbolo_Tentativa, Delito_Tentativa, Cant_Tentativa, Color_Tentativa
        """
        from ..utils.constants import ORDEN_DELITOS_CONSUMADOS, ORDEN_DELITOS_TENTATIVAS
        from ..core.field_mapper import normalizar_delito
        
        if not self.periodo:
            return pd.DataFrame()
        
        # Obtener conteo de delitos
        conteo = self.periodo.conteo_por_delito()
        
        # Normalizar claves del conteo
        conteo_normalizado = {}
        for k, v in conteo.items():
            k_norm = normalizar_delito(k)
            if k_norm in conteo_normalizado:
                conteo_normalizado[k_norm] += v
            else:
                conteo_normalizado[k_norm] = v
        
        data = []
        
        # Iterar sobre las listas ordenadas
        for i, delito_cons in enumerate(ORDEN_DELITOS_CONSUMADOS):
            delito_tent = ORDEN_DELITOS_TENTATIVAS[i] if i < len(ORDEN_DELITOS_TENTATIVAS) else ""
            
            # Consumado
            sim_cons = SIMBOLOS_DELITOS.get(delito_cons)
            cant_cons = conteo_normalizado.get(delito_cons, 0)
            
            # Tentativa
            sim_tent = SIMBOLOS_DELITOS.get(delito_tent)
            cant_tent = conteo_normalizado.get(delito_tent, 0)
            
            row = {
                'Símbolo': sim_cons.simbolo if sim_cons else '',
                'Delito Consumado': delito_cons.replace('_', ' '),
                'Cant': cant_cons,
                'Color': sim_cons.color if sim_cons else '',
                'Símbolo_T': sim_tent.simbolo if sim_tent else '',
                'Tentativa': delito_tent.replace('TENTATIVA DE ', '').replace('_', ' ') if delito_tent else '',
                'Cant_T': cant_tent,
                'Color_T': sim_tent.color if sim_tent else '',
            }
            data.append(row)
        
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
        
        # Validar que ambos períodos existan
        if not p1 or not p2:
            return self.generar_tabla_delitos()
        
        try:
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
                    'Variación': comp.porcentaje_formateado if hasattr(comp, 'porcentaje_formateado') else 'N/A',
                    'Tendencia': comp.tendencia_icono if hasattr(comp, 'tendencia_icono') else ''
                })
            
            # Total
            total_comp = comparator.resumen_general().get('total_hechos')
            if total_comp:
                data.append({
                    'DELITOS CON MODALIDADES': 'TOTAL DE HECHOS',
                    p1.rango_fechas: total_p1,
                    '%': '100,00%',
                    p2.rango_fechas: total_p2,
                    '% ': '100,00%',
                    'Variación': total_comp.porcentaje_formateado if hasattr(total_comp, 'porcentaje_formateado') else 'N/A',
                    'Tendencia': total_comp.tendencia_icono if hasattr(total_comp, 'tendencia_icono') else ''
                })
            
            return pd.DataFrame(data)
        
        except Exception as e:
            print(f"Error generando tabla comparativa de delitos: {e}")
            return self.generar_tabla_delitos()
    
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
        Genera matriz de delitos CON MODALIDAD por día de la semana.
        """
        if not self.periodo:
            return pd.DataFrame()
        
        # Usar matriz con modalidades
        matriz = self.periodo.matriz_delito_modalidad_dia()
        
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
        Genera matriz de delitos CON MODALIDAD por franja horaria.
        """
        if not self.periodo:
            return pd.DataFrame()
        
        # Usar matriz con modalidades
        matriz = self.periodo.matriz_delito_modalidad_franja()
        
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
        
        p1 = self.report.periodo_principal
        p2 = self.report.periodo_comparacion
        
        # Validar que ambos períodos existan
        if not p1 or not p2:
            return pd.DataFrame()
        
        try:
            comparator = PeriodComparator(p1, p2)
            filas = comparator.to_comparison_table()
            
            if not filas:
                return pd.DataFrame()
            
            return pd.DataFrame(filas)
        
        except Exception as e:
            print(f"Error generando tabla comparativa general: {e}")
            return pd.DataFrame()
    
    # ═══════════════════════════════════════════════════════════════════════
    # GENERAR TODAS LAS TABLAS
    # ═══════════════════════════════════════════════════════════════════════
    
    def generar_todas(self) -> Dict[str, pd.DataFrame]:
        """
        Genera todas las tablas del reporte.
        
        Returns:
            Diccionario {nombre_tabla: DataFrame}
        """
        tablas = {}
        
        # Generar cada tabla con manejo de errores
        try:
            tablas['cuadro_referencia'] = self.generar_cuadro_referencia()
        except Exception as e:
            print(f"Error generando cuadro_referencia: {e}")
            tablas['cuadro_referencia'] = pd.DataFrame()
        
        try:
            if self.report.es_comparativo:
                tablas['delitos'] = self.generar_tabla_delitos_comparativa()
            else:
                tablas['delitos'] = self.generar_tabla_delitos()
        except Exception as e:
            print(f"Error generando tabla delitos: {e}")
            tablas['delitos'] = pd.DataFrame()
        
        try:
            tablas['dias_semana'] = self.generar_tabla_dias_semana()
        except Exception as e:
            print(f"Error generando dias_semana: {e}")
            tablas['dias_semana'] = pd.DataFrame()
        
        try:
            tablas['franja_horaria'] = self.generar_tabla_franja_horaria()
        except Exception as e:
            print(f"Error generando franja_horaria: {e}")
            tablas['franja_horaria'] = pd.DataFrame()
        
        try:
            tablas['movilidad'] = self.generar_tabla_movilidad()
        except Exception as e:
            print(f"Error generando movilidad: {e}")
            tablas['movilidad'] = pd.DataFrame()
        
        try:
            tablas['armas'] = self.generar_tabla_armas()
        except Exception as e:
            print(f"Error generando armas: {e}")
            tablas['armas'] = pd.DataFrame()
        
        try:
            tablas['ambito'] = self.generar_tabla_ambito()
        except Exception as e:
            print(f"Error generando ambito: {e}")
            tablas['ambito'] = pd.DataFrame()
        
        try:
            tablas['matriz_delito_dia'] = self.generar_matriz_delito_dia()
        except Exception as e:
            print(f"Error generando matriz_delito_dia: {e}")
            tablas['matriz_delito_dia'] = pd.DataFrame()
        
        try:
            tablas['matriz_delito_franja'] = self.generar_matriz_delito_franja()
        except Exception as e:
            print(f"Error generando matriz_delito_franja: {e}")
            tablas['matriz_delito_franja'] = pd.DataFrame()
        
        try:
            tablas['mencionados'] = self.generar_tabla_mencionados()
        except Exception as e:
            print(f"Error generando mencionados: {e}")
            tablas['mencionados'] = pd.DataFrame()
        
        try:
            tablas['aprehendidos'] = self.generar_tabla_aprehendidos()
        except Exception as e:
            print(f"Error generando aprehendidos: {e}")
            tablas['aprehendidos'] = pd.DataFrame()
        
        try:
            tablas['aprehendidos_clasificacion'] = self.generar_tabla_aprehendidos_clasificacion()
        except Exception as e:
            print(f"Error generando aprehendidos_clasificacion: {e}")
            tablas['aprehendidos_clasificacion'] = pd.DataFrame()
        
        try:
            tablas['esclarecimiento'] = self.generar_tabla_esclarecimiento()
        except Exception as e:
            print(f"Error generando esclarecimiento: {e}")
            tablas['esclarecimiento'] = pd.DataFrame()
        
        # Tabla comparativa general solo para reportes comparativos
        if self.report.es_comparativo:
            try:
                tablas['comparativa_general'] = self.generar_tabla_comparativa_general()
            except Exception as e:
                print(f"Error generando comparativa_general: {e}")
                tablas['comparativa_general'] = pd.DataFrame()
        
        return tablas
