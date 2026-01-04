"""
Constantes y configuración del sistema S.I.D.I.C
"""
from dataclasses import dataclass
from typing import Dict, List
from enum import Enum

# ═══════════════════════════════════════════════════════════════════════════════
# INFORMACIÓN DE LA APLICACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

APP_NAME = "S.I.D.I.C"
APP_FULL_NAME = "Sistema de Información Delictual e Inteligencia Criminal"
APP_VERSION = "1.0.0"


# ═══════════════════════════════════════════════════════════════════════════════
# FRANJAS HORARIAS
# ═══════════════════════════════════════════════════════════════════════════════

class FranjaHoraria(Enum):
    """Franjas horarias para clasificación de hechos."""
    MADRUGADA = ("MADRUGADA", 0, 4, "00:00-04:59")
    MANANA = ("MAÑANA", 5, 8, "05:00-08:59")
    VESPERTINA = ("VESPERTINA", 9, 12, "09:00-12:59")
    SIESTA = ("SIESTA", 13, 16, "13:00-16:59")
    TARDE = ("TARDE", 17, 19, "17:00-19:59")
    NOCHE = ("NOCHE", 20, 23, "20:00-23:59")

    def __init__(self, nombre: str, hora_inicio: int, hora_fin: int, rango: str):
        self.nombre = nombre
        self.hora_inicio = hora_inicio
        self.hora_fin = hora_fin
        self.rango = rango

    @classmethod
    def from_hour(cls, hour: int) -> 'FranjaHoraria':
        """Obtiene la franja horaria correspondiente a una hora."""
        for franja in cls:
            if franja.hora_inicio <= hour <= franja.hora_fin:
                return franja
        return cls.MADRUGADA

    @property
    def display_name(self) -> str:
        """Nombre para mostrar con rango horario."""
        return f"{self.nombre} ({self.rango})"


# ═══════════════════════════════════════════════════════════════════════════════
# DÍAS DE LA SEMANA
# ═══════════════════════════════════════════════════════════════════════════════

DIAS_SEMANA = [
    "LUNES",
    "MARTES", 
    "MIÉRCOLES",
    "JUEVES",
    "VIERNES",
    "SÁBADO",
    "DOMINGO"
]

# Mapeo de Python weekday (0=Lunes) a nombres
WEEKDAY_TO_NAME = {i: dia for i, dia in enumerate(DIAS_SEMANA)}


# ═══════════════════════════════════════════════════════════════════════════════
# CATEGORÍAS DE DELITOS
# ═══════════════════════════════════════════════════════════════════════════════

class CategoriaDelito(Enum):
    """Categorías principales de delitos."""
    ROBO = "ROBOS"
    HURTO = "HURTOS"
    OTROS = "OTROS DELITOS"


# Delitos considerados como ROBO
DELITOS_ROBO = [
    "ROBO_OPORTUNISTA",
    "ROBO_ARREBATO",
    "ROBO_DE_MOTOVEHICULOS",
    "ROBO_AGRAVADO_DE_MOTOVEHICULOS",
    "ROBO_CLAVERO_DE_AUTOS",
    "TENTATIVA_DE_ROBO_ARREBATO",
    "ROBO_AGRAVADO",
    "ROBO_CON_ARMA",
]

# Delitos considerados como HURTO
DELITOS_HURTO = [
    "HURTO_OPORTUNISTA",
    "HURTO_AUTOMOTOR",
    "HURTO_DE_MOTOVEHICULOS",
    "TENTATIVA_DE_HURTO",
]

# Delitos que califican como "Robo Agravado" (requieren arma)
DELITOS_ROBO_AGRAVADO = [
    "ROBO_AGRAVADO",
    "ROBO_AGRAVADO_DE_MOTOVEHICULOS",
    "ROBO_CON_ARMA",
    "ROBO_AGRAVADO_ASALTANTE",
]


# ═══════════════════════════════════════════════════════════════════════════════
# SÍMBOLOS PARA CUADRO DE REFERENCIA
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SimboloDelito:
    """Símbolo visual para un tipo de delito."""
    simbolo: str
    color: str
    descripcion: str


SIMBOLOS_DELITOS: Dict[str, SimboloDelito] = {
    "ROBO_AGRAVADO_DE_MOTOVEHICULOS": SimboloDelito("▷", "#FFFF00", "Robo Agravado de Motovehículo"),
    "ROBO_ARREBATO": SimboloDelito("△", "#FFFF00", "Robo Arrebato"),
    "ROBO_CLAVERO_DE_AUTOS": SimboloDelito("◢", "#FFFF00", "Robo Clavero de Autos"),
    "ROBO_DE_MOTOVEHICULOS": SimboloDelito("◣", "#FFFF00", "Robo de Motovehículos"),
    "ROBO_OPORTUNISTA": SimboloDelito("▲", "#000000", "Robo Oportunista"),
    "TENTATIVA_DE_ROBO_ARREBATO": SimboloDelito("◇", "#FFFF00", "Tentativa de Robo Arrebato"),
    "HURTO_OPORTUNISTA": SimboloDelito("●", "#000000", "Hurto Oportunista"),
    "HURTO_AUTOMOTOR": SimboloDelito("○", "#0000FF", "Hurto Automotor"),
    "ESCLARECIDO_PARCIAL": SimboloDelito("◎", "#00FF00", "Hecho Esclarecido Parcialmente"),
    "ESCLARECIDO_TOTAL": SimboloDelito("◉", "#00FF00", "Hecho Esclarecido Totalmente"),
    "COMISARIA": SimboloDelito("Ⓟ", "#0000FF", "Comisaría Jurisdiccional"),
}


# ═══════════════════════════════════════════════════════════════════════════════
# ÁMBITOS DE OCURRENCIA
# ═══════════════════════════════════════════════════════════════════════════════

AMBITOS_OCURRENCIA = [
    "VIA_PUBLICA",
    "VIVIENDA",
    "COMERCIO",
    "TRANSPORTE_PUBLICO",
    "ESTABLECIMIENTO_EDUCATIVO",
    "OTRO",
]


# ═══════════════════════════════════════════════════════════════════════════════
# MEDIOS DE MOVILIDAD
# ═══════════════════════════════════════════════════════════════════════════════

MEDIOS_MOVILIDAD = [
    "A_PIE",
    "MOTOCICLETA",
    "AUTOMOVIL",
    "BICICLETA",
    "#NO_CONSTA",
]


# ═══════════════════════════════════════════════════════════════════════════════
# ARMAS/MEDIOS UTILIZADOS
# ═══════════════════════════════════════════════════════════════════════════════

ARMAS_MEDIOS = [
    "ARMA_DE_FUEGO",
    "ARMA_BLANCA",
    "OBJETO_CONTUNDENTE",
    "SIMULACRO_DE_ARMA",
    "FUERZA_FISICA",
    "#NO_CONSTA",
]


# ═══════════════════════════════════════════════════════════════════════════════
# CLASIFICACIÓN DE APREHENDIDOS
# ═══════════════════════════════════════════════════════════════════════════════

CLASIFICACION_APREHENDIDOS = [
    "MAYOR_CON_ANTECEDENTES",
    "MAYOR_PRIMERIZO",
    "MENOR_CON_ANTECEDENTES",
    "MENOR_PRIMERIZO",
]


# ═══════════════════════════════════════════════════════════════════════════════
# MAPEO DE CAMPOS (CONFIGURACIÓN POR DEFECTO)
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_FIELD_MAPPING = {
    "hechos": {
        "fecha": ["FECHA", "FEC_HECHO", "fecha_hecho", "FECHA_HECHO"],
        "hora": ["HORA", "HOR_HECHO", "hora_hecho", "HORA_HECHO"],
        "delito": ["DELITO", "TIPO_DELITO", "modalidad", "MODALIDAD"],
        "ambito": ["AMBITO", "AMB_OCURR", "lugar", "LUGAR_HECHO"],
        "movilidad": ["MOVILIDAD", "MEDIO_MOV", "transporte", "MEDIO_MOVILIDAD"],
        "arma": ["ARMA", "MEDIO_ARMA", "arma_utilizada", "ARMA_MEDIO"],
        "esclarecido": ["ESCLAREC", "ESTADO", "resuelto", "ESCLARECIDO"],
        "direccion": ["DIRECCION", "DOMICILIO", "CALLE", "UBICACION"],
    },
    "mencionados": {
        "alias": ["ALIAS", "NOMBRE", "UN_TAL", "MENCIONADO"],
        "delito": ["DELITO", "TIPO_DELITO", "HECHO"],
        "fecha": ["FECHA", "FEC_HECHO"],
        "hora": ["HORA", "HOR_HECHO"],
        "direccion": ["DIRECCION", "LUGAR", "DOMICILIO_HECHO"],
        "datos": ["DATOS", "DESCRIPCION", "FILIACION", "DATOS_FILIATORIOS"],
    },
    "aprehendidos": {
        "nombre": ["NOMBRE", "APELLIDO_NOMBRE", "IDENTIDAD"],
        "clasificacion": ["CLASIFICACION", "CATEGORIA", "TIPO"],
        "delito": ["DELITO", "CAUSA"],
        "fecha": ["FECHA", "FEC_APREH"],
        "edad": ["EDAD", "ANOS"],
        "sexo": ["SEXO", "GENERO"],
    },
}


# ═══════════════════════════════════════════════════════════════════════════════
# COLORES DEL TEMA POLICIAL
# ═══════════════════════════════════════════════════════════════════════════════

class ColoresPolicial:
    """Paleta de colores del tema policial ultramoderno."""
    
    # Fondos
    FONDO_PRINCIPAL = "#0a0a12"
    FONDO_SECUNDARIO = "#0f0f1a"
    FONDO_PANEL = "#1a1a2e"
    FONDO_CARD = "#16213e"
    
    # Acentos
    CYAN_NEON = "#00d4ff"
    CYAN_OSCURO = "#0099cc"
    ROJO_ALERTA = "#ff3b3b"
    ROJO_OSCURO = "#cc0000"
    VERDE_EXITO = "#00ff88"
    VERDE_OSCURO = "#00cc66"
    AMARILLO_WARNING = "#ffaa00"
    NARANJA = "#ff6600"
    
    # Texto
    TEXTO_PRINCIPAL = "#e0e0e0"
    TEXTO_SECUNDARIO = "#a0a0a0"
    TEXTO_TITULO = "#ffffff"
    
    # Bordes
    BORDE_ACTIVO = "#00d4ff"
    BORDE_INACTIVO = "#2a2a4a"
    
    # Excel/Reportes
    EXCEL_HEADER_BG = "#FF0000"  # Rojo
    EXCEL_HEADER_FG = "#FFFFFF"  # Blanco
    EXCEL_TOTAL_BG = "#FFFF00"   # Amarillo
    EXCEL_TOTAL_FG = "#000000"   # Negro
    EXCEL_SUBTOTAL_BG = "#0000FF"  # Azul
    EXCEL_SUBTOTAL_FG = "#FFFFFF"  # Blanco
    EXCEL_ALTERNADO_1 = "#FFFFFF"
    EXCEL_ALTERNADO_2 = "#F0F0F0"


# ═══════════════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE GRÁFICOS
# ═══════════════════════════════════════════════════════════════════════════════

CHART_CONFIG = {
    "figure_size": (10, 6),
    "dpi": 150,
    "bar_color": "#4169E1",  # Azul Royal
    "bar_edge_color": "#000000",
    "font_family": "Segoe UI",
    "title_font_size": 14,
    "label_font_size": 10,
    "tick_font_size": 9,
    "grid_alpha": 0.3,
    "background_color": "#FFFFFF",
}

# Colores para gráficos de barras agrupadas por delito
COLORES_DELITOS = {
    "HURTO_OPORTUNISTA": "#9400D3",      # Violeta
    "ROBO_OPORTUNISTA": "#32CD32",        # Verde lima
    "ROBO_DE_MOTOVEHICULOS": "#0000CD",   # Azul medio
    "ROBO_AGRAVADO_DE_MOTOVEHICULOS": "#800080",  # Púrpura
    "ROBO_ARREBATO": "#FF0000",           # Rojo
    "ROBO_CLAVERO_DE_AUTOS": "#FF8C00",   # Naranja oscuro
    "TENTATIVA_DE_ROBO_ARREBATO": "#00CED1",  # Turquesa
}
