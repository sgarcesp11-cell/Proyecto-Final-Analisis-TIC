import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# -------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
# -------------------------------------------------------------------------
st.set_page_config(page_title="Control Tower - TIC", layout="wide", page_icon="📡")

# Inyectar CSS personalizado para mejorar el diseño de las métricas
st.markdown("""
<style>
    .metric-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 20px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #1f77b4;
    }
</style>
""", unsafe_allow_html=True)

# Banner de imagen superior (usando una imagen pública de Unsplash para darle un toque pro)
st.image("https://images.unsplash.com/photo-1551288049-bebda4e38f71?auto=format&fit=crop&w=2000&q=80", use_container_width=True)

st.title("📡 Control Tower: Análisis de Reincidencia TIC")
st.markdown("Plataforma interactiva para el monitoreo de resolución en primer contacto (FCR) y comportamiento de re-llamadas. Proyecto Final Talento Tech.")
st.markdown("---")

# -------------------------------------------------------------------------
# 2. CARGA Y PREPARACIÓN DE DATOS
# -------------------------------------------------------------------------
@st.cache_data
def load_data():
    conn = sqlite3.connect('proyecto_tic.db')
    query = """
        SELECT 
            f.id_interaccion, f.fecha_hora, u.plan_servicio, a.nivel_experiencia,
            a.turno, t.categoria, t.prioridad, f.duracion_segundos,
            f.resuelta_en_primera_llamada, f.es_rellamada,
            CASE 
                WHEN u.fecha_registro >= '2025-01-01' THEN 'A: Clientes nuevos'
                WHEN f.duracion_segundos = 0 THEN 'B: No contacto'
                WHEN f.duracion_segundos > 180 THEN 'C: Contacto con TMO > 3 Min'
                ELSE 'D: restantes' 
            END AS segmento_operativo
        FROM Fact_Interacciones f
        JOIN Dim_Usuarios u ON f.id_usuario = u.id_usuario
        JOIN Dim_Agentes a ON f.id_agente = a.id_agente
        JOIN Dim_Tipo_Incidencia t ON f.id_tipo_incidencia = t.id_tipo_incidencia
    """
    df = pd.read_sql_query(query, conn)
    conn.close()
    
    # Asegurar formato de fecha para gráficas temporales
    df['fecha_hora'] = pd.to_datetime(df['fecha_hora'])
    df['fecha_dia'] = df['fecha_hora'].dt.date
    return df

df = load_data()

# -------------------------------------------------------------------------
# 3. BARRA LATERAL (SIDEBAR) - FILTROS AVANZADOS
# -------------------------------------------------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/8633/8633190.png", width=120)
st.sidebar.header("🎯 Segmentación Dinámica")
st.sidebar.markdown("Usa estos filtros para explorar distintos escenarios.")

# Multiselects
turnos = st.sidebar.multiselect("⌚ Turno Operativo:", options=df['turno'].unique(), default=df['turno'].unique())
experiencia = st.sidebar.multiselect("🎖️ Nivel de Experiencia:", options=df['nivel_experiencia'].unique(), default=df['nivel_experiencia'].unique())
prioridad = st.sidebar.multiselect("🚨 Prioridad del Caso:", options=df['prioridad'].unique(), default=df['prioridad'].unique())
segmentos = st.sidebar.multiselect("📊 Segmento Operativo:", options=df['segmento_operativo'].unique(), default=df['segmento_operativo'].unique())

# Aplicar todos los filtros al DataFrame
df_filtrado = df[
    (df['turno'].isin(turnos)) & 
    (df['nivel_experiencia'].isin(experiencia)) & 
    (df['prioridad'].isin(prioridad)) &
    (df['segmento_operativo'].isin(segmentos))
]

# -------------------------------------------------------------------------
# 4. KPIs PRINCIPALES (Tarjetas)
# -------------------------------------------------------------------------
if len(df_filtrado) == 0:
    st.warning("⚠️ No hay datos para los filtros seleccionados. Por favor ajusta tu búsqueda.")
else:
    col1, col2, col3, col4 = st.columns(4)
    
    total_casos = len(df_filtrado)
    tasa_re = (df_filtrado['es_rellamada'].sum() / total_casos) * 100
    tmo_prom = df_filtrado['duracion_segundos'].mean() / 60
    fcr_pct = (df_filtrado['resuelta_en_primera_llamada'].sum() / total_casos) * 100

    col1.metric("📞 Interacciones Atendidas", f"{total_casos:,}", "Volumen total")
    col2.metric("⚠️ Tasa de Reincidencia", f"{tasa_re:.1f}%", "- Objetivo: < 15%", delta_color="inverse")
    col3.metric("⏱️ TMO Promedio", f"{tmo_prom:.1f} min", "Tiempo de operación")
    col4.metric("✅ Resolución 1er Contacto", f"{fcr_pct:.1f}%", "+ Objetivo: > 70%")

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 5. TABS DE ANÁLISIS (Pestañas organizadas)
    # -------------------------------------------------------------------------
    tab1, tab2, tab3 = st.tabs(["📈 Análisis de Reincidencia", "👥 Rendimiento Operativo", "📋 Base de Datos"])

    with tab1:
        st.subheader("Drivers de Re-llamadas")
        c1, c2 = st.columns(2)
        
        with c1:
            # Gráfico de Barras: Volumen por Categoría
            df_re = df_filtrado[df_filtrado['es_rellamada'] == 1]
            fig1 = px.histogram(df_re, y='categoria', color='prioridad', 
                                title="Volumen de Re-llamadas por Categoría y Prioridad",
                                template="plotly_white", barmode='stack')
            fig1.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig1, use_container_width=True)
            
        with c2:
            # Heatmap de Riesgo (Cruce de Prioridad vs Experiencia)
            matriz_riesgo = df_filtrado.pivot_table(index='prioridad', columns='nivel_experiencia', 
                                                    values='es_rellamada', aggfunc='mean') * 100
            fig2 = px.imshow(matriz_riesgo, text_auto=".1f", aspect="auto", color_continuous_scale='Reds',
                             title="Matriz de Riesgo: % Reincidencia (Prioridad vs Experiencia)")
            st.plotly_chart(fig2, use_container_width=True)

        # Gráfico de Línea: Evolución temporal
        df_tendencia = df_filtrado.groupby('fecha_dia')['es_rellamada'].sum().reset_index()
        fig3 = px.line(df_tendencia, x='fecha_dia', y='es_rellamada', markers=True, 
                       title="Evolución Temporal de Re-llamadas Diarias", template="plotly_white", color_discrete_sequence=['#e63946'])
        st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        st.subheader("Análisis de Tiempos y Esfuerzo")
        c3, c4 = st.columns(2)
        
        with c3:
            # Boxplot de TMO
            fig4 = px.box(df_filtrado, x='segmento_operativo', y='duracion_segundos', color='turno',
                          title="Dispersión del TMO por Segmento Operativo", template="plotly_white")
            st.plotly_chart(fig4, use_container_width=True)
            
        with c4:
            # Pie chart: Distribución de esfuerzo
            fig5 = px.pie(df_filtrado, names='plan_servicio', values='duracion_segundos', 
                          title="Tiempo Total Invertido por Plan de Servicio", hole=0.3, template="plotly_white")
            st.plotly_chart(fig5, use_container_width=True)

    with tab3:
        st.subheader("Extracción de Datos")
        st.markdown("Visualiza y descarga el dataset consolidado basado en los filtros aplicados.")
        st.dataframe(df_filtrado.sort_values('fecha_hora', ascending=False), use_container_width=True)
