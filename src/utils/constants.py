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
    TENTATIVA_ROBO = "TENTATIVA DE ROBOS"
    HURTO = "HURTOS"
    TENTATIVA_HURTO = "TENTATIVA DE HURTOS"
    ESTAFA = "ESTAFAS"
    OTROS = "OTROS DELITOS"


# Delitos considerados como ROBO
DELITOS_ROBO = [
    "ROBO AGRAVADO ASALTANTE",
    "ROBO AGRAVADO ASALTANTE EN BANDA",
    "ROBO AGRAVADO DE MOTOVEHICULO",
    "ROBO AGRAVADO PIRAÑA DE MOTOVEHICULO",
    "ROBO AGRAVADO DE AUTOMOTOR",
    "ROBO AGRAVADO ENTRADERA",
    "ROBO AGRAVADO ARIETE",
    "ROBO PIRAÑA DE MOTOVEHICULOS",
    "ROBO PIRAÑA",
    "ROBO ARREBATO",
    "ROBO CLAVERO DE AUTOS",
    "ROBO DE MOTOVEHICULOS",
    "ROBO DE AUTOMOTOR",
    "ROBO ESCRUCHE",
    "ROBO BOQUETERO",
    "ROBO ROMPE VIDRIO",
    "ROBO OPORTUNISTA",
]

# Tentativas de robo
DELITOS_TENTATIVA_ROBO = [
    "TENTATIVA DE ROBO AGRAVADO ASALTANTE",
    "TENTATIVA DE ROBO AGRAVADO ASALTANTE EN BANDA",
    "TENTATIVA DE ROBO AGRAVADO DE MOTOVEHICULO",
    "TENTATIVA DE ROBO AGRAVADO PIRAÑA DE MOTOVEHICULO",
    "TENTATIVA DE ROBO AGRAVADO DE AUTOMOTOR",
    "TENTATIVA DE ROBO AGRAVADO ENTRADERA",
    "TENTATIVA DE ROBO AGRAVADO ARIETE",
    "TENTATIVA DE ROBO PIRAÑA DE MOTOVEHICULOS",
    "TENTATIVA DE ROBO PIRAÑA",
    "TENTATIVA DE ROBO ARREBATO",
    "TENTATIVA DE ROBO CLAVERO DE AUTOS",
    "TENTATIVA DE ROBO DE MOTOVEHICULOS",
    "TENTATIVA DE ROBO DE AUTOMOTOR",
    "TENTATIVA DE ROBO ESCRUCHE",
    "TENTATIVA DE ROBO BOQUETERO",
    "TENTATIVA DE ROBO ROMPE VIDRIO",
    "TENTATIVA DE ROBO OPORTUNISTA",
]

# Delitos considerados como HURTO
DELITOS_HURTO = [
    "HURTO PUNGA",
    "HURTO MECHERA",
    "HURTO OPORTUNISTA",
    "HURTO DE MOTOVEHICULO",
    "HURTO DE AUTOMOTOR",
    "HURTO INHIBIDOR DE ALARMAS",
    "HURTO ESCALAMIENTO",
    "HURTO VIUDA NEGRA",
]

# Tentativas de hurto
DELITOS_TENTATIVA_HURTO = [
    "TENTATIVA DE HURTO PUNGA",
    "TENTATIVA DE HURTO MECHERA",
    "TENTATIVA DE HURTO OPORTUNISTA",
    "TENTATIVA DE HURTO DE MOTOVEHICULO",
    "TENTATIVA DE HURTO DE AUTOMOTOR",
    "TENTATIVA DE HURTO INHIBIDOR DE ALARMAS",
    "TENTATIVA DE HURTO ESCALAMIENTO",
    "TENTATIVA DE HURTO VIUDA NEGRA",
]

# Estafas
DELITOS_ESTAFA = [
    "ESTAFA CUENTO DEL TIO",
    "TENTATIVA DE ESTAFA CUENTO DEL TIO",
]

# Delitos que califican como "Robo Agravado" (requieren arma)
DELITOS_ROBO_AGRAVADO = [
    "ROBO AGRAVADO ASALTANTE",
    "ROBO AGRAVADO ASALTANTE EN BANDA",
    "ROBO AGRAVADO DE MOTOVEHICULO",
    "ROBO AGRAVADO PIRAÑA DE MOTOVEHICULO",
    "ROBO AGRAVADO DE AUTOMOTOR",
    "ROBO AGRAVADO ENTRADERA",
    "ROBO AGRAVADO ARIETE",
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
    relleno: bool = True


# Símbolos según cuadro de referencia oficial
# IMPORTANTE: Los símbolos y colores están definidos según la imagen de referencia policial
SIMBOLOS_DELITOS: Dict[str, SimboloDelito] = {
    # ═══════════════════════════════════════════════════════════════════════
    # ROBOS CONSUMADOS (columna izquierda de la imagen)
    # ═══════════════════════════════════════════════════════════════════════
    
    # Robos Agravados
    "ROBO AGRAVADO ASALTANTE": SimboloDelito("▲", "#FF0000", "Robo Agravado Asaltante", True),
    "ROBO AGRAVADO ASALTANTE EN BANDA": SimboloDelito("△", "#FFFF00", "Robo Agravado Asaltante en Banda", False),
    "ROBO AGRAVADO DE MOTOVEHICULO": SimboloDelito("▷", "#00FF00", "Robo Agravado de Motovehículo", True),
    "ROBO AGRAVADO PIRAÑA DE MOTOVEHICULO": SimboloDelito("▶", "#FF0000", "Robo Agravado Piraña de Motovehículo", True),
    "ROBO AGRAVADO DE AUTOMOTOR": SimboloDelito("▷", "#FFFFFF", "Robo Agravado de Automotor", False),
    "ROBO AGRAVADO ENTRADERA": SimboloDelito("▷", "#00FF00", "Robo Agravado Entradera", True),
    "ROBO AGRAVADO ARIETE": SimboloDelito("▶", "#0000FF", "Robo Agravado Ariete", True),
    
    # Robos Simples
    "ROBO PIRAÑA DE MOTOVEHICULOS": SimboloDelito("⬠", "#00FF00", "Robo Piraña de Motovehículos", True),
    "ROBO PIRAÑA": SimboloDelito("⬡", "#0000FF", "Robo Piraña", True),
    "ROBO ARREBATO": SimboloDelito("△", "#FFFF00", "Robo Arrebato", False),
    "ROBO CLAVERO DE AUTOS": SimboloDelito("△", "#00FF00", "Robo Clavero de Autos", False),
    "ROBO DE MOTOVEHICULOS": SimboloDelito("△", "#00FF00", "Robo de Motovehículos", False),
    "ROBO DE AUTOMOTOR": SimboloDelito("△", "#FFFFFF", "Robo de Automotor", False),
    "ROBO ESCRUCHE": SimboloDelito("■", "#FF0000", "Robo Escruche", True),
    "ROBO BOQUETERO": SimboloDelito("■", "#00FF00", "Robo Boquetero", True),
    "ROBO ROMPE VIDRIO": SimboloDelito("▶", "#0000FF", "Robo Rompe Vidrio", True),
    "ROBO OPORTUNISTA": SimboloDelito("▲", "#000000", "Robo Oportunista", True),
    
    # ═══════════════════════════════════════════════════════════════════════
    # TENTATIVAS DE ROBO (columna derecha de la imagen - símbolos sin relleno)
    # ═══════════════════════════════════════════════════════════════════════
    
    "TENTATIVA DE ROBO AGRAVADO ASALTANTE": SimboloDelito("△", "#FF0000", "Tentativa de Robo Agravado Asaltante", False),
    "TENTATIVA DE ROBO AGRAVADO ASALTANTE EN BANDA": SimboloDelito("△", "#FFFF00", "Tentativa de Robo Agravado Asaltante en Banda", False),
    "TENTATIVA DE ROBO AGRAVADO DE MOTOVEHICULO": SimboloDelito("▷", "#00FF00", "Tentativa de Robo Agravado de Motovehículo", False),
    "TENTATIVA DE ROBO AGRAVADO PIRAÑA DE MOTOVEHICULO": SimboloDelito("▷", "#FF0000", "Tentativa de Robo Agravado Piraña de Motovehículo", False),
    "TENTATIVA DE ROBO AGRAVADO DE AUTOMOTOR": SimboloDelito("▷", "#FFFFFF", "Tentativa de Robo Agravado de Automotor", False),
    "TENTATIVA DE ROBO AGRAVADO ENTRADERA": SimboloDelito("▷", "#00FF00", "Tentativa de Robo Agravado Entradera", False),
    "TENTATIVA DE ROBO AGRAVADO ARIETE": SimboloDelito("▷", "#0000FF", "Tentativa de Robo Agravado Ariete", False),
    "TENTATIVA DE ROBO PIRAÑA DE MOTOVEHICULO": SimboloDelito("⬡", "#00FF00", "Tentativa de Robo Piraña de Motovehículo", False),
    "TENTATIVA DE ROBO PIRAÑA": SimboloDelito("⬡", "#0000FF", "Tentativa de Robo Piraña", False),
    "TENTATIVA DE ROBO ARREBATO": SimboloDelito("△", "#FFFF00", "Tentativa de Robo Arrebato", False),
    "TENTATIVA DE ROBO CLAVERO DE AUTOS": SimboloDelito("△", "#00FF00", "Tentativa de Robo Clavero de Autos", False),
    "TENTATIVA DE ROBO DE MOTOVEHICULOS": SimboloDelito("△", "#00FF00", "Tentativa de Robo de Motovehículos", False),
    "TENTATIVA DE ROBO DE AUTOMOTOR": SimboloDelito("△", "#FFFFFF", "Tentativa de Robo de Automotor", False),
    "TENTATIVA DE ROBO ESCRUCHE": SimboloDelito("□", "#FF0000", "Tentativa de Robo Escruche", False),
    "TENTATIVA DE ROBO BOQUETERO": SimboloDelito("□", "#00FF00", "Tentativa de Robo Boquetero", False),
    "TENTATIVA DE ROBO ROMPE VIDRIO": SimboloDelito("▷", "#0000FF", "Tentativa de Robo Rompe Vidrio", False),
    "TENTATIVA DE ROBO OPORTUNISTA": SimboloDelito("△", "#000000", "Tentativa de Robo Oportunista", False),
    
    # ═══════════════════════════════════════════════════════════════════════
    # HURTOS CONSUMADOS (círculos con relleno)
    # ═══════════════════════════════════════════════════════════════════════
    
    "HURTO PUNGA": SimboloDelito("●", "#0000FF", "Hurto Punga", True),
    "HURTO MECHERA": SimboloDelito("●", "#00FF00", "Hurto Mechera", True),
    "HURTO OPORTUNISTA": SimboloDelito("●", "#FFFF00", "Hurto Oportunista", True),
    "HURTO DE MOTOVEHICULO": SimboloDelito("●", "#FF0000", "Hurto de Motovehículo", True),
    "HURTO DE AUTOMOTOR": SimboloDelito("●", "#808080", "Hurto de Automotor", True),
    "HURTO INHIBIDOR DE ALARMAS": SimboloDelito("○", "#FFFFFF", "Hurto Inhibidor de Alarmas", False),
    "HURTO ESCALAMIENTO": SimboloDelito("●", "#FFA500", "Hurto Escalamiento", True),
    "HURTO VIUDA NEGRA": SimboloDelito("●", "#000000", "Hurto Viuda Negra", True),
    
    # ═══════════════════════════════════════════════════════════════════════
    # TENTATIVAS DE HURTO (círculos sin relleno)
    # ═══════════════════════════════════════════════════════════════════════
    
    "TENTATIVA DE HURTO PUNGA": SimboloDelito("○", "#0000FF", "Tentativa de Hurto Punga", False),
    "TENTATIVA DE HURTO MECHERA": SimboloDelito("○", "#00FF00", "Tentativa de Hurto Mechera", False),
    "TENTATIVA DE HURTO OPORTUNISTA": SimboloDelito("○", "#FFFF00", "Tentativa de Hurto Oportunista", False),
    "TENTATIVA DE HURTO DE MOTOVEHICULO": SimboloDelito("○", "#FF0000", "Tentativa de Hurto de Motovehículo", False),
    "TENTATIVA DE HURTO DE AUTOMOTOR": SimboloDelito("○", "#808080", "Tentativa de Hurto de Automotor", False),
    "TENTATIVA DE HURTO INHIBIDOR DE ALARMAS": SimboloDelito("○", "#FFFFFF", "Tentativa de Hurto Inhibidor de Alarmas", False),
    "TENTATIVA DE HURTO ESCALAMIENTO": SimboloDelito("○", "#FFA500", "Tentativa de Hurto Escalamiento", False),
    "TENTATIVA DE HURTO VIUDA NEGRA": SimboloDelito("○", "#000000", "Tentativa de Hurto Viuda Negra", False),
    
    # ═══════════════════════════════════════════════════════════════════════
    # ESTAFAS (rombos)
    # ═══════════════════════════════════════════════════════════════════════
    
    "ESTAFA CUENTO DEL TIO": SimboloDelito("◆", "#0000FF", "Estafa Cuento del Tío", True),
    "TENTATIVA DE ESTAFA CUENTO DEL TIO": SimboloDelito("◇", "#0000FF", "Tentativa de Estafa Cuento del Tío", False),
    
    # ═══════════════════════════════════════════════════════════════════════
    # INDICADORES ESPECIALES
    # ═══════════════════════════════════════════════════════════════════════
    
    "ESCLARECIDO": SimboloDelito("◉", "#00FF00", "Hecho Esclarecido", True),
    "COMISARIA": SimboloDelito("Ⓟ", "#0000FF", "Comisaría Jurisdiccional", True),
}


# Lista ordenada de delitos para cuadro de referencia (consumados)
ORDEN_DELITOS_CONSUMADOS = [
    "ROBO AGRAVADO ASALTANTE",
    "ROBO AGRAVADO ASALTANTE EN BANDA",
    "ROBO AGRAVADO DE MOTOVEHICULO",
    "ROBO AGRAVADO PIRAÑA DE MOTOVEHICULO",
    "ROBO AGRAVADO DE AUTOMOTOR",
    "ROBO AGRAVADO ENTRADERA",
    "ROBO AGRAVADO ARIETE",
    "ROBO PIRAÑA DE MOTOVEHICULOS",
    "ROBO PIRAÑA",
    "ROBO ARREBATO",
    "ROBO CLAVERO DE AUTOS",
    "ROBO DE MOTOVEHICULOS",
    "ROBO DE AUTOMOTOR",
    "ROBO ESCRUCHE",
    "ROBO BOQUETERO",
    "ROBO ROMPE VIDRIO",
    "ROBO OPORTUNISTA",
    "HURTO PUNGA",
    "HURTO MECHERA",
    "HURTO OPORTUNISTA",
    "HURTO DE MOTOVEHICULO",
    "HURTO DE AUTOMOTOR",
    "HURTO INHIBIDOR DE ALARMAS",
    "HURTO ESCALAMIENTO",
    "HURTO VIUDA NEGRA",
    "ESTAFA CUENTO DEL TIO",
]

# Lista ordenada de tentativas para cuadro de referencia
ORDEN_DELITOS_TENTATIVAS = [
    "TENTATIVA DE ROBO AGRAVADO ASALTANTE",
    "TENTATIVA DE ROBO AGRAVADO ASALTANTE EN BANDA",
    "TENTATIVA DE ROBO AGRAVADO DE MOTOVEHICULO",
    "TENTATIVA DE ROBO AGRAVADO PIRAÑA DE MOTOVEHICULO",
    "TENTATIVA DE ROBO AGRAVADO DE AUTOMOTOR",
    "TENTATIVA DE ROBO AGRAVADO ENTRADERA",
    "TENTATIVA DE ROBO AGRAVADO ARIETE",
    "TENTATIVA DE ROBO PIRAÑA DE MOTOVEHICULO",
    "TENTATIVA DE ROBO PIRAÑA",
    "TENTATIVA DE ROBO ARREBATO",
    "TENTATIVA DE ROBO CLAVERO DE AUTOS",
    "TENTATIVA DE ROBO DE MOTOVEHICULOS",
    "TENTATIVA DE ROBO DE AUTOMOTOR",
    "TENTATIVA DE ROBO ESCRUCHE",
    "TENTATIVA DE ROBO BOQUETERO",
    "TENTATIVA DE ROBO ROMPE VIDRIO",
    "TENTATIVA DE ROBO OPORTUNISTA",
    "TENTATIVA DE HURTO PUNGA",
    "TENTATIVA DE HURTO MECHERA",
    "TENTATIVA DE HURTO OPORTUNISTA",
    "TENTATIVA DE HURTO DE MOTOVEHICULO",
    "TENTATIVA DE HURTO DE AUTOMOTOR",
    "TENTATIVA DE HURTO INHIBIDOR DE ALARMAS",
    "TENTATIVA DE HURTO ESCALAMIENTO",
    "TENTATIVA DE HURTO VIUDA NEGRA",
    "TENTATIVA DE ESTAFA CUENTO DEL TIO",
]


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
# Nota: Los nombres de campo DBF están truncados a 10 caracteres
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_FIELD_MAPPING = {
    "hechos": {
        # Campos truncados del DBF (máx 10 caracteres) primero
        "nro_sumario": ["ID_N_SRIO", "Nº DE IMAGEN-SUMARIO Nº", "NRO_SUMAR", "SUMARIO"],
        "jurisdiccion": ["JURIS_HECH", "JURISDICCION DONDE TUVO LUGAR EL DELITO", "JURISDICCION", "JURISD"],
        "dependencia": ["DPCIA_INT", "DEPENDENCIA INTERVINIENTE", "DEPENDENCIA", "COMISARIA"],
        "fecha": ["FECHA_HECH", "FECHA DEL DELITO", "FECHA", "FEC_HECHO"],
        "dia_semana": ["DIA_HECHO", "DIA EN QUE OCURRIO EL HECHO", "DIA", "DIA_SEMANA"],
        "hora": ["HORA_HECH", "HORA DEL DELITO", "HORA", "HORA_HECHO"],
        "franja_horaria": ["FRAN_HORAR", "FRANJA HORARIA EN QUE OCURRIO EL DELITO", "FRANJA_HOR", "FRANJA"],
        "direccion": ["DIREC_HECH", "DIRECCION DONDE OCURRIO EL DELITO", "DIRECCION", "DIR_HECHO", "CALLE"],
        "ambito": ["LUGR_HECHO", "LUGAR DONDE TUVO LUGAR EL DELITO", "AMBITO", "LUGAR", "TIPO_LUGAR"],
        "detalle_lugar": ["DET_LUG_HE", "DETALLE DEL LUGAR DONDE OCURRIO EL DELITO"],
        "delito": ["DELITO", "DELITO COMETIDO", "TIPO_DELIT", "MODALIDAD"],
        "modus_operandi": ["MODUS_OPER", "MODUS OPERANDI", "MODUS", "MOD_OPER"],
        "movilidad": ["VEHIC_UTIL", "VEHICULOS UTILIZADOS", "MOVILIDAD", "VEHICULO", "MEDIO_MOV"],
        "descripcion_vehiculo": ["DET_VEHIC", "DESCRIPCION DEL O LOS VEHICULOS UTILIZADOS"],
        "arma": ["ARMA_UTILI", "ARMA UTILIZADA", "ARMA", "TIPO_ARMA", "MEDIO_ARMA"],
        "detalle_arma": ["DET_ARMA", "DETALLE DEL ARMA UTILIZADA"],
        "elemento_sustraido": ["ELEMN_SUST", "ELEMENTO SUSTRAIDO", "ELEM_SUST"],
        "detalle_elemento": ["DET_ELE_SU", "DETALLE DEL ELEMENTO SUSTRAIDO"],
        "resena_hecho": ["RESEN_HECH", "RESENA_HECHO"],
        "sexo_victima": ["SEXO_VICTI", "SEXO DE LA VICTIMA", "SEXO_VICT"],
        "edad_victima": ["EDAD_VICTI", "EDAD DE LA VICTIMA", "EDAD_VICT"],
        "nombre_victima": ["AP_NOM_VIC", "APELLIDO Y NOMBRE DE LA VICTIMA"],
        "dni_victima": ["DNI_VICTIM", "DNI_VICTIMA"],
        "direccion_victima": ["DIREC_VICT", "DIRECCION_VICTIMA"],
        "nombre_causante": ["AP_NOM_CAU", "APELLIDO Y NOMBRE DEL CAUSANTE", "CAUSANTE"],
        "sexo_causante": ["SEXO_CAUS", "SEXO DEL CAUSANTE"],
        "edad_causante": ["EDAD_CAUSA", "EDAD DEL CAUSANTE", "EDAD_CAUS"],
        "dni_causante": ["DNI_CAUSAN", "DNI_CAUSANTE"],
        "direccion_causante": ["DIREC_CAUS", "DIRECCION DEL CAUSANTE"],
        "descripcion_causante": ["DESC_CAUS", "DESCRIPCION_CAUSANTE"],
        "esclarecido": ["HECH_RESUE", "EL HECHO FUE RESUELTO", "ESCLAREC", "RESUELTO", "ESTADO"],
        "resolucion_hecho": ["RESOL_HECH", "RESOLUCION_HECHO"],
        "situacion_causante": ["SITUA_CAUS", "SITUACION DEL CAUSANTE", "SIT_CAUS"],
        "mes": ["MES_DENU", "MES EN QUE OCURRIO EL DELITO", "MES"],
        "barrio": ["PRDA_URBAN", "PARADA_URBANA", "BARRIO"],
        "coordenada_x": ["X"],
        "coordenada_y": ["Y"],
    },
    "mencionados": {
        "alias": ["ALIAS", "alias", "APODO", "TAL", "CONOCIDO"],
        "nombre": ["AP_NOM_CAU", "APELLIDO Y NOMBRE DEL CAUSANTE", "NOMBRE", "CAUSANTE"],
        "delito": ["DELITO", "DELITO COMETIDO", "TIPO_DELIT"],
        "fecha": ["FECHA_HECH", "FECHA DEL DELITO", "FECHA"],
        "hora": ["HORA_HECH", "HORA DEL DELITO", "HORA"],
        "direccion": ["DIREC_HECH", "DIRECCION DONDE OCURRIO EL DELITO", "DIRECCION"],
        "descripcion": ["DESC_CAUS", "DESCRIPCION", "FILIACION", "DATOS_FILIATORIOS"],
        "nro_sumario": ["ID_N_SRIO", "NRO_SUMAR", "SUMARIO"],
    },
    "aprehendidos": {
        "nombre": ["AP_NOM_CAU", "APELLIDO Y NOMBRE DEL CAUSANTE", "CAUSANTE", "NOMBRE"],
        "edad": ["EDAD_CAUSA", "EDAD DEL CAUSANTE", "EDAD"],
        "sexo": ["SEXO_CAUS", "SEXO DEL CAUSANTE", "SEXO"],
        "delito": ["DELITO", "DELITO COMETIDO", "CAUSA"],
        "fecha_aprehension": ["FECHA_HECH", "FECHA DEL DELITO", "FECHA", "FEC_APREH"],
        "situacion": ["SITUA_CAUS", "SITUACION DEL CAUSANTE", "SITUACION"],
        "direccion": ["DIREC_CAUS", "DIRECCION DEL CAUSANTE", "DIRECCION", "DOMICILIO"],
        "descripcion": ["DESC_CAUS", "DESCRIPCION_CAUSANTE"],
    },
    "jurisdiccion": {
        "nombre": ["JURIS_HECH", "JURISDICCION DONDE TUVO LUGAR EL DELITO", "JURISDICCION", "NOMBRE"],
        "dependencia": ["DPCIA_INT", "DEPENDENCIA INTERVINIENTE", "DEPENDENCIA"],
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
    # Robos agravados - tonos rojos
    "ROBO AGRAVADO ASALTANTE": "#FF0000",
    "ROBO AGRAVADO ASALTANTE EN BANDA": "#CC0000",
    "ROBO AGRAVADO DE MOTOVEHICULO": "#FF3333",
    "ROBO AGRAVADO PIRAÑA DE MOTOVEHICULO": "#FF6666",
    "ROBO AGRAVADO DE AUTOMOTOR": "#990000",
    "ROBO AGRAVADO ENTRADERA": "#FF4444",
    "ROBO AGRAVADO ARIETE": "#CC3333",
    # Robos simples - tonos verdes/amarillos
    "ROBO PIRAÑA DE MOTOVEHICULOS": "#00FF00",
    "ROBO PIRAÑA": "#33CC33",
    "ROBO ARREBATO": "#FFFF00",
    "ROBO CLAVERO DE AUTOS": "#66CC66",
    "ROBO DE MOTOVEHICULOS": "#009900",
    "ROBO DE AUTOMOTOR": "#006600",
    "ROBO ESCRUCHE": "#00CC00",
    "ROBO BOQUETERO": "#339933",
    "ROBO ROMPE VIDRIO": "#333333",
    "ROBO OPORTUNISTA": "#000000",
    # Hurtos - tonos azules
    "HURTO PUNGA": "#0000FF",
    "HURTO MECHERA": "#CCCC00",
    "HURTO OPORTUNISTA": "#333333",
    "HURTO DE MOTOVEHICULO": "#CC0000",
    "HURTO DE AUTOMOTOR": "#666666",
    "HURTO INHIBIDOR DE ALARMAS": "#444444",
    "HURTO ESCALAMIENTO": "#FF8800",
    "HURTO VIUDA NEGRA": "#111111",
    # Estafas
    "ESTAFA CUENTO DEL TIO": "#0066FF",
    "TENTATIVA DE ESTAFA CUENTO DEL TIO": "#3399FF",
}


# ═══════════════════════════════════════════════════════════════════════════════
# MODUS OPERANDI
# ═══════════════════════════════════════════════════════════════════════════════

MODUS_OPERANDI = [
    "ASALTANTE",
    "ASALTANTE EN BANDA",
    "PIRAÑA",
    "ARREBATO",
    "ESCRUCHE",
    "BOQUETERO",
    "ROMPE VIDRIO",
    "ENTRADERA",
    "ARIETE",
    "CLAVERO",
    "INHIBIDOR DE ALARMAS",
    "ESCALAMIENTO",
    "VIUDA NEGRA",
    "PUNGA",
    "MECHERA",
    "OPORTUNISTA",
    "CUENTO DEL TIO",
]


# ═══════════════════════════════════════════════════════════════════════════════
# RESOLUCIÓN DE HECHOS
# ═══════════════════════════════════════════════════════════════════════════════

RESOLUCION_HECHOS = {
    "06-DETENCION_CIVIL": "Detención Civil",
    "05-IDENTIFICADO": "Identificado",
    "04-MENCIONADO": "Mencionado",
    "03-APREHENDIDO": "Aprehendido",
    "02-APREHENDIDO": "Aprehendido",
    "01-SIN_RESOLVER": "Sin Resolver",
}

SITUACION_CAUSANTE = {
    "02-APREHENDIDO": "Aprehendido",
    "03-IDENTIFICADO": "Identificado",
    "04-MENCIONADO": "Mencionado",
    "01-PROFUGO": "Prófugo",
}


# ═══════════════════════════════════════════════════════════════════════════════
# RUTA SHAPEFILE POR DEFECTO
# ═══════════════════════════════════════════════════════════════════════════════

DEFAULT_SHAPEFILE_PATH = r"\\analisis-3\Analisis-3\MAPA DEL DELITO\MAPAS DEL DELITO POR JURISDICCIONES\CRIA AMAICHA DEL VALLE-URO\MAPA DELICTUAL CRIA  AMAICHA DEL VALLE-URO\MAPA DELICTUAL CRIA AMAICHA DEL VALLE-URO.shp"
DEFAULT_JURISDICCION = "URO_COMISARIA_AMAICHA_DEL_VALLE"
DEFAULT_DEPENDENCIA = "URO_COMISARIA_AMAICHA_DEL_VALLE"
