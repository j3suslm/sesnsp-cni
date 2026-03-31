# libraries
from shiny import render, reactive
from shiny.express import input, ui
from shinywidgets import render_widget
import polars as pl
import plotly.express as px
import folium

# read dataset
df = pl.read_parquet('datasets/df.parquet')

# delegaciones array
delegaciones = sorted(df['delegacion'].unique().to_list())

# page layout 
ui.page_opts(title="Monitor de Incidencias CDMX", fillable=True, theme=ui.Theme.from_brand('_brand.yml'))

# sidebar
with ui.sidebar(open='desktop', width=260,):
    #ui.markdown('<img src="https://upload.wikimedia.org/wikipedia/commons/e/ed/Logo_SESNSP.png" alt="sesnsp" width="200"/>')
    ui.markdown('<img src="https://logoeps.com/wp-content/uploads/2013/03/flag-of-mexico-vector-logo.png" alt="mexico" width="200"/>')

    ui.input_select("delegacion", "Delegación:", choices=["TODAS"] + delegaciones)
    #ui.input_slider("mes_range", "Rango de Meses:", min=1, max=12, value=[1, 12])
    ui.input_date_range('daterange', "Rango de Meses", start='2018-01-01', end='2021-03-01', format='yyyy-mm-dd', startview='month', separator=' - ', autoclose=True)

    # dark mode
    ui.input_dark_mode()

    ui.markdown('JLM &copy; 2026')

# logic
@reactive.calc
def filtered_df():
    # Filter by date range
    res = df.filter(
        (pl.col("fecha_inicio") >= input.daterange()[0]) &
        (pl.col("fecha_inicio") <= input.daterange()[1])
    )
    
    # Filter by delegation
    if input.delegacion() != "TODAS":
        res = res.filter(pl.col("delegacion") == input.delegacion())
        
    return res

# incidencias por delegacion
def incidencias_delegacion():
    # Filter by date range
    res2 = df.filter(
        (pl.col("fecha_inicio") >= input.daterange()[0]) &
        (pl.col("fecha_inicio") <= input.daterange()[1])
    )

    conteo_del = (
        res2
        .group_by('delegacion')
        .agg(pl.col('carpeta_investigacion').count().alias('Incidencias'))
        .sort('delegacion')
        .rename({'delegacion':'Delegacion'})
    )

    return conteo_del

# judicializacion ratio
@reactive.calc
def kpi_judicializacion():
    df = filtered_df()
    if df.is_empty():
        return 0.0
    
    # Calculo
    ratio = df.select(pl.col('judicializacion').sum() / pl.col('total_flagrancias').sum()).item()
    return ratio

# kpi rezago respuesta
@reactive.calc
def kpi_tiempo_respuesta():
    df = filtered_df()
    if df.is_empty():
        return 0
    
    return (
        df.with_columns(
            ((pl.col("fecha_inicio") - pl.col("fecha_hechos")).dt.total_days()).alias("diff")
        )
        # Filtramos errores de captura (diferencias negativas o mayores a 10 años)
        .filter((pl.col("diff") >= 0) & (pl.col("diff") <= 3650))
        .select(pl.col("diff").mean())
        .item()
    )

# tabla resumen final
def generar_tabla_resumen(df):
    historico = (
        df
            .select('fecha_inicio','delegacion','PPO')
            .with_columns(pl.col("fecha_inicio").dt.truncate("1mo").alias("mes"))
            .group_by(["delegacion", "mes"])
            .agg([
                pl.len().alias("total_carpetas"),
                (pl.col("PPO").sum() / pl.len()).alias("pct_prision")
            ])
            .sort(["delegacion", "mes"])
    )

    resumen_final = (
        historico
        #.with_columns(
        #    ((pl.col("total_carpetas") - pl.col("total_carpetas").shift(1).over("delegacion")) / 
        #     pl.col("total_carpetas").shift(1).over("delegacion") * 100).alias("variacion_pct")
        #)
        # filtrar mes más reciente
        .filter(
            (pl.col('mes') >= input.daterange()[0]) &
            (pl.col('mes') <= input.daterange()[1])
        )
        .select([
            pl.col("delegacion").alias('Delegacion'),
            pl.col('mes').alias('Fecha'),
            pl.col("total_carpetas").alias("Total Carpetas"),
            (pl.col("pct_prision") * 100).round(1).alias("% Prision Preventiva"),
        #   pl.col("variacion_pct").round(1).alias("Var% (mes anterior)"),
        ])
    )

    return resumen_final

# incidencias por rango edad
def incidencias_edad(df):
    df_clean = df.filter(
        pl.col("edad").is_not_null() & (pl.col("edad") > 0) & (pl.col("edad") < 100)
    )

    # bins
    breaks = [18, 30, 45, 60]
    labels = ["0-18", "18-30", "31-45", "46-59", "60+"]

    df_bins = (
        df_clean.with_columns(
            pl.col("edad").cut(breaks, labels=labels).alias("Rango de Edad")
        )
        .group_by("Rango de Edad")
        .agg(pl.len().alias("Total"))
        .sort("Rango de Edad", descending=True)
    )

    fig = px.bar(
        df_bins,
        y="Rango de Edad",
        x="Total",
        orientation='h',
        text_auto=True,
        title="Víctimas por Grupo de Edad",
        color_discrete_sequence=["#bc955c"] 
    )

    fig.update_layout(
        plot_bgcolor="white",
        font=dict(
            family="Arial",
            size=16,
            color="black"
        ),
        xaxis=dict(
            title=dict(text="Grupo Etario", font=dict(size=16)),
            tickfont=dict(size=16)
        ),
        yaxis=dict(
            title=dict(text="Número de Incidencias", font=dict(size=16)),
            tickfont=dict(size=16)
        ),
        title=dict(
            font=dict(size=20)
        ),
        bargap=0.3,
        margin=dict(t=60, l=10, r=10, b=10)
    )

    fig.update_traces(
        textfont_size=18,
        textangle=0,
        textposition="outside",
        cliponaxis=False
    )

    return fig

# tabs
@reactive.effect
def bienvenida():
    ui.modal_show(
        ui.modal(
            ui.div(
                ui.h3("Dashboard Delictivo", 
                      style="color: #691c32; font-weight: bold;"),
                ui.p("Herramienta técnica para el análisis de indicadores de seguridad pública Ciudad de México."),
                ui.p("Elaborado por Jesus LM"),
                style="text-align: center; padding: 10px;"
            ),
            title=None,
            size="m",
            easy_close=True,
            footer=ui.modal_button("Cerrar"),
        )
    )

# intro
with ui.nav_panel("Overview"):
    ui.markdown(
    '''
    <h4 style="color:#bc955c;">Sistema de Monitoreo de Seguridad Pública CdMx</h4>

    <h4 style="color:#6f7271;">Objetivo</h4>

    Desarrollo de una plataforma analítica interactiva para visualizar la
    transición de los casos penales, desde la denuncia inicial hasta la sentencia,
    permitiendo identificar cuellos de botella y concentraciones geográficas de la
    incidencia delictiva.

    <h4 style="color:#6f7271;">Componentes Clave</h4>

    * Módulo de Incidencia: Análisis temporal de carpetas iniciadas con filtros dinámicos por municipio y rango de fechas.
    * Geointeligencia: Mapeo de precisión mediante coordenadas UTM convertidas para la identificación de hotspots criminales.
    * Análisis de Víctimas y Sentencias: Integración de datos sociodemográficos (sexo/edad).

    <h4 style="color:#6f7271;">Herramientas IT usadas</h4>
    
    Desarrollado con `Shiny for Python` y `Polars`, optimizado para el procesamiento de
    datos estructurados de alta velocidad y visualizaciones reactivas con `Plotly` y
    `Folium`.

    <i style="color:#bc955c;">Elaborado por: Jesus LM</i>
    <br>
    `2026-03-22`
    <br>
    <hr>
    '''
)

# time series
with ui.nav_panel("Análisis Temporal"):

    with ui.layout_columns(col_widths=(3, 3, 3, 3)):
        with ui.card():
            ui.card_header("Total incidencias")
            with ui.value_box(theme="danger"):
                ""
                @render.ui
                def count_summary():
                    # Calling the reactive calculation
                    return f"{len(filtered_df())}"
        with ui.card():
            ui.card_header("Indice de judicialización")
            with ui.value_box(theme="danger"):
                ""
                @render.text
                def display_kpi():
                    return f"{kpi_judicializacion():.2%}"
        with ui.card():
            ui.card_header("Retraso promedio")
            with ui.value_box(theme="danger"):
                ""
                @render.text
                def display_tiempo():
                    dias = kpi_tiempo_respuesta()
                    return f"{dias:.1f} días"
        with ui.card():
            ui.card_header("Nota")
            ui.markdown('''
            En la barra lateral, selecciona la delegación de interés.
            y en el filtro calendario, el período de interés.
            ''')

    with ui.card(full_screen=True):
        ui.card_header("Comportamiento temporal de incidencias")
        @render_widget
        def time_series_plot():
            # Get the filtered data
            data_to_plot = filtered_df()
                        
            if data_to_plot.is_empty():
                return None

            # Aggregate for the time series
            monthly_counts = (
                data_to_plot
                    .sort('fecha_inicio')
                    .group_by_dynamic("fecha_inicio", every="1mo")
                    .agg(pl.count().alias("Incidencias"))
            )

            fig = px.line(
                monthly_counts,
                x="fecha_inicio",
                y="Incidencias",
                title=f"Incidencias: {input.delegacion()}",
                markers=True,
                #template="ggplot2",
                color_discrete_sequence=["#691c32"]
            )
                        
            fig.update_layout(
                hovermode="x unified",
                paper_bgcolor='rgba(0,0,0,0)', 
                plot_bgcolor='rgba(0,0,0,0)',
                font_color="#888"
            )
            
            fig.update_traces(
                marker=dict(size=10),
                line=dict(width=3),
            )

            fig.update_xaxes(title_text=None)

            return fig

with ui.nav_panel("Análisis Etario"):
    with ui.layout_columns():
        with ui.card(full_screen=True):
            ui.card_header("Distribución de Incidencias por Edad")
            @render_widget
            def chart_edad():
                data = filtered_df()
                if data.is_empty():
                    return None
                # Usamos la función de Plotly que definimos antes
                return incidencias_edad(data)


with ui.nav_panel("Mapa Delictivo"):
    with ui.card(full_screen=True):
        ui.card_header("Visualización Espacial de Incidencias")
        @render.ui
        def incident_map():
            df_map = filtered_df()
            
            # Centro de CDMX
            m = folium.Map(location=[19.38, -99.13], zoom_start=11)
            
            for row in df_map.to_dicts():
                lat = row.get("latitud")
                lon = row.get("longitud")
                if lat:
                    folium.CircleMarker(
                        location=[lat, lon],
                        radius=6,
                        color="#691c32",
                        fill=True,
                        fill_color="#bc955c",
                        fill_opacity=0.7,
                        popup=f"Delegación: {row['delegacion']}<br>Fecha: {row['fecha_inicio']}<br>Sexo: {row['sexo']}<br>Edad: {row['edad']}"
                    ).add_to(m)
            
            return m

    

with ui.nav_panel("Anexos"):
    with ui.layout_columns(col_widths=(8, 4)):
        with ui.card(full_screen=True):
            ui.card_header("Sábana de Incidencias")
            @render.data_frame
            def raw_data_table():
                return render.DataGrid(filtered_df().select(
                    'carpeta_investigacion',
                    'fecha_inicio',
                    'fecha_hechos',
                    'delegacion',
                    ),
                    row_selection_mode="single",
                    width="100%",
                    summary=False,
                )
            
            with ui.card(full_screen=True):
                ui.card_header("Resumen Ejecutivo por Municipio")
                
                @render.data_frame
                def tabla_municipios():
                    df = generar_tabla_resumen(filtered_df())
                    return render.DataGrid(
                        df,
                        row_selection_mode="single",
                        width="100%",
                        summary=False,
                    )


        with ui.card(full_screen=True):
            ui.card_header("Incidencias por Delegación")
            @render.data_frame
            def inc_del_table():
                return render.DataGrid(
                    incidencias_delegacion(),
                    row_selection_mode="single",
                    summary=False,
                )
