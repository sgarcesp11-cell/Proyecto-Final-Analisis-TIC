# 📡 Control Tower: Análisis de Reincidencia y Comportamiento (TIC)

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Plotly](https://img.shields.io/badge/Plotly-3F4F75?style=for-the-badge&logo=plotly&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-003B57?style=for-the-badge&logo=sqlite&logoColor=white)

Una aplicación web interactiva construida con **Streamlit** para analizar el comportamiento operativo y la resolución de incidencias en un entorno BPO, procesando un dataset simulado de 25,000 interacciones a través de una base de datos relacional.

---

## 🚀 Enlaces del Proyecto
* 🌐 **Landing Page (Contexto y Presentación):** [Visitar Página Web](https://sgarcesp11-cell.github.io/Proyecto-Final-Analisis-TIC/)
* 📊 **Dashboard Interactivo (Torre de Control):** [Abrir Aplicación en Vivo](https://gujkjps22j9cgpjaueht8o.streamlit.app/)

---

Este repositorio contiene el código fuente y la base de datos para el Proyecto Final del Nivel Integrador del bootcamp Talento Tech. El proyecto se enfoca en la línea de investigación de Tecnologías de la Información y la Comunicación (TIC), resolviendo un desafío analítico común en operaciones de atención al usuario.

## 🎯 Objetivo del Proyecto
Desarrollar una solución analítica integral para monitorear, analizar y mitigar la tasa de "re-llamadas" (reincidencia) en una plataforma de soporte TIC. A través del análisis del comportamiento de los usuarios y la efectividad operativa, este dashboard permite identificar cuellos de botella en la resolución en el primer contacto (FCR) y evaluar el impacto del Tiempo Medio de Operación (TMO).

## 🛠️ Tecnologías Utilizadas
El proyecto integra un flujo de trabajo completo de análisis de datos:
* **Base de Datos:** `SQLite` (Modelo de Estrella con 1 tabla de hechos y 3 dimensiones).
* **Procesamiento de Datos:** `Pandas` para manipulación, limpieza y cálculo de KPIs estadísticos.
* **Visualización:** `Plotly` para gráficos interactivos (Heatmaps, diagramas de Pareto, Boxplots, Series de Tiempo).
* **Despliegue Web:** `Streamlit` para la creación de la interfaz y `GitHub Pages` para la Landing Page corporativa.

## 📊 Características del Dashboard
* **Filtros Dinámicos:** Capacidad de segmentar la data en vivo por Mes, Turno Operativo, Nivel de Experiencia del agente y Prioridad de la incidencia.
* **KPIs Estratégicos:** Tarjetas de métricas calculadas en tiempo real para Interacciones Totales, Tasa de Reincidencia, TMO Promedio y Volumen FCR, comparados contra metas operativas.
* **Análisis Visual:** * Mapas de calor (Heatmaps) para medir riesgo por saturación de turnos.
  * Regla 80/20 (Pareto) para priorizar las causas de soporte técnico.
  * Matriz de dispersión para detectar falsos positivos en la velocidad de atención de los asesores.
* **Extracción de Datos:** Opción integrada para descargar el *dataframe* consolidado y filtrado en formato CSV.

## 📂 Estructura del Repositorio
* `app.py`: Script principal de Python que ejecuta el dashboard de Streamlit y renderiza las visualizaciones.
* `index.html`: Código fuente de la Landing Page estática alojada en GitHub Pages.
* `proyecto_tic.db`: Base de datos relacional (SQLite) que contiene el histórico de la operación.
* `requirements.txt`: Archivo de dependencias necesarias para el despliegue en Streamlit Community Cloud.
* `README.md`: Documentación principal del proyecto.

## 👥 Equipo Desarrollador
* Santiago Garcés
* Yorleidys Osorio Contreras
* Karoly Arrubla Rojas
* Juan Esteban Gomez Acero
