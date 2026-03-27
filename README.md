# 📡 Control Tower: Análisis de Reincidencia y Comportamiento (TIC)

Este repositorio contiene el código fuente y la base de datos para el Proyecto Final del Nivel Integrador del bootcamp Talento Tech[cite: 4, 5, 31]. [cite_start]El proyecto se enfoca en la línea de investigación de Tecnologías de la Información y la Comunicación (TIC), resolviendo un desafío analítico común en operaciones de atención al usuario[cite: 8, 32].

## 🎯 Objetivo del Proyecto
Desarrollar una solución analítica integral para monitorear, analizar y mitigar la tasa de "re-llamadas" (reincidencia) en una plataforma de soporte TIC[cite: 14, 32]. A través del análisis del comportamiento de los usuarios y la efectividad operativa, este dashboard permite identificar cuellos de botella en la resolución en el primer contacto (FCR) y evaluar el impacto del Tiempo Medio de Operación (TMO).

## 🛠️ Tecnologías Utilizadas
El proyecto integra un flujo de trabajo completo de análisis de datos:
* **Base de Datos:** `SQLite` (Modelo de Estrella con tablas de hechos y dimensiones)[cite: 35].
* **Procesamiento de Datos:** `Pandas` para manipulación, agrupación y cálculo de KPIs estadísticos[cite: 41].
* **Visualización:** `Plotly` para gráficos interactivos (Heatmaps, Boxplots, Series de Tiempo)[cite: 43].
* ]**Despliegue Web:** `Streamlit` para la creación del dashboard interactivo y su alojamiento en la nube[cite: 43].

## 📊 Características del Dashboard
* **Filtros Dinámicos:** Capacidad de segmentar la data en vivo por Turno Operativo, Nivel de Experiencia del agente, Prioridad de la incidencia y Segmento Operativo.
* **KPIs Estratégicos:** Tarjetas de métricas calculadas en tiempo real para Interacciones Totales, Tasa de Reincidencia, TMO Promedio y Volumen FCR.
* **Análisis Visual:** * Matriz de riesgo para cruzar prioridad vs. experiencia.
  * Distribución del esfuerzo operativo por planes de servicio.
  * Análisis de dispersión del TMO para detectar valores atípicos (outliers).
* **Extracción de Datos:** Pestaña dedicada para visualizar el *dataframe* consolidado y filtrado.

## 📂 Estructura del Repositorio
* `app.py`: Script principal de Python que ejecuta la aplicación de Streamlit y renderiza las visualizaciones[cite: 74].
* `proyecto_tic.db`: Base de datos relacional (SQLite) que contiene las tablas `Fact_Interacciones`, `Dim_Usuarios`, `Dim_Agentes` y `Dim_Tipo_Incidencia`[cite: 35, 74].
* `requirements.txt`: Archivo de dependencias necesarias para el despliegue en Streamlit Community Cloud.
* `README.md`: Documentación principal del proyecto.

## 🚀 Cómo ejecutar el proyecto localmente
Si deseas correr este dashboard en tu máquina local, sigue estos pasos:

1. Clona este repositorio:
   ```bash
   git clone [https://github.com/TuUsuario/Proyecto-Analisis-TIC.git](https://github.com/TuUsuario/Proyecto-Analisis-TIC.git)
