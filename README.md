# S.I.D.I.C

## Sistema de Información Delictual e Inteligencia Criminal

<p align="center">
  <strong>🔒 Aplicación de escritorio para procesamiento de datos delictuales y generación de informes estadísticos profesionales</strong>
</p>

---

## 📋 Descripción

S.I.D.I.C es una aplicación de escritorio desarrollada en Python que procesa datos geográficos delictuales provenientes de QGIS 2.14.14 (shapefiles) y genera informes estadísticos completos en formatos Excel, Word y PDF.

### Características principales:

- 🗺️ **Procesamiento de Shapefiles**: Lee y procesa hasta 5 archivos shapefile de QGIS
- 📊 **Tablas Estadísticas**: Genera todas las tablas requeridas para informes policiales
- 📈 **Gráficos de Barras**: Visualizaciones profesionales con estilo policial
- 📅 **Análisis por Períodos**: Soporte para reportes simples y comparativos
- 📁 **Exportación Múltiple**: Excel (.xlsx), Word (.docx) y PDF
- 🎨 **Interfaz Ultramoderna**: Estilo policial con tema oscuro y acentos neón

---

## 🚀 Instalación

### Requisitos previos

- **Windows 10/11**
- **Python 3.11+** (descargar de [python.org](https://www.python.org/downloads/))
- **Microsoft Word** (opcional, para conversión a PDF)

### Instalación automática

1. Descargue o clone este repositorio
2. Ejecute `install.bat`
3. ¡Listo!

### Instalación manual

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/sidic.git
cd sidic

# Crear entorno virtual
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

---

## 💻 Uso

### Interfaz Gráfica

```bash
# Usando el script
run_sidic.bat

# O manualmente
venv\Scripts\activate
cd src
python main.py
```

### Línea de Comandos

```bash
python src/main.py --cli \
    --hechos "C:/datos/hechos.shp" \
    --inicio 2024-01-01 \
    --fin 2024-01-31 \
    --salida "C:/reportes/informe.xlsx" \
    --formato excel
```

---

## 📁 Estructura del Proyecto

```
S.I.D.I.C/
├── src/
│   ├── main.py              # Punto de entrada
│   ├── core/                # Lógica principal
│   │   ├── data_processor.py
│   │   ├── field_mapper.py
│   │   ├── period_comparator.py
│   │   └── shapefile_reader.py
│   ├── models/              # Modelos de datos
│   │   ├── apprehended.py
│   │   ├── crime_record.py
│   │   ├── mentioned_person.py
│   │   └── report_data.py
│   ├── reports/             # Generación de reportes
│   │   ├── chart_generator.py
│   │   ├── excel_exporter.py
│   │   ├── pdf_exporter.py
│   │   ├── table_generator.py
│   │   └── word_exporter.py
│   ├── ui/                  # Interfaz gráfica
│   │   ├── main_window.py
│   │   ├── widgets/
│   │   └── styles/
│   └── utils/               # Utilidades
│       ├── constants.py
│       ├── date_utils.py
│       └── geo_utils.py
├── config/
│   └── field_mappings.json  # Configuración de campos
├── requirements.txt
├── install.bat
├── run_sidic.bat
└── README.md
```

---

## 📊 Reportes Generados

### Tablas incluidas:

| Tabla                   | Descripción                                    |
| ----------------------- | ---------------------------------------------- |
| Cuadro de Referencia    | Símbolo, delito, cantidad (ROBOS/HURTOS/Total) |
| Delitos con Modalidades | Tipo de delito y modalidad con cantidades      |
| Días de la Semana       | Distribución por día de la semana              |
| Franja Horaria          | Distribución por franjas (6 definidas)         |
| Movilidad               | Medios de movilidad utilizados                 |
| Armas                   | Armas/medios en robos agravados                |
| Ámbito de Ocurrencia    | Lugar donde ocurrieron los hechos              |
| Matriz Delito × Día     | Tabla cruzada delitos por días                 |
| Matriz Delito × Franja  | Tabla cruzada delitos por franjas              |
| Mencionados             | Lista de "Un tal..." con datos                 |
| Aprehendidos            | Personas detenidas                             |
| Esclarecimiento         | Índice de esclarecimiento                      |

### Franjas Horarias:

| Franja     | Horario       |
| ---------- | ------------- |
| MADRUGADA  | 00:00 - 04:59 |
| MAÑANA     | 05:00 - 08:59 |
| VESPERTINA | 09:00 - 12:59 |
| SIESTA     | 13:00 - 16:59 |
| TARDE      | 17:00 - 19:59 |
| NOCHE      | 20:00 - 23:59 |

---

## ⚙️ Configuración

El archivo `config/field_mappings.json` permite configurar el mapeo de campos de sus shapefiles.

Ejemplo:

```json
{
    "mappings": {
        "hechos": {
            "fecha": {
                "source_fields": ["FECHA", "FEC_HECHO"],
                "type": "date",
                "format": "%d/%m/%Y"
            }
        }
    }
}
```

---

## 🔧 Generar Ejecutable

Para crear un archivo .exe independiente:

```bash
pip install pyinstaller
pyinstaller --name "SIDIC" --onefile --windowed src/main.py
```

El ejecutable se generará en `dist/SIDIC.exe`

---

## 📜 Licencia

Este proyecto es software propietario para uso exclusivo de las fuerzas de seguridad autorizadas.

---

## 👤 Autor

Desarrollado para la gestión de inteligencia criminal.

---

<p align="center">
  <strong>S.I.D.I.C v1.0.0</strong><br>
  Sistema de Información Delictual e Inteligencia Criminal
</p>
# S.I.D.I.C
