import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go

# 1. Configuración de página (Más ancha y con ícono)
st.set_page_config(page_title="Dashboard Operativo TIC", layout="wide", page_icon="🚀")

# CSS Personalizado para darle un toque premium a los KPIs
st.markdown("""
<style>
    div[data-testid="metric-container"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 5% 10% 5% 10%;
        border-radius: 10px;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

st.title("📊 Análisis de Comportamiento y Re-llamadas (TIC)")
st.markdown("---")

# 2. Carga de datos
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
    return df

df = load_data()

# 3. Barra lateral de Filtros
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2043/2043064.png", width=100)
st.sidebar.header("Filtros Dinámicos")

turnos_seleccionados = st.sidebar.multiselect("Filtrar por Turno:", options=df['turno'].unique(), default=df['turno'].unique())
planes_seleccionados = st.sidebar.multiselect("Filtrar por Plan:", options=df['plan_servicio'].unique(), default=df['plan_servicio'].unique())

df_filtrado = df[(df['turno'].isin(turnos_seleccionados)) & (df['plan_servicio'].isin(planes_seleccionados))]

# 4. KPIs Principales
col1, col2, col3, col4 = st.columns(4)
tasa_re = (df_filtrado['es_rellamada'].sum() / len(df_filtrado)) * 100 if len(df_filtrado) > 0 else 0

with col1:
    st.metric("📞 Interacciones Totales", f"{len(df_filtrado):,}")
with col2:
    st.metric("⚠️ Tasa de Reincidencia", f"{tasa_re:.1f}%")
with col3:
    st.metric("⏱️ TMO Promedio", f"{df_filtrado['duracion_segundos'].mean()/60:.1f} min")
with col4:
    st.metric("✅ FCR (Primer Contacto)", f"{df_filtrado['resuelta_en_primera_llamada'].sum():,}")

st.markdown("<br>", unsafe_allow_html=True)

# 5. Pestañas de Navegación (Tabs)
tab1, tab2, tab3 = st.tabs(["📈 Análisis General", "👥 Agentes y Turnos", "📋 Detalle de Datos"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        # Gráfico de Barras interactivo
        df_rellamadas = df_filtrado[df_filtrado['es_rellamada'] == 1]
        fig1 = px.histogram(df_rellamadas, y='categoria', color='categoria', 
                            title="Volumen de Re-llamadas por Categoría",
                            template="plotly_white", text_auto=True).update_yaxes(categoryorder="total ascending")
        st.plotly_chart(fig1, use_container_width=True)
    with c2:
        # Gráfico Donut
        fig2 = px.pie(df_filtrado, names='segmento_operativo', title="Distribución por Segmento Operativo", 
                      hole=0.4, template="plotly_white")
        st.plotly_chart(fig2, use_container_width=True)

with tab2:
    c3, c4 = st.columns(2)
    with c3:
        # Gráfico de Caja (Boxplot)
        fig3 = px.box(df_filtrado, x='turno', y='duracion_segundos', color='nivel_experiencia',
                      title="Dispersión del TMO por Turno y Experiencia", template="plotly_white")
        st.plotly_chart(fig3, use_container_width=True)
    with c4:
        # Gráfico de Barras Apiladas
        fig4 = px.histogram(df_filtrado, x='nivel_experiencia', color='es_rellamada', barmode='group',
                            title="Impacto de la Experiencia en la Reincidencia",
                            labels={'es_rellamada': 'Es Re-llamada'}, template="plotly_white")
        st.plotly_chart(fig4, use_container_width=True)

with tab3:
    st.subheader("Base de Datos Exploratoria")
    st.dataframe(df_filtrado.sort_values('fecha_hora', ascending=False).head(100), use_container_width=True)
