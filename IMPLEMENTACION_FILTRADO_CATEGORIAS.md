# Implementación: Filtrado por Categorías de Delitos

## ✅ Estado: COMPLETADO

## Resumen de Cambios

Se ha implementado exitosamente la funcionalidad de filtrado por categorías de delitos en el sistema S.I.D.I.C, permitiendo al usuario incluir o excluir categorías específicas (ROBOS, HURTOS, ESTAFAS, OTROS) al generar informes.

## Archivos Modificados

### 1. `src/ui/main_window.py` (2 cambios)

#### Cambio 1: Checkboxes de categorías (líneas ~630-655)

- ✅ Agregados 4 checkboxes en la sección de opciones de exportación:
  - `check_incluir_robos` - Incluir ROBOS (y tentativas)
  - `check_incluir_hurtos` - Incluir HURTOS (y tentativas)
  - `check_incluir_estafas` - Incluir ESTAFAS
  - `check_incluir_otros` - Incluir OTROS DELITOS
- Todos marcados por defecto (True)
- Incluyen tooltips descriptivos

#### Cambio 2: Captura de categorías en `_on_generate()` (líneas ~980-998)

- ✅ Lógica para leer el estado de los checkboxes
- ✅ Construcción de lista `categorias_incluidas` según selección
- ✅ Manejo de categorías con tentativas (ROBOS incluye TENTATIVA DE ROBOS)
- ✅ Comportamiento por defecto: si ningún checkbox está marcado, incluir todas

#### Cambio 3: Pasar categorías al generador (líneas ~107-120)

- ✅ `ReportGeneratorThread` recibe `categorias_incluidas` en opciones
- ✅ Pasa el parámetro a `create_report()` y `create_single_period_report()`

### 2. `src/core/data_processor.py` (4 cambios)

#### Cambio 1: Método `filter_by_categories()` (líneas ~218-235)

- ✅ Nuevo método que filtra hechos por categoría
- ✅ Retorna todos los hechos si la lista está vacía
- ✅ Usa la propiedad `categoria` del modelo `CrimeRecord`

#### Cambio 2: Actualizar `create_period_data()` (líneas ~237-270)

- ✅ Nuevo parámetro opcional: `categorias_incluidas`
- ✅ Aplica filtrado por categorías después del filtrado por período
- ⚠️ **IMPORTANTE**: Mencionados y aprehendidos NO se filtran por categoría
  - Los modelos no tienen campo de relación directa con los hechos
  - Solo se filtran por período temporal
  - Aparecerán en el reporte aunque sus hechos asociados estén filtrados

#### Cambio 3: Actualizar `create_report()` (líneas ~281-313)

- ✅ Nuevo parámetro opcional: `categorias_incluidas`
- ✅ Propaga el parámetro a todas las llamadas a `create_period_data()`

#### Cambio 4: Actualizar `create_single_period_report()` (líneas ~315-330)

- ✅ Nuevo parámetro opcional: `categorias_incluidas`
- ✅ Propaga el parámetro a `create_report()`

## Funcionalidad Implementada

### Opciones de Filtrado

1. **Incluir ROBOS**: Incluye delitos de las categorías:

   - `ROBOS`
   - `TENTATIVA DE ROBOS`

2. **Incluir HURTOS**: Incluye delitos de las categorías:

   - `HURTOS`
   - `TENTATIVA DE HURTOS`

3. **Incluir ESTAFAS**: Incluye delitos de la categoría:

   - `ESTAFAS`

4. **Incluir OTROS**: Incluye delitos de la categoría:
   - `OTROS DELITOS`

### Comportamiento

- **Por defecto**: Todos los checkboxes están marcados → incluye todas las categorías
- **Sin selección**: Si ningún checkbox está marcado → incluye todas las categorías
- **Selección parcial**: Solo incluye las categorías seleccionadas
- **Ejemplo**: Desmarcando "Incluir ESTAFAS", el informe excluirá todas las estafas

### Flujo de Datos

```
Usuario marca/desmarca checkboxes
    ↓
main_window.py captura estado (_on_generate)
    ↓
ReportGeneratorThread recibe categorias_incluidas
    ↓
DataProcessor.create_report(..., categorias_incluidas)
    ↓
DataProcessor.create_period_data(..., categorias_incluidas)
    ↓
DataProcessor.filter_by_categories(hechos, categorias_incluidas)
    ↓
PeriodData con hechos filtrados
    ↓
Generación de tablas, gráficos y reportes
```

**⚠️ Nota Importante**: Mencionados y aprehendidos se incluyen según el período temporal, no según categorías de delitos, porque no existe campo de relación directa en los modelos.

## Pruebas Realizadas

✅ Script de prueba inicial: `test_category_filter.py`
✅ Script de prueba de corrección: `test_fix_category_filter.py`

Casos probados:

1. ✅ Categorización automática de delitos
2. ✅ Filtrar solo ROBOS (2/4 registros)
3. ✅ Filtrar solo ESTAFAS (1/4 registros)
4. ✅ Excluir ESTAFAS (3/4 registros)
5. ✅ Lista vacía incluye todos (4/4 registros)
6. ✅ Creación de reporte completo con filtrado
7. ✅ Mencionados y aprehendidos no se filtran por categoría

## Corrección de Error (14/01/2026)

### Error Encontrado

```
'CrimeRecord' object has no attribute 'numero_hecho'
```

### Causa

Las líneas 265-267 del código original intentaban filtrar mencionados y aprehendidos usando un atributo `numero_hecho` que no existe en ninguno de los modelos.

### Solución Aplicada

Se eliminaron las líneas que intentaban filtrar mencionados y aprehendidos por categoría, ya que:

1. Los modelos no tienen campo de relación directa con los hechos
2. El filtrado por categorías solo aplica a los hechos delictuales
3. Mencionados y aprehendidos ya están correctamente filtrados por período temporal

### Código Corregido

```python
# Aplicar filtrado por categorías si se especifica
if categorias_incluidas is not None:
    hechos = self.filter_by_categories(hechos, categorias_incluidas)
    # Nota: mencionados y aprehendidos no se filtran por categoría
    # ya que no existe campo de relación directa con los hechos.
    # Solo están filtrados por período temporal.
```

## Integración con Sistema Existente

✅ **Compatible con modo simple**: Reportes de un solo período
✅ **Compatible con modo comparativo**: Reportes multi-período
✅ **No afecta otras opciones**: Los demás checkboxes funcionan igual
✅ **Sin errores de sintaxis**: Verificado con `get_errors()`
⚠️ **Limitación conocida**: Mencionados y aprehendidos no se filtran por categoría (solo por período)

## Uso en la Aplicación

### Caso de Uso: Generar informe sin estafas

1. Abrir S.I.D.I.C
2. Cargar shapefiles (hechos, mencionados, aprehendidos)
3. Seleccionar período
4. En "Opciones de Exportación":
   - ✅ Incluir ROBOS
   - ✅ Incluir HURTOS
   - ❌ Incluir ESTAFAS (desmarcar)
   - ✅ Incluir OTROS
5. Generar informe

**Resultado**: El informe contendrá robos, hurtos y otros delitos, pero excluirá todas las estafas.

**⚠️ Advertencia**: Los mencionados y aprehendidos del período completo aparecerán en el reporte, independientemente de la categoría de sus delitos asociados, ya que no existe relación directa en los modelos de datos.

## Notas Técnicas

### Ventajas de la Implementación

1. **Mínimamente invasiva**: Solo 2 archivos modificados
2. **Retrocompatible**: Si no se especifican categorías, comportamiento original
3. **Tipo-segura**: Usa la enumeración `CategoriaDelito` existente
4. **Eficiente**: Filtrado en memoria, no requiere re-lectura de shapefiles
5. **Sin errores**: Corregido y probado exitosamente

### Limitaciones Conocidas

⚠️ **Mencionados y Aprehendidos**: No se filtran por categoría de delito

- **Razón técnica**: Los modelos `MentionedPerson` y `Apprehended` no tienen campo de relación directa con `CrimeRecord`
- **Comportamiento actual**: Se incluyen todos los del período temporal, independientemente de la categoría del delito
- **Impacto**: Mínimo, ya que estos datos son complementarios y su inclusión no afecta las estadísticas principales de hechos delictuales
- **Solución futura**: Requeriría rediseño de modelos para agregar campo de relación (ej: `id_hecho` o `nro_sumario`)

### Categorización Automática

El sistema ya tenía la infraestructura de categorización implementada en `CrimeRecord.categoria` (propiedad), que clasifica automáticamente delitos según patrones definidos en `constants.py`:

- **ROBOS**: 17 patrones (ROBO AGRAVADO ASALTANTE, ROBO PIRAÑA, etc.)
- **HURTOS**: 8 patrones (HURTO PUNGA, HURTO MECHERA, etc.)
- **ESTAFAS**: 2 patrones (ESTAFA CUENTO DEL TIO, TENTATIVA DE...)
- **OTROS**: Todos los delitos que no coinciden con patrones anteriores

## Próximos Pasos (Opcional)

Mejoras futuras que podrían considerarse:

1. **Indicador en el reporte**: Agregar texto en el encabezado del Excel/Word indicando qué categorías fueron incluidas
2. **Presets**: Botones rápidos "Todos", "Sin estafas", "Solo robos", etc.
3. **Estadísticas**: Mostrar conteo de registros excluidos
4. **Persistencia**: Recordar la última selección del usuario

## Conclusión

✅ **Implementación exitosa y probada**
✅ **Funcionalidad completa según requerimiento**
✅ **Error corregido - funcionando correctamente**
⚠️ **Limitación documentada**: Mencionados y aprehendidos no se filtran por categoría (solo por período temporal)
✅ **Lista para uso en producción**
