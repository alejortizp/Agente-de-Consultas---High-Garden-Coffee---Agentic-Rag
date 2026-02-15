"""Agente principal de análisis de datos con LangChain."""

import logging
import os
import warnings

from langchain_core.tools import StructuredTool
from langchain_experimental.agents import create_pandas_dataframe_agent
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from agente_consultas.config import Config
from agente_consultas.data_loader import DataLoader
from agente_consultas.plot_generator import PlotGenerator

warnings.filterwarnings("ignore", category=UserWarning, module="matplotlib")

logger = logging.getLogger("agente_consultas")


class PlotToolInput(BaseModel):
    """Schema Pydantic para la herramienta de generación de gráficas."""

    plot_type: str = Field(
        default="line",
        description="Tipo de gráfica: 'line', 'bar', 'scatter', 'histogram', 'boxplot'",
    )
    x_col: str = Field(default="", description="Columna para el eje X (se auto-detecta si vacío)")
    y_col: str = Field(default="", description="Columna para el eje Y (se auto-detecta si vacío)")
    hue_col: str | None = Field(
        default=None, description="Columna para diferenciar series (opcional)"
    )
    title: str = Field(default="Análisis de Datos", description="Título de la gráfica")
    filters: dict[str, str | list[str]] | None = Field(
        default=None, description="Filtros a aplicar en formato dict (columna: valor)"
    )


class DataAgent:
    """Clase principal del agente de análisis de datos."""

    def __init__(self, config: Config) -> None:
        self.config = config
        self.df = None
        self.agent = None
        self.plot_generator: PlotGenerator | None = None

        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY no está configurada en las variables de entorno")

        self.llm = ChatOpenAI(
            model=self.config.model,
            temperature=self.config.temperature,
        )

        logger.info("DataAgent inicializado correctamente")

    def load_data(self, file_path: str | None = None) -> None:
        """Carga los datos y configura el agente."""
        file_path = file_path or self.config.csv_file

        try:
            self.df = DataLoader.load_data(file_path)
            self.plot_generator = PlotGenerator(self.config, self.df)

            logger.info("Datos cargados: %d filas, %d columnas", len(self.df), len(self.df.columns))
            logger.info("Columnas: %s", list(self.df.columns))

            self._setup_agent()

        except Exception as e:
            logger.error("Error al cargar datos: %s", e)
            raise

    def _setup_agent(self) -> None:
        """Configura el agente de Pandas DataFrame."""
        plot_tool = StructuredTool.from_function(
            func=self.plot_generator.create_and_save_plot,
            name="create_and_save_plot",
            description=(
                "Genera y guarda una gráfica de los datos del DataFrame. "
                "Tipos: 'line', 'bar', 'scatter', 'histogram', 'boxplot'. "
                "Las columnas se auto-detectan si no se especifican."
            ),
            args_schema=PlotToolInput,
        )

        self.agent = create_pandas_dataframe_agent(
            self.llm,
            self.df,
            verbose=True,
            agent_type="tool-calling",
            allow_dangerous_code=self.config.allow_dangerous_code,
            extra_tools=[plot_tool],
            max_iterations=10,
            early_stopping_method="generate",
        )

        logger.info("Agente configurado exitosamente")

    def query(self, question: str) -> str:
        """Procesa una consulta del usuario.

        Args:
            question: Pregunta o solicitud del usuario.

        Returns:
            Respuesta del agente.
        """
        if not self.agent:
            return "Error: Agente no inicializado. Carga los datos primero."

        enhanced_prompt = f"""
        Analiza la siguiente consulta del usuario sobre el dataset.

        Información del dataset:
        - Filas: {len(self.df)}
        - Columnas: {list(self.df.columns)}
        - Tipos de datos: {dict(self.df.dtypes)}

        Si la consulta solicita una visualización (gráfica, gráfico, plot, visualiza, etc.):
        1. Usa la herramienta 'create_and_save_plot'
        2. Infiere los parámetros apropiados basándote en los datos y la consulta
        3. Los tipos de gráfica disponibles son: {", ".join(self.config.supported_plot_types)}

        Consulta del usuario: {question}
        """

        try:
            response = self.agent.invoke({"input": enhanced_prompt})
            return response.get("output", "No se pudo generar respuesta")
        except Exception as e:
            logger.error("Error procesando consulta: %s", e)
            return f"Error al procesar la consulta: {e}"

    def get_data_summary(self) -> str:
        """Retorna un resumen de los datos cargados."""
        if self.df is None:
            return "No hay datos cargados"

        return f"""
        === RESUMEN DEL DATASET ===
        Filas: {len(self.df)}
        Columnas: {len(self.df.columns)}

        Columnas y tipos:
        {self.df.dtypes.to_string()}

        Primeras 5 filas:
        {self.df.head().to_string()}

        Información de valores nulos:
        {self.df.isnull().sum().to_string()}
        """
