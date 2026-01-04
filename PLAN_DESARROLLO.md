# S.I.D.I.C - Sistema de Información Delictual e Inteligencia Criminal

## 🎯 Plan de Desarrollo v1.0

---

## 1. DESCRIPCIÓN GENERAL

**Aplicación de escritorio** para Windows que procesa **5 archivos Shapefile** de QGIS 2.14.14 (Essen) y genera informes delictuales automatizados con:

- Cuadros estadísticos
- Gráficos de barras
- Cuadros de referencia para mapas
- Comparativos entre períodos
- Exportación a **Excel** y **Word/PDF**

**Estilo visual:** Policial ultramoderno (oscuro, colores de alerta, tipografía técnica).

---

## 2. ARQUITECTURA TÉCNICA

### 2.1 Stack Tecnológico Propuesto

| Componente            | Tecnología                 | Justificación                            |
| --------------------- | -------------------------- | ---------------------------------------- |
| **Lenguaje**          | Python 3.11+               | Librerías GIS maduras, rápido desarrollo |
| **GUI**               | PyQt6 / PySide6            | Moderno, personalizable, multiplataforma |
| **Lectura Shapefile** | `geopandas` + `pyshp`      | Soporte completo para .shp/.dbf/.shx     |
| **Gráficos**          | `matplotlib` + `seaborn`   | Estilizables, exportables a imagen       |
| **Excel**             | `openpyxl` / `xlsxwriter`  | Tablas + gráficos embebidos              |
| **Word/PDF**          | `python-docx` + `docx2pdf` | Plantillas personalizables               |
| **Empaquetado**       | `PyInstaller`              | Ejecutable .exe sin Python instalado     |

### 2.2 Estructura del Proyecto

```
S.I.D.I.C/
├── src/
│   ├── main.py                    # Punto de entrada
│   ├── ui/
│   │   ├── main_window.py         # Ventana principal
│   │   ├── config_dialog.py       # Configuración de campos
│   │   ├── period_selector.py     # Selector de períodos
│   │   ├── preview_panel.py       # Vista previa de reportes
│   │   └── styles/
│   │       └── police_dark.qss    # Estilo policial ultramoderno
│   ├── core/
│   │   ├── shapefile_reader.py    # Lectura y validación de shapes
│   │   ├── data_processor.py      # Procesamiento y agregación
│   │   ├── period_comparator.py   # Comparación entre períodos
│   │   └── field_mapper.py        # Mapeo configurable de campos
│   ├── reports/
│   │   ├── table_generator.py     # Generador de cuadros
│   │   ├── chart_generator.py     # Generador de gráficos
│   │   ├── excel_exporter.py      # Exportación Excel
│   │   ├── word_exporter.py       # Exportación Word
│   │   └── pdf_exporter.py        # Conversión a PDF
│   ├── models/
│   │   ├── crime_record.py        # Modelo de hecho delictual
│   │   ├── mentioned_person.py    # Modelo de "mencionados"
│   │   └── apprehended.py         # Modelo de aprehendidos
│   └── utils/
│       ├── date_utils.py          # Utilidades de fecha/hora
│       ├── geo_utils.py           # Utilidades geográficas
│       └── constants.py           # Constantes y configuración
├── assets/
│   ├── icons/                     # Iconos de la app
│   ├── symbols/                   # Símbolos para cuadro de referencia
│   └── templates/
│       ├── informe_template.docx  # Plantilla Word
│       └── styles.xlsx            # Estilos Excel
├── config/
│   └── field_mappings.json        # Mapeo de campos configurable
├── tests/
├── requirements.txt
├── build.spec                     # Configuración PyInstaller
└── README.md
```

---

## 3. ENTRADA DE DATOS (5 SHAPEFILES)

### 3.1 Capas Esperadas

| #   | Capa                   | Descripción                     | Campos Clave                                 |
| --- | ---------------------- | ------------------------------- | -------------------------------------------- |
| 1   | **Hechos Delictuales** | Puntos de ocurrencia de delitos | fecha, hora, delito, ámbito, movilidad, arma |
| 2   | **Robos Agravados**    | Subset de robos con arma        | delito, arma_medio, fecha, hora              |
| 3   | **Mencionados**        | "Un tal..." posibles autores    | alias, delito, fecha, hora, direccion, datos |
| 4   | **Aprehendidos**       | Personas detenidas              | clasificacion, edad, sexo, delito, fecha     |
| 5   | **Jurisdicción**       | Límite comisaría (polígono)     | nombre, codigo                               |

### 3.2 Mapeo Configurable de Campos

La app permitirá configurar qué campo del shapefile corresponde a cada dato requerido:

```json
{
  "hechos": {
    "fecha": ["FECHA", "FEC_HECHO", "fecha_hecho"],
    "hora": ["HORA", "HOR_HECHO", "hora_hecho"],
    "delito": ["DELITO", "TIPO_DELITO", "modalidad"],
    "ambito": ["AMBITO", "AMB_OCURR", "lugar"],
    "movilidad": ["MOVILIDAD", "MEDIO_MOV", "transporte"],
    "arma": ["ARMA", "MEDIO_ARMA", "arma_utilizada"],
    "esclarecido": ["ESCLAREC", "ESTADO", "resuelto"]
  }
}
```

### 3.3 Validación al Cargar

- ✅ Verificar archivos asociados (.shp, .dbf, .shx, .prj)
- ✅ Detectar campos faltantes
- ✅ Validar formato de fecha/hora
- ✅ Alertar registros sin geometría
- ✅ Verificar CRS/proyección

---

## 4. SALIDAS (CUADROS Y GRÁFICOS)

### 4.1 Cuadro de Referencia para Mapas

| Símbolo                       | Delito                             | Cantidad |
| ----------------------------- | ---------------------------------- | -------- |
| ▷                             | Robo Agravado de Motovehículo      | 1        |
| △                             | Robo Arrebato                      | 1        |
| ◢                             | Robo Clavero de Autos              | 1        |
| ...                           | ...                                | ...      |
| **SUBTOTAL - ROBOS**          |                                    | **8**    |
| ●                             | Hurto Oportunista                  | 4        |
| **SUBTOTAL - HURTOS**         |                                    | **4**    |
| **TOTAL DELITOS REGISTRADOS** |                                    | **12**   |
| ○                             | Hechos Esclarecidos "PARCIALMENTE" | 1        |
| Ⓟ                             | Comisaría Jurisdiccional           |          |

**Símbolos configurables** por tipo de delito (colores: amarillo, rojo, azul, verde, etc.).

---

### 4.2 Cuadros Estadísticos (1 o N períodos)

Para cada período seleccionado, la app genera:

#### A) DELITOS CON MODALIDADES

| DELITOS CON MODALIDADES | Período 1 | %        | Período 2 | %        | Variación |
| ----------------------- | --------- | -------- | --------- | -------- | --------- |
| HURTO_OPORTUNISTA       | 4         | 33,33%   | 6         | 40%      | +50%      |
| ROBO_OPORTUNISTA        | 3         | 25,00%   | 2         | 13,33%   | -33,33%   |
| ...                     |           |          |           |          |           |
| **TOTAL DE HECHOS**     | **12**    | **100%** | **15**    | **100%** | **+25%**  |

📊 **Gráfico de barras:** Sí (simple o comparativo)

---

#### B) DÍAS DE LA SEMANA

| DÍAS DE LA SEMANA | Cantidad | Porcentaje |
| ----------------- | -------- | ---------- |
| LUNES             | 1        | 8,33%      |
| MARTES            | 2        | 16,67%     |
| MIÉRCOLES         | 2        | 16,67%     |
| JUEVES            | 3        | 25,00%     |
| VIERNES           | 1        | 8,33%      |
| SÁBADO            | 1        | 8,33%      |
| DOMINGO           | 2        | 16,67%     |
| **TOTAL**         | **12**   | **100%**   |

📊 **Gráfico de barras:** Sí

---

#### C) FRANJA HORARIA

| FRANJA HORARIA           | Cantidad | Porcentaje |
| ------------------------ | -------- | ---------- |
| MADRUGADA (00:00-04:59)  | 2        | 16,67%     |
| MAÑANA (05:00-08:59)     | 2        | 16,67%     |
| VESPERTINA (09:00-12:59) | 1        | 8,33%      |
| SIESTA (13:00-16:59)     | 1        | 8,33%      |
| TARDE (17:00-19:59)      | 4        | 33,33%     |
| NOCHE (20:00-23:59)      | 2        | 16,67%     |
| **TOTAL**                | **12**   | **100%**   |

📊 **Gráfico de barras:** Sí

---

#### D) MEDIOS DE MOVILIDAD UTILIZADOS

| MOVILIDAD   | Cantidad | Porcentaje |
| ----------- | -------- | ---------- |
| A_PIE       | 9        | 75,00%     |
| MOTOCICLETA | 2        | 16,67%     |
| #NO_CONSTA  | 1        | 8,33%      |
| **TOTAL**   | **12**   | **100%**   |

📊 **Gráfico de barras:** Sí

---

#### E) MEDIOS O ARMAS EN ROBOS AGRAVADOS

_(Solo para delitos tipo ROBO*AGRAVADO*_)\*

| ARMA/MEDIO    | Cantidad | Porcentaje |
| ------------- | -------- | ---------- |
| ARMA_DE_FUEGO | 1        | 50,00%     |
| ARMA_BLANCA   | 1        | 50,00%     |
| **TOTAL**     | **2**    | **100%**   |

📊 **Gráfico de barras:** Sí

---

#### F) ÁMBITO DE OCURRENCIA DELICTUAL

| ÁMBITO      | Cantidad | Porcentaje |
| ----------- | -------- | ---------- |
| VIA_PUBLICA | 6        | 50,00%     |
| VIVIENDA    | 6        | 50,00%     |
| COMERCIO    | 0        | 0,00%      |
| **TOTAL**   | **12**   | **100%**   |

📊 **Gráfico de barras:** Sí

---

### 4.3 Cuadros Matriciales (SIN gráfico de barras simple)

#### G) DELITOS × DÍAS DE LA SEMANA

| DELITO            | LUN | MAR | MIÉ | JUE | VIE | SÁB | DOM | TOTAL  |
| ----------------- | --- | --- | --- | --- | --- | --- | --- | ------ |
| HURTO_OPORTUNISTA | 0   | 1   | 0   | 3   | 0   | 0   | 0   | 4      |
| ROBO_OPORTUNISTA  | 0   | 0   | 2   | 0   | 0   | 0   | 1   | 3      |
| ...               |     |     |     |     |     |     |     |        |
| **TOTAL POR DÍA** | 1   | 2   | 2   | 3   | 1   | 1   | 2   | **12** |

📊 **Gráfico:** Barras agrupadas por delito (coloreadas)

---

#### H) DELITOS × FRANJA HORARIA

| DELITO               | MADRUG | MAÑANA | VESP | SIESTA | TARDE | NOCHE | TOTAL  |
| -------------------- | ------ | ------ | ---- | ------ | ----- | ----- | ------ |
| HURTO_OPORTUNISTA    | 1      | 0      | 0    | 0      | 3     | 0     | 4      |
| ROBO_OPORTUNISTA     | 0      | 2      | 0    | 0      | 0     | 1     | 3      |
| ...                  |        |        |      |        |       |       |        |
| **TOTAL POR FRANJA** | 2      | 2      | 1    | 1      | 4     | 2     | **12** |

📊 **Gráfico:** Barras agrupadas por delito (coloreadas)

---

### 4.4 Cuadro de Mencionados ("Un Tal...")

**MENCIONADOS COMO POSIBLES AUTORES MATERIALES:**

| #   | Alias                        | Delito            | Dirección Hecho         | Fecha      | Hora  | Datos Filiatorios           |
| --- | ---------------------------- | ----------------- | ----------------------- | ---------- | ----- | --------------------------- |
| 1   | "MARIO MENA"                 | HURTO OPORTUNISTA | MONSEÑOR Nº 83          | 02/12/2025 | 17:30 | Domiciliado en la zona      |
| 2   | "JUAN PABLO CAZORLA"         | ROBO OPORTUNISTA  | MONSEÑOR Nº 83          | 03/12/2025 | 20:20 | -                           |
| 3   | "RODRIGO" y "CHINO CAMPBELL" | HURTO OPORTUNISTA | VICTORIA OCAMPO Nº 1283 | 04/12/2025 | 03:00 | Sin remera, bermuda de jean |
| ... |                              |                   |                         |            |       |                             |

**Total Mencionados:** X personas

---

### 4.5 Cuadro de Aprehendidos

| #   | Nombre/Alias | Clasificación          | Delito | Fecha      | Edad | Sexo |
| --- | ------------ | ---------------------- | ------ | ---------- | ---- | ---- |
| 1   | ...          | MAYOR CON ANTECEDENTES | ROBO   | 05/12/2025 | 28   | M    |
| 2   | ...          | MENOR PRIMERIZO        | HURTO  | 08/12/2025 | 16   | M    |

**Resumen por Clasificación:**
| Clasificación | Cantidad |
|---------------|----------|
| MAYOR CON ANTECEDENTES | 2 |
| MAYOR PRIMERIZO | 1 |
| MENOR CON ANTECEDENTES | 0 |
| MENOR PRIMERIZO | 1 |
| **TOTAL APREHENDIDOS** | **4** |

---

### 4.6 Cuadros Adicionales Sugeridos (Valor Agregado)

#### I) MAPA DE CALOR TEMPORAL

Matriz hora × día para identificar patrones:

```
        LUN  MAR  MIÉ  JUE  VIE  SÁB  DOM
00-04    0    1    0    0    1    0    0
05-08    0    0    0    1    0    0    0
...
```

#### J) TOP 5 ZONAS/CALLES CON MÁS INCIDENCIA

| Zona/Calle       | Cantidad | % del Total |
| ---------------- | -------- | ----------- |
| AV. CONSTITUCIÓN | 3        | 25%         |
| MONSEÑOR         | 2        | 16,67%      |
| ...              |          |             |

#### K) ÍNDICE DE ESCLARECIMIENTO

| Estado                   | Cantidad | %      |
| ------------------------ | -------- | ------ |
| ESCLARECIDO TOTALMENTE   | 0        | 0%     |
| ESCLARECIDO PARCIALMENTE | 1        | 8,33%  |
| NO ESCLARECIDO           | 11       | 91,67% |

#### L) TENDENCIA SEMANAL (si hay datos suficientes)

Gráfico de línea mostrando evolución semana a semana.

---

## 5. COMPARACIÓN ENTRE PERÍODOS

### 5.1 Reglas de Cálculo

```
Variación Absoluta = Período_2 - Período_1
Variación % = ((Período_2 - Período_1) / Período_1) * 100

Si Período_1 = 0:
  - Si Período_2 > 0 → "+∞%" o "NUEVO"
  - Si Período_2 = 0 → "0%" o "SIN CAMBIO"
```

### 5.2 Formato Visual de Variación

| Variación         | Color          | Icono |
| ----------------- | -------------- | ----- |
| Aumento > 20%     | 🔴 Rojo        | ▲     |
| Aumento 1-20%     | 🟠 Naranja     | ▲     |
| Sin cambio        | ⚪ Gris        | ─     |
| Disminución 1-20% | 🟢 Verde claro | ▼     |
| Disminución > 20% | 🟢 Verde       | ▼     |

### 5.3 Cuadro Comparativo General

| Indicador     | Período A | Período B | Variación | %         |
| ------------- | --------- | --------- | --------- | --------- |
| Total Delitos | 12        | 18        | +6        | +50% 🔴▲  |
| Total Robos   | 8         | 10        | +2        | +25% 🟠▲  |
| Total Hurtos  | 4         | 8         | +4        | +100% 🔴▲ |
| Esclarecidos  | 1         | 3         | +2        | +200% 🟢▲ |
| Aprehendidos  | 2         | 5         | +3        | +150%     |
| Mencionados   | 5         | 4         | -1        | -20% 🟢▼  |

---

## 6. INTERFAZ DE USUARIO (GUI)

### 6.1 Pantalla Principal

```
┌─────────────────────────────────────────────────────────────────────────┐
│  S.I.D.I.C  │  Sistema de Información Delictual e Inteligencia Criminal │
├─────────────────────────────────────────────────────────────────────────┤
│ ┌─────────────────────┐  ┌─────────────────────────────────────────────┐│
│ │  📁 CARGAR SHAPES   │  │              VISTA PREVIA                   ││
│ │                     │  │  ┌─────────────────────────────────────────┐││
│ │  ☑ Hechos.shp      │  │  │                                         │││
│ │  ☑ Robos_Agrav.shp │  │  │    [Cuadros / Gráficos / Mapas]         │││
│ │  ☑ Mencionados.shp │  │  │                                         │││
│ │  ☑ Aprehendidos.shp│  │  │                                         │││
│ │  ☑ Jurisdiccion.shp│  │  └─────────────────────────────────────────┘││
│ └─────────────────────┘  └─────────────────────────────────────────────┘│
│ ┌─────────────────────┐  ┌─────────────────────────────────────────────┐│
│ │  📅 PERÍODOS        │  │              OPCIONES                       ││
│ │                     │  │  ☑ Cuadro de Referencia                    ││
│ │  Período 1:         │  │  ☑ Delitos con Modalidades                 ││
│ │  [01/12/2025] →     │  │  ☑ Días de la Semana                       ││
│ │  [22/12/2025]       │  │  ☑ Franja Horaria                          ││
│ │                     │  │  ☑ Movilidad                               ││
│ │  ☐ Agregar período  │  │  ☑ Armas (Robos Agravados)                 ││
│ │     comparativo     │  │  ☑ Ámbito de Ocurrencia                    ││
│ │                     │  │  ☑ Matriz Delito×Día                       ││
│ │  Período 2:         │  │  ☑ Matriz Delito×Hora                      ││
│ │  [01/11/2025] →     │  │  ☑ Mencionados                             ││
│ │  [30/11/2025]       │  │  ☑ Aprehendidos                            ││
│ └─────────────────────┘  │  ☑ Cuadro Comparativo                      ││
│                          └─────────────────────────────────────────────┘│
│ ┌───────────────────────────────────────────────────────────────────────┤
│ │  [🔄 PROCESAR]   [📊 EXCEL]   [📄 WORD]   [📕 PDF]   [⚙️ CONFIG]     │
│ └───────────────────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────────────────┘
```

### 6.2 Estilo Visual "Policial Ultramoderno"

```css
/* police_dark.qss */
QMainWindow {
    background-color: #0a0a12;
    color: #e0e0e0;
}

QLabel#title {
    font-family: "Orbitron", "Segoe UI";
    font-size: 24px;
    font-weight: bold;
    color: #00d4ff;
    text-shadow: 0 0 10px #00d4ff;
}

QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
        stop:0 #1a1a2e, stop:1 #16213e);
    border: 1px solid #00d4ff;
    border-radius: 4px;
    color: #ffffff;
    padding: 10px 20px;
    font-weight: bold;
}

QPushButton:hover {
    background: #00d4ff;
    color: #0a0a12;
}

QTableWidget {
    background-color: #0f0f1a;
    gridline-color: #2a2a4a;
    color: #ffffff;
}

QTableWidget::item:selected {
    background-color: #ff3b3b;
}

/* Colores de alerta */
.danger { color: #ff3b3b; }
.warning { color: #ffaa00; }
.success { color: #00ff88; }
.info { color: #00d4ff; }
```

**Paleta de Colores:**

- **Fondo principal:** #0a0a12 (negro azulado)
- **Acentos:** #00d4ff (cyan), #ff3b3b (rojo alerta)
- **Éxito:** #00ff88 (verde neón)
- **Advertencia:** #ffaa00 (ámbar)
- **Texto:** #e0e0e0 (gris claro)

**Tipografía:**

- Títulos: "Orbitron" o "Rajdhani" (fuentes tech/futuristas)
- Cuerpo: "Segoe UI", "Roboto"
- Datos: "JetBrains Mono" (monoespaciada)

---

## 7. EXPORTACIÓN

### 7.1 Excel (.xlsx)

**Estructura del archivo:**

- Hoja 1: **Resumen** (totales, período, jurisdicción)
- Hoja 2: **Cuadro de Referencia**
- Hoja 3: **Delitos con Modalidades** + gráfico
- Hoja 4: **Días de la Semana** + gráfico
- Hoja 5: **Franja Horaria** + gráfico
- Hoja 6: **Movilidad** + gráfico
- Hoja 7: **Armas Robos Agravados** + gráfico
- Hoja 8: **Ámbito de Ocurrencia** + gráfico
- Hoja 9: **Matriz Delito×Día** + gráfico
- Hoja 10: **Matriz Delito×Hora** + gráfico
- Hoja 11: **Mencionados**
- Hoja 12: **Aprehendidos**
- Hoja 13: **Comparativo** (si hay múltiples períodos)

**Estilos Excel:**

- Header: fondo rojo (#FF0000), texto blanco, bold
- Totales: fondo amarillo (#FFFF00), bold
- Subtotales: fondo azul (#0000FF), texto blanco
- Datos: fondo alternado (blanco/gris claro)

### 7.2 Word (.docx)

**Plantilla con:**

- Encabezado institucional (logo, jurisdicción)
- Título del informe
- Período analizado
- Cada cuadro con su gráfico debajo
- Pie de página con fecha de generación

### 7.3 PDF

- Generado desde Word (python-docx → docx2pdf)
- O directamente con ReportLab/WeasyPrint

---

## 8. FLUJO DE TRABAJO

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   CARGAR    │────▶│   MAPEAR    │────▶│  VALIDAR    │
│  SHAPEFILES │     │   CAMPOS    │     │   DATOS     │
└─────────────┘     └─────────────┘     └─────────────┘
                                               │
                                               ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  EXPORTAR   │◀────│  GENERAR    │◀────│ SELECCIONAR │
│ EXCEL/WORD  │     │  REPORTES   │     │  PERÍODOS   │
└─────────────┘     └─────────────┘     └─────────────┘
```

---

## 9. FASES DE DESARROLLO

### Fase 1: Core (2-3 semanas)

- [ ] Lectura de shapefiles con geopandas
- [ ] Mapeo configurable de campos
- [ ] Modelo de datos interno
- [ ] Procesador de períodos
- [ ] Generador de tablas básicas

### Fase 2: Reportes (2 semanas)

- [ ] Todos los cuadros estadísticos
- [ ] Cuadros matriciales
- [ ] Cuadro de mencionados
- [ ] Cuadro de aprehendidos
- [ ] Comparación entre períodos

### Fase 3: Gráficos (1 semana)

- [ ] Gráficos de barras simples
- [ ] Gráficos de barras agrupadas
- [ ] Gráficos comparativos
- [ ] Estilizado policial

### Fase 4: GUI (2 semanas)

- [ ] Ventana principal
- [ ] Selector de archivos
- [ ] Selector de períodos
- [ ] Vista previa
- [ ] Estilo policial ultramoderno

### Fase 5: Exportación (1 semana)

- [ ] Exportación Excel completa
- [ ] Exportación Word con plantilla
- [ ] Generación PDF

### Fase 6: Empaquetado (3-5 días)

- [ ] Empaquetado con PyInstaller
- [ ] Instalador (opcional: Inno Setup)
- [ ] Documentación de usuario

**Tiempo total estimado: 8-10 semanas**

---

## 10. REQUISITOS DEL SISTEMA

### Para desarrollo:

- Python 3.11+
- Windows 10/11
- 8 GB RAM mínimo
- QGIS 2.14.14 (para generar shapes de prueba)

### Para usuario final:

- Windows 10/11
- 4 GB RAM mínimo
- 500 MB espacio en disco
- **No requiere Python instalado** (ejecutable standalone)

---

## 11. DEPENDENCIAS (requirements.txt)

```
geopandas>=0.14.0
pandas>=2.0.0
numpy>=1.24.0
matplotlib>=3.7.0
seaborn>=0.12.0
PyQt6>=6.5.0
openpyxl>=3.1.0
XlsxWriter>=3.1.0
python-docx>=0.8.11
docx2pdf>=0.1.8
pyshp>=2.3.0
shapely>=2.0.0
Pillow>=10.0.0
pyinstaller>=5.13.0
```

---

## 12. PRÓXIMOS PASOS

1. **Confirmar** que este plan cubre todos tus requerimientos
2. **Obtener** los 5 shapefiles reales para mapear campos exactos
3. **Definir** logotipo/escudo para el encabezado
4. **Comenzar** desarrollo por Fase 1 (Core)

---

_Documento generado: 04/01/2026_
_Versión: 1.0_
_Proyecto: S.I.D.I.C_
