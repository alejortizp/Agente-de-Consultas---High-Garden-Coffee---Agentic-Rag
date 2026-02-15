# Agente de Consultas - High Garden Coffee

agente conversacional de análisis de datos para la empresa exportadora de café **High Garden Coffee**.

## Contexto del Problema

High Garden Coffee es una exportadora de café internacional que posee una base de datos de consumo doméstico de café (en tazas) desde 1990 hasta 2020, con datos de diferentes países y tipos de café. El área de innovación busca aprovechar estos datos para identificar tendencias, información clave y obtener ventaja competitiva en el mercado.

## Solución Implementada

Se construyó un **agente conversacional** que permite al usuario consultar los datos en lenguaje natural. El agente utiliza un modelo LLM (GPT-4o) integrado con un agente de pandas de LangChain para ejecutar análisis directamente sobre los datos y generar visualizaciones bajo demanda.

### Componentes principales

| Componente | Descripción |
|---|---|
| `data_transformation.py` | Pipeline ETL que transforma el dataset original (`coffee_db.parquet`, formato ancho) a formato largo (`coffee_final.csv`) con columnas: Fecha, Country, Ventas, Coffee type |
| `improved_data_agent.py` | Agente principal con interfaz REPL interactiva. Contiene la lógica de carga de datos, el agente LangChain y el generador de gráficas |

### Stack Tecnológico

- **LLM:** OpenAI GPT-4o via `langchain-openai`
- **Agente:** `langchain-experimental` (`create_pandas_dataframe_agent`) con ejecución de código Python habilitada
- **Datos:** pandas + pyarrow
- **Visualización:** matplotlib + seaborn
- **Gestión de dependencias:** uv

## Dataset

El dataset transformado (`coffee_final.csv`) contiene **1,650 registros** con la siguiente estructura:

| Columna | Tipo | Descripción |
|---|---|---|
| `Fecha` | datetime | Año del registro (1991-2020) |
| `Country` | string | País productor/consumidor |
| `Ventas` | numérico | Consumo doméstico en tazas |
| `Coffee type` | string | Tipo de café: Arabica, Robusta o Mezcla (Arabica/Robusta) |

## Instalación y Ejecución

### Requisitos previos

- Python >= 3.14
- [uv](https://docs.astral.sh/uv/) (gestor de paquetes)
- Una API key de OpenAI

### Pasos

1. Clonar el repositorio e instalar dependencias:

```bash
uv sync
```

2. Crear un archivo `.env` en la raíz del proyecto:

```
OPENAI_API_KEY=sk-...
```

3. (Opcional) Regenerar el CSV a partir del parquet original:

```bash
uv run python data_transformation.py
```

4. Ejecutar el agente:

```bash
uv run python improved_data_agent.py
```

## Uso

Al iniciar, el agente muestra un resumen del dataset y queda en espera de consultas. Ejemplos:

```
🔍 Tu consulta: ¿Cuáles son las ventas totales por país?
🔍 Tu consulta: Muestra un gráfico de líneas de ventas por año para Colombia
🔍 Tu consulta: Compara las ventas de Arabica vs Robusta con un gráfico de barras
🔍 Tu consulta: ¿Cuál es el país con mayor consumo promedio?
```

Las visualizaciones se guardan automáticamente en la carpeta `plots/` con nombres descriptivos y timestamp.

Para salir: `salir`, `exit` o `quit`.

## Estructura del Proyecto

```
├── coffee_db.parquet          # Dataset original (formato ancho)
├── data_transformation.py     # ETL: parquet → CSV formato largo
├── coffee_final.csv           # Dataset transformado (generado)
├── improved_data_agent.py     # Agente conversacional principal
├── plots/                     # Gráficas generadas (auto-creado)
├── data_agent.log             # Logs de ejecución
├── pyproject.toml             # Configuración del proyecto y dependencias
├── uv.lock                    # Lockfile de dependencias

```

## Decisiones de Diseño

- **Agente pandas sobre RAG:** Se optó por un agente que ejecuta código pandas directamente en lugar de un enfoque RAG, ya que permite consultas analíticas arbitrarias (agregaciones, filtros, comparaciones) sin limitarse a fragmentos de texto pre-indexados.
- **Herramienta de visualización como tool de LangChain:** El generador de gráficas se registra como `StructuredTool`, permitiendo que el LLM decida cuándo y cómo generar visualizaciones basándose en la consulta del usuario.
- **Auto-detección de tipos:** `DataLoader` detecta automáticamente columnas de fecha y numéricas, haciendo el agente adaptable a otros datasets CSV sin modificar código.
- **Temperatura 0.0:** Configuración determinista para obtener respuestas consistentes y reproducibles en las consultas analíticas.
