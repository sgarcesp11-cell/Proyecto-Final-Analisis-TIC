import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

# -------------------------------------------------------------------------
# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
# -------------------------------------------------------------------------
st.set_page_config(page_title="Control Tower - TIC", layout="wide", page_icon="📡")

st.markdown("""
<style>
    .metric-card { background-color: #ffffff; border-radius: 10px; padding: 20px; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1); border-left: 5px solid #1f77b4; }
</style>
""", unsafe_allow_html=True)

st.title("📡 Control Tower: Análisis de Reincidencia TIC")
st.markdown("Plataforma interactiva para el monitoreo de FCR, comportamiento de re-llamadas y rendimiento de asesores.")
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
            a.turno, a.nombre AS nombre_agente, t.categoria, t.prioridad, f.duracion_segundos,
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
    
    df['fecha_hora'] = pd.to_datetime(df['fecha_hora'])
    df['fecha_dia'] = df['fecha_hora'].dt.date
    df['hora'] = df['fecha_hora'].dt.hour
    
    dias_semana = {0: '1-Lunes', 1: '2-Martes', 2: '3-Miércoles', 3: '4-Jueves', 4: '5-Viernes', 5: '6-Sábado', 6: '7-Domingo'}
    df['dia_semana'] = df['fecha_hora'].dt.dayofweek.map(dias_semana)
    
    meses_dict = {1:'01-Ene', 2:'02-Feb', 3:'03-Mar', 4:'04-Abr', 5:'05-May', 6:'06-Jun', 
                  7:'07-Jul', 8:'08-Ago', 9:'09-Sep', 10:'10-Oct', 11:'11-Nov', 12:'12-Dic'}
    df['mes'] = df['fecha_hora'].dt.month.map(meses_dict)
    
    return df

df = load_data()

# -------------------------------------------------------------------------
# 3. BARRA LATERAL (SIDEBAR) - FILTROS AVANZADOS
# -------------------------------------------------------------------------
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/8633/8633190.png", width=120)
st.sidebar.header("🎯 Segmentación Dinámica")

meses = st.sidebar.multiselect("📅 Mes de Operación:", options=sorted(df['mes'].unique()), default=sorted(df['mes'].unique()))
turnos = st.sidebar.multiselect("⌚ Turno Operativo:", options=df['turno'].unique(), default=df['turno'].unique())
experiencia = st.sidebar.multiselect("🎖️ Nivel de Experiencia:", options=df['nivel_experiencia'].unique(), default=df['nivel_experiencia'].unique())
prioridad = st.sidebar.multiselect("🚨 Prioridad del Caso:", options=df['prioridad'].unique(), default=df['prioridad'].unique())

df_filtrado = df[
    (df['mes'].isin(meses)) &
    (df['turno'].isin(turnos)) & 
    (df['nivel_experiencia'].isin(experiencia)) & 
    (df['prioridad'].isin(prioridad))
]

# -------------------------------------------------------------------------
# 4. KPIs PRINCIPALES (AHORA CON METAS/DELTAS)
# -------------------------------------------------------------------------
if len(df_filtrado) == 0:
    st.warning("⚠️ No hay datos para los filtros seleccionados.")
else:
    col1, col2, col3, col4 = st.columns(4)
    total_casos = len(df_filtrado)
    tasa_re = (df_filtrado['es_rellamada'].sum() / total_casos) * 100
    tmo_prom = df_filtrado['duracion_segundos'].mean() / 60
    fcr_pct = (df_filtrado['resuelta_en_primera_llamada'].sum() / total_casos) * 100

    # Metas Operativas Estándar
    meta_re = 15.0
    meta_fcr = 75.0
    meta_tmo = 15.0

    col1.metric("📞 Interacciones Atendidas", f"{total_casos:,}", "Volumen Filtrado")
    col2.metric("⚠️ Tasa de Reincidencia", f"{tasa_re:.1f}%", f"{meta_re - tasa_re:.1f}% vs Meta (15%)", delta_color="inverse")
    col3.metric("⏱️ TMO Promedio", f"{tmo_prom:.1f} min", f"{meta_tmo - tmo_prom:.1f} min vs Meta (15m)", delta_color="inverse")
    col4.metric("✅ Resolución 1er Contacto", f"{fcr_pct:.1f}%", f"{fcr_pct - meta_fcr:.1f}% vs Meta (75%)")

    st.markdown("<br>", unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # 5. TABS DE ANÁLISIS
    # -------------------------------------------------------------------------
    tab1, tab2, tab3, tab4 = st.tabs(["🔥 Mapas de Calor", "📈 Análisis General & Pareto", "👥 Análisis de Asesores", "📋 Base de Datos"])

    with tab1:
        st.subheader("Análisis de Saturación y Riesgo Operativo")
        
        # NUEVO: Velocímetros de Salud Operativa
        c_v1, c_v2 = st.columns(2)
        with c_v1:
            fig_gauge1 = go.Figure(go.Indicator(
                mode = "gauge+number", value = tasa_re, title = {'text': "Termómetro de Re-llamadas"},
                gauge = {'axis': {'range': [0, 40]}, 'bar': {'color': "darkred"},
                         'steps': [{'range': [0, 15], 'color': "lightgreen"}, {'range': [15, 25], 'color': "yellow"}, {'range': [25, 40], 'color': "salmon"}]}
            ))
            fig_gauge1.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_gauge1, use_container_width=True)
            
        with c_v2:
            fig_gauge2 = go.Figure(go.Indicator(
                mode = "gauge+number", value = fcr_pct, title = {'text': "Efectividad FCR"},
                gauge = {'axis': {'range': [0, 100]}, 'bar': {'color': "darkblue"},
                         'steps': [{'range': [0, 60], 'color': "salmon"}, {'range': [60, 75], 'color': "yellow"}, {'range': [75, 100], 'color': "lightgreen"}]}
            ))
            fig_gauge2.update_layout(height=250, margin=dict(l=10, r=10, t=30, b=10))
            st.plotly_chart(fig_gauge2, use_container_width=True)

        st.markdown("---")
        st.markdown("**1. Mapa de Calor: Re-llamadas por Día y Hora**")
        df_rellamadas = df_filtrado[df_filtrado['es_rellamada'] == 1]
        hm_dia_hora = df_rellamadas.groupby(['dia_semana', 'hora']).size().reset_index(name='volumen')
        fig_hm1 = px.density_heatmap(hm_dia_hora, x='hora', y='dia_semana', z='volumen', color_continuous_scale='Inferno', text_auto=True)
        fig_hm1.update_yaxes(categoryorder='category descending') 
        st.plotly_chart(fig_hm1, use_container_width=True)
        
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**2. Mapa de Calor: Volumen por Día y Experiencia**")
            hm_dia_exp = df_filtrado.groupby(['dia_semana', 'nivel_experiencia']).size().reset_index(name='volumen')
            fig_hm2 = px.density_heatmap(hm_dia_exp, x='nivel_experiencia', y='dia_semana', z='volumen', color_continuous_scale='Blues', text_auto=True)
            fig_hm2.update_yaxes(categoryorder='category descending')
            st.plotly_chart(fig_hm2, use_container_width=True)
            
        with c2:
            st.markdown("**3. Mapa de Calor: Tipo de Incidencia vs Hora del Día**")
            hm_inc_hora = df_filtrado.groupby(['categoria', 'hora']).size().reset_index(name='volumen')
            fig_hm3 = px.density_heatmap(hm_inc_hora, x='hora', y='categoria', z='volumen', color_continuous_scale='Viridis', text_auto=True)
            st.plotly_chart(fig_hm3, use_container_width=True)

    with tab2:
        # NUEVO: Análisis de Pareto (80/20)
        st.subheader("Análisis de Pareto: Raíz de las Re-llamadas")
        df_pareto = df_filtrado[df_filtrado['es_rellamada'] == 1].groupby('categoria').size().reset_index(name='volumen')
        df_pareto = df_pareto.sort_values(by='volumen', ascending=False)
        df_pareto['acumulado_pct'] = df_pareto['volumen'].cumsum() / df_pareto['volumen'].sum() * 100

        fig_pareto = go.Figure()
        fig_pareto.add_trace(go.Bar(x=df_pareto['categoria'], y=df_pareto['volumen'], name='Volumen', marker_color='rgb(55, 83, 109)'))
        fig_pareto.add_trace(go.Scatter(x=df_pareto['categoria'], y=df_pareto['acumulado_pct'], name='% Acumulado', yaxis='y2', mode='lines+markers', marker_color='rgb(219, 64, 82)'))
        fig_pareto.update_layout(
            title='Ley de Pareto (80/20) en Tipología de Incidencias',
            yaxis=dict(title='Volumen de Re-llamadas'),
            yaxis2=dict(title='% Acumulado', overlaying='y', side='right', range=[0, 110]),
            template="plotly_white", legend=dict(x=0.8, y=0.1)
        )
        st.plotly_chart(fig_pareto, use_container_width=True)

        c3, c4 = st.columns(2)
        with c3:
            fig_box = px.box(df_filtrado, x='segmento_operativo', y='duracion_segundos', color='turno', title="Dispersión del TMO por Segmento", template="plotly_white")
            st.plotly_chart(fig_box, use_container_width=True)
        with c4:
            df_tendencia = df_filtrado.groupby('mes')['es_rellamada'].sum().reset_index()
            fig_line = px.bar(df_tendencia, x='mes', y='es_rellamada', title="Evolución Mensual de Re-llamadas", template="plotly_white", text_auto=True)
            st.plotly_chart(fig_line, use_container_width=True)

    with tab3:
        st.subheader("Rendimiento Individual por Asesor")
        df_agentes = df_filtrado.groupby(['nombre_agente', 'nivel_experiencia']).agg(
            total_llamadas=('id_interaccion', 'count'), tmo_promedio=('duracion_segundos', 'mean'), total_rellamadas=('es_rellamada', 'sum')
        ).reset_index()
        
        df_agentes['tasa_rellamada'] = (df_agentes['total_rellamadas'] / df_agentes['total_llamadas']) * 100
        df_agentes['tmo_promedio_min'] = df_agentes['tmo_promedio'] / 60
        
        c5, c6 = st.columns(2)
        with c5:
            fig_scatter = px.scatter(df_agentes, x='tmo_promedio_min', y='tasa_rellamada', color='nivel_experiencia',
                                     hover_name='nombre_agente', size='total_llamadas', title="Matriz: TMO vs Tasa de Re-llamadas",
                                     labels={'tmo_promedio_min': 'TMO Promedio (Min)', 'tasa_rellamada': '% Re-llamadas'}, template="plotly_white")
            fig_scatter.add_hline(y=df_agentes['tasa_rellamada'].mean(), line_dash="dot", line_color="red", annotation_text="Promedio Falla")
            fig_scatter.add_vline(x=df_agentes['tmo_promedio_min'].mean(), line_dash="dot", line_color="blue", annotation_text="Promedio TMO")
            st.plotly_chart(fig_scatter, use_container_width=True)
            
        with c6:
            df_peores = df_agentes.sort_values('tasa_rellamada', ascending=False).head(10)
            fig_ranking = px.bar(df_peores, x='tasa_rellamada', y='nombre_agente', color='nivel_experiencia',
                                 orientation='h', title="Top 10 Asesores Críticos (% Reincidencia)", template="plotly_white", text_auto='.1f')
            fig_ranking.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_ranking, use_container_width=True)

    with tab4:
        st.subheader("Extracción de Datos Crudos")
        
        # NUEVO: Botón de descarga profesional
        csv = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar Base de Datos Filtrada (CSV)",
            data=csv,
            file_name='dataset_tic_filtrado.csv',
            mime='text/csv',
        )
        st.markdown("<br>", unsafe_allow_html=True)
        st.dataframe(df_filtrado.sort_values('fecha_hora', ascending=False).head(500), use_container_width=True)