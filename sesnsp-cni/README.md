# Justificación

## Uso de Software (Python)

Utilzo `Python` debido a diversos beneficios, tales como: la alta eficiencia en el procesamiento de grandes volúmenes de datos, la integración con aplicaciones web (Flask o FastAPI), la automatización de procesos del sistema, la fácil conexión con arquitecturas de software complejas así como el soporte de la comunidad.

Para este proyecto, utilizamos `Polars` ya que permite una reactividad más fluida en el dashboard al manejar operaciones de agregación temporal de forma vectorizada, mientras que `Shiny for Python` ofrece una sintaxis moderna que prioriza la mantenibilidad y la rapidez en el despliegue de prototipos de grado producción.

# Procedimiento

## Limpieza de Datos

* Estandarización de Municipios: (quitar acentos y limpiar nombres (ej. "GUSTAVO A MADERO" vs "GUSTAVO A. MADERO").

* Manejo de Coordenadas: Las coordenadas están en UTM, se convirtieron a Lat/Lon para el mapa de Folium/Leaflet.

* Cruce de Hojas: Se realizaron joins entre las diversas hojas de excel y se crearon archivos parquet para un almacenamiento más eficiente y la apertura a la creación de un data lake futuro.

## KPIs

* Índice de judicialización: (Imputados Judicializados / Total de Flagrancias).

* Tiempo de Respuesta: Diferencia promedio entre "Fecha de hechos" y "Fecha de inicio" (mide la demora en denuncia).

## Visualización de datos

- Serie de Tiempo: Gráfico interactivo de líneas para el comportamiento temporal de Incidencias por mes.

- Mapa interactivo de incidencias individuales ya que son pocos registros.

- Tabla: Resumen de Carpetas de investigación, fecha, y % de Prisión Preventiva.

# Resumen Ejecutivo del Proyecto

Resumen: Sistema de Monitoreo de Etapas Procesales (SMEP)

**Objetivo**

Desarrollo de una plataforma analítica interactiva para visualizar la transición de los casos penales, desde la denuncia inicial hasta la sentencia, permitiendo identificar cuellos de botella y concentraciones geográficas de la incidencia delictiva.

**Componentes clave**

- Módulo de Incidencia: Análisis temporal de carpetas iniciadas con filtros dinámicos por municipio y rango de fechas.

- Geointeligencia: Mapeo de precisión mediante coordenadas UTM convertidas para la identificación de hotspots criminales.

- Análisis de Víctimas y Sentencias: Integración de datos sociodemográficos (edad).

**Tecnología**

Desarrollado con Shiny for Python y Polars, optimizado para el procesamiento de datos estructurados de alta velocidad y visualizaciones reactivas con Plotly y Folium.

# Organización de Código

- Manejo de datos: Lectura de las 4-5 hojas del Excel a archivos parquet.

- Preprocesamiento: Función única que limpie nombres de municipios, formatee fechas y realice los joins de víctimas.

- UI: Sidebar para filtros globales y nav_panels para separar "Análisis Temporal", "Mapa", "Análisis Etario" y "Anexos".

- Server/Logic: Uso de @reactive.calc para que todos los gráficos beban de la misma base filtrada, evitando cálculos redundantes.
