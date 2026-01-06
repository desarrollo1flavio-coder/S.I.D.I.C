"""
Generador de datos de ejemplo para demostración del sistema S.I.D.I.C.

Proporciona datos realistas de prueba para probar la generación de informes
sin necesidad de cargar archivos shapefile reales.
"""
from datetime import date, time, timedelta
from random import randint, choice, seed as random_seed
from typing import List, Optional

from ..models.crime_record import CrimeRecord
from ..models.mentioned_person import MentionedPerson
from ..models.apprehended import Apprehended
from ..models.report_data import PeriodData, ReportData


# ═══════════════════════════════════════════════════════════════════════════════
# DATOS BASE PARA GENERACIÓN
# ═══════════════════════════════════════════════════════════════════════════════

DELITOS_DEMO = [
    "ROBO AGRAVADO ASALTANTE",
    "ROBO AGRAVADO ASALTANTE EN BANDA",
    "ROBO ARREBATO",
    "ROBO ESCRUCHE",
    "ROBO OPORTUNISTA",
    "HURTO PUNGA",
    "HURTO OPORTUNISTA",
    "HURTO DESCUIDISTA",
    "TENTATIVA DE ROBO ASALTANTE",
    "TENTATIVA DE ROBO ESCRUCHE",
    "ESTAFA CUENTO DEL TIO",
    "ESTAFA ELECTRONICA",
]

MODUS_OPERANDI_DEMO = [
    "ASALTANTE",
    "PUNGA",
    "ARREBATADOR",
    "DESCUIDISTA",
    "ESCRUCHE",
    "OPORTUNISTA",
    "BOQUETERO",
]

MOVILIDADES_DEMO = [
    "MOTOCICLETA",
    "{A_PIE}",
    "AUTOMOVIL",
    "BICICLETA",
    "{SIN_DATOS}",
]

ARMAS_DEMO = [
    "{ARMA_BLANCA}",
    "{ARMA_FUEGO}",
    "{INTIMIDACION}",
    "{SIN_ARMAS}",
    "{SIN_DATOS}",
]

AMBITOS_DEMO = [
    "VIA_PUBLICA",
    "COMERCIO",
    "DOMICILIO",
    "TRANSPORTE_PUBLICO",
    "ESTACIONAMIENTO",
]

ESCLARECIDOS_DEMO = [
    "01-SIN_RESOLVER",
    "01-SIN_RESOLVER",
    "01-SIN_RESOLVER",  # Mayor probabilidad de no resuelto
    "03-APREHENDIDO",
    "05-IDENTIFICADO",
    "02-EN_INVESTIGACION",
]

JURISDICCIONES_DEMO = [
    "DEMO - Jurisdicción Norte",
    "DEMO - Jurisdicción Sur",
    "DEMO - Jurisdicción Centro",
    "DEMO - Jurisdicción Este",
    "DEMO - Jurisdicción Oeste",
]

CALLES_DEMO = [
    "Av. San Martín",
    "Av. Belgrano",
    "Calle 24 de Septiembre",
    "Calle Rivadavia",
    "Av. Sarmiento",
    "Calle Laprida",
    "Calle Muñecas",
    "Av. Mate de Luna",
    "Calle Junín",
    "Av. Roca",
    "Calle Mendoza",
    "Calle Córdoba",
]

ALIAS_DEMO = [
    "EL FLACO",
    "EL GORDO",
    "PICHI",
    "CABEZON",
    "EL NEGRO",
    "TITO",
    "CHUECO",
    "PELADO",
    "MONO",
    "CHAPU",
]

NOMBRES_DEMO = [
    "JUAN CARLOS RODRIGUEZ",
    "MIGUEL ANGEL GONZALEZ",
    "ROBERTO CARLOS FERNANDEZ",
    "CARLOS ALBERTO MARTINEZ",
    "JOSE LUIS SANCHEZ",
    "MARIA ELENA GOMEZ",
    "CARLOS RAMON LOPEZ",
    "PEDRO ANTONIO DIAZ",
]

CLASIFICACIONES_DEMO = [
    "MAYOR_PRIMERIZO",
    "MAYOR_CON_ANTECEDENTES",
    "MENOR_PRIMERIZO",
    "MENOR_CON_ANTECEDENTES",
]


# ═══════════════════════════════════════════════════════════════════════════════
# FUNCIONES GENERADORAS
# ═══════════════════════════════════════════════════════════════════════════════

def generate_sample_hechos(
    count: int = 50,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    seed: Optional[int] = None
) -> List[CrimeRecord]:
    """
    Genera hechos delictuales de ejemplo.
    
    Args:
        count: Número de hechos a generar (default: 50)
        start_date: Fecha de inicio del período (default: hace 30 días)
        end_date: Fecha de fin del período (default: hoy)
        seed: Semilla para reproducibilidad
    
    Returns:
        Lista de CrimeRecord con datos demo.
    """
    if seed is not None:
        random_seed(seed)
    
    if start_date is None:
        start_date = date.today() - timedelta(days=30)
    if end_date is None:
        end_date = date.today()
    
    dias_rango = (end_date - start_date).days
    if dias_rango < 1:
        dias_rango = 1
    
    hechos = []
    for i in range(count):
        fecha_hecho = start_date + timedelta(days=randint(0, dias_rango))
        
        hechos.append(CrimeRecord(
            id=f"DEMO-{i+1:04d}",
            nro_sumario=f"{randint(1000, 9999)}-{fecha_hecho.year}",
            fecha=fecha_hecho,
            hora=time(randint(0, 23), randint(0, 59)),
            delito=choice(DELITOS_DEMO),
            modus_operandi=choice(MODUS_OPERANDI_DEMO),
            ambito=choice(AMBITOS_DEMO),
            movilidad=choice(MOVILIDADES_DEMO),
            arma_medio=choice(ARMAS_DEMO),
            esclarecido=choice(ESCLARECIDOS_DEMO),
            direccion=f"{choice(CALLES_DEMO)} {randint(100, 2999)}",
            jurisdiccion=choice(JURISDICCIONES_DEMO),
            dependencia="DEMO - Comisaría de Demostración",
            coordenadas=(-65.2 + randint(-50, 50)/1000, -26.8 + randint(-50, 50)/1000),
            sexo_victima=choice(["MASCULINO", "FEMENINO"]),
            edad_victima=str(randint(18, 70)),
        ))
    
    return hechos


def generate_sample_mencionados(
    count: int = 5,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    seed: Optional[int] = None
) -> List[MentionedPerson]:
    """
    Genera personas mencionadas de ejemplo.
    
    Args:
        count: Número de mencionados a generar (default: 5)
        start_date: Fecha de inicio del período
        end_date: Fecha de fin del período
        seed: Semilla para reproducibilidad
    
    Returns:
        Lista de MentionedPerson con datos demo.
    """
    if seed is not None:
        random_seed(seed)
    
    if start_date is None:
        start_date = date.today() - timedelta(days=30)
    if end_date is None:
        end_date = date.today()
    
    dias_rango = (end_date - start_date).days
    if dias_rango < 1:
        dias_rango = 1
    
    mencionados = []
    alias_usados = []
    
    for i in range(count):
        # Evitar alias repetidos
        alias_disponibles = [a for a in ALIAS_DEMO if a not in alias_usados]
        if not alias_disponibles:
            alias_disponibles = ALIAS_DEMO
        
        alias = choice(alias_disponibles)
        alias_usados.append(alias)
        
        fecha_hecho = start_date + timedelta(days=randint(0, dias_rango))
        
        mencionados.append(MentionedPerson(
            id=f"MENC-DEMO-{i+1:03d}",
            alias=alias,
            datos_filiatorios=f"Aproximadamente {randint(20, 45)} años, contextura {choice(['delgada', 'media', 'robusta'])}",
            delito=choice(DELITOS_DEMO),
            fecha=fecha_hecho,
            hora=time(randint(0, 23), randint(0, 59)),
            direccion_hecho=f"{choice(CALLES_DEMO)} {randint(100, 2999)}",
        ))
    
    return mencionados


def generate_sample_aprehendidos(
    count: int = 8,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    seed: Optional[int] = None
) -> List[Apprehended]:
    """
    Genera personas aprehendidas de ejemplo.
    
    Args:
        count: Número de aprehendidos a generar (default: 8)
        start_date: Fecha de inicio del período
        end_date: Fecha de fin del período
        seed: Semilla para reproducibilidad
    
    Returns:
        Lista de Apprehended con datos demo.
    """
    if seed is not None:
        random_seed(seed)
    
    if start_date is None:
        start_date = date.today() - timedelta(days=30)
    if end_date is None:
        end_date = date.today()
    
    dias_rango = (end_date - start_date).days
    if dias_rango < 1:
        dias_rango = 1
    
    aprehendidos = []
    
    for i in range(count):
        clasificacion = choice(CLASIFICACIONES_DEMO)
        
        # Determinar edad según clasificación
        if "MENOR" in clasificacion:
            edad = randint(14, 17)
        else:
            edad = randint(18, 45)
        
        fecha_hecho = start_date + timedelta(days=randint(0, dias_rango))
        
        aprehendidos.append(Apprehended(
            id=f"APREH-DEMO-{i+1:03d}",
            nombre=choice(NOMBRES_DEMO),
            edad=edad,
            sexo=choice(["M", "M", "M", "F"]),  # Mayor probabilidad masculino
            clasificacion=clasificacion,
            delito=choice(DELITOS_DEMO),
            fecha=fecha_hecho,
        ))
    
    return aprehendidos


def generate_sample_report(
    titulo: str = "INFORME DE DEMOSTRACIÓN",
    num_hechos: int = 50,
    num_mencionados: int = 5,
    num_aprehendidos: int = 8,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    seed: Optional[int] = 42
) -> ReportData:
    """
    Genera un ReportData completo con datos de demostración.
    
    Args:
        titulo: Título del informe
        num_hechos: Número de hechos a generar
        num_mencionados: Número de mencionados a generar
        num_aprehendidos: Número de aprehendidos a generar
        start_date: Fecha de inicio del período
        end_date: Fecha de fin del período
        seed: Semilla para reproducibilidad
    
    Returns:
        ReportData completo con datos demo.
    """
    if start_date is None:
        start_date = date.today() - timedelta(days=30)
    if end_date is None:
        end_date = date.today()
    
    hechos = generate_sample_hechos(num_hechos, start_date, end_date, seed)
    mencionados = generate_sample_mencionados(num_mencionados, start_date, end_date, seed)
    aprehendidos = generate_sample_aprehendidos(num_aprehendidos, start_date, end_date, seed)
    
    period = PeriodData(
        nombre="Período de Demostración",
        fecha_inicio=start_date,
        fecha_fin=end_date,
        hechos=hechos,
        mencionados=mencionados,
        aprehendidos=aprehendidos
    )
    
    report = ReportData(
        titulo=titulo,
        jurisdiccion="DEMO - Jurisdicción de Ejemplo",
        fecha_generacion=date.today()
    )
    report.agregar_periodo(period)
    
    return report
