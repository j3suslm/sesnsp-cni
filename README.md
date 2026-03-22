# Justificación del Uso de Software (Python)

Se eligió `Shiny for Python` en combinación con `Polars` y `folium` debido a la alta eficiencia en el procesamiento de grandes volúmenes de datos (Excel y transformaciones de series de tiempo).

La arquitectura de `Polars` permite una reactividad más fluida en el dashboard al manejar operaciones de agregación temporal de forma vectorizada, mientras que `Shiny for Python` ofrece una sintaxis moderna que prioriza la mantenibilidad y la rapidez en el despliegue de prototipos de grado producción.

# Procedimiento

### Limpieza de Datos

* Estandarización de Municipios: (quitar acentos y limpiar nombres (ej. "GUSTAVO A MADERO" vs "GUSTAVO A. MADERO").

* Manejo de Coordenadas: Las coordenadas están en UTM, se convirtieron a Lat/Lon para que el mapa de Folium/Leaflet.

* Cruce de Hojas: Se realizaron joins entre las diversas hojas de excel y se crearon archivos parquet para un almacenamiento más eficiente y la apertura a la creación de un data lake futuro.

### KPIs

* Índice de judicialización: (Imputados Judicializados / Total de Flagrancias).

* Tiempo de Respuesta: Diferencia promedio entre "Fecha de hechos" y "Fecha de inicio" (mide la demora en denuncia).

### Visualización de datos

- Serie de Tiempo: Gráfico interactivo de líneas para el comportamiento temporal de Incidencias por mes.

- Mapa interactivo de incidencias individuales ya que son pocos registros.

- Tabla: Resumen de Carpetas de investigación, fecha, y % de Prisión Preventiva.

# Resumen Ejecutivo del Proyecto

Resumen: Sistema de Monitoreo de Etapas Procesales (SMEP)

Objetivo:
Desarrollo de una plataforma analítica interactiva para visualizar la transición de los casos penales, desde la denuncia inicial hasta la sentencia, permitiendo identificar cuellos de botella y concentraciones geográficas de la incidencia delictiva.

Componentes Clave:

- Módulo de Incidencia: Análisis temporal de carpetas iniciadas con filtros dinámicos por municipio y rango de fechas.

- Geointeligencia: Mapeo de precisión mediante coordenadas UTM convertidas para la identificación de hotspots criminales.

- Análisis de Víctimas y Sentencias: Integración de datos sociodemográficos (edad).

Tecnología:
Desarrollado con Shiny for Python y Polars, optimizado para el procesamiento de datos estructurados de alta velocidad y visualizaciones reactivas con Plotly y Folium.

# Organización de Código

- Data Ingestion: Lectura de las 4-5 hojas del Excel a archivos parquet.

- Preprocessing Pipeline: Función única que limpie nombres de municipios, formatee fechas y realice los joins de víctimas.

- UI: Sidebar para filtros globales y nav_panels para separar "Análisis Temporal", "Mapa", "Análisis Etario" y "Anexos".

- Server/Logic: Uso de @reactive.calc para que todos los gráficos beban de la misma base filtrada, evitando cálculos redundantes.
