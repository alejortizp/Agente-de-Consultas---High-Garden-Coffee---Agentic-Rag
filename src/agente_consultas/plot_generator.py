"""Generación de visualizaciones matplotlib/seaborn."""

import json
import logging
from datetime import datetime
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns

from agente_consultas.config import Config

logger = logging.getLogger("agente_consultas")


class PlotGenerator:
    """Genera y guarda visualizaciones a partir de un DataFrame."""

    def __init__(self, config: Config, df: pd.DataFrame) -> None:
        self.config = config
        self.df = df

    def create_and_save_plot(
        self,
        plot_type: str = "line",
        x_col: str = "",
        y_col: str = "",
        hue_col: str | None = None,
        title: str = "Análisis de Datos",
        filters: dict[str, str | list[str]] | None = None,
    ) -> str:
        """Genera y guarda una gráfica de los datos del DataFrame.

        Args:
            plot_type: Tipo de gráfica ('line', 'bar', 'scatter', 'histogram', 'boxplot').
            x_col: Columna para el eje X.
            y_col: Columna para el eje Y.
            hue_col: Columna para diferenciar series.
            title: Título de la gráfica.
            filters: Filtros a aplicar (dict con columna: valor/lista_valores).

        Returns:
            Mensaje de éxito o error.
        """
        if self.df is None:
            return "Error: DataFrame no cargado. No se puede generar la gráfica."

        if plot_type not in self.config.supported_plot_types:
            return (
                f"Error: Tipo de gráfica '{plot_type}' no soportado. "
                f"Tipos disponibles: {', '.join(self.config.supported_plot_types)}"
            )

        try:
            df_filtered = self._apply_filters(self.df.copy(), filters or {})

            if df_filtered.empty:
                return "No hay datos para graficar después de aplicar los filtros."

            x_col, y_col = self._auto_detect_columns(df_filtered, x_col, y_col, plot_type)

            validation_result = self._validate_columns(df_filtered, x_col, y_col, hue_col)
            if validation_result != "OK":
                return validation_result

            return self._generate_plot(df_filtered, plot_type, x_col, y_col, hue_col, title)

        except Exception as e:
            logger.error("Error en create_and_save_plot: %s", e)
            return f"Error al generar la gráfica: {e}"

    def _apply_filters(
        self, df: pd.DataFrame, filters: dict[str, str | list[str]] | str
    ) -> pd.DataFrame:
        """Aplica filtros al DataFrame."""
        if not filters:
            return df

        if isinstance(filters, str):
            try:
                filters = json.loads(filters)
            except json.JSONDecodeError:
                logger.warning("No se pudo parsear filters como JSON: %s", filters)
                return df

        for col, val in filters.items():
            if col not in df.columns:
                logger.warning("Columna de filtro '%s' no encontrada", col)
                continue

            if isinstance(val, list):
                df = df[df[col].isin(val)]
            elif pd.api.types.is_string_dtype(df[col]):
                df = df[df[col].str.contains(str(val), case=False, na=False)]
            else:
                df = df[df[col] == val]

        return df

    def _auto_detect_columns(
        self, df: pd.DataFrame, x_col: str, y_col: str, plot_type: str
    ) -> tuple[str, str]:
        """Auto-detecta columnas apropiadas si no se especifican."""
        if not x_col:
            date_cols = [col for col in df.columns if df[col].dtype.name.startswith("datetime")]
            if date_cols:
                x_col = date_cols[0]
            else:
                categorical_cols = [col for col in df.columns if df[col].dtype == "object"]
                x_col = categorical_cols[0] if categorical_cols else df.columns[0]

        if not y_col and plot_type != "histogram":
            numeric_cols = [
                col for col in df.columns if pd.api.types.is_numeric_dtype(df[col]) and col != x_col
            ]
            if numeric_cols:
                priority_keywords = ("venta", "cantidad", "precio", "total", "sales", "amount")
                for keyword in priority_keywords:
                    priority_cols = [col for col in numeric_cols if keyword in col.lower()]
                    if priority_cols:
                        y_col = priority_cols[0]
                        break
                if not y_col:
                    y_col = numeric_cols[0]

        return x_col, y_col

    def _validate_columns(
        self, df: pd.DataFrame, x_col: str, y_col: str, hue_col: str | None
    ) -> str:
        """Valida que las columnas existan y sean apropiadas."""
        required_cols = [col for col in [x_col, y_col, hue_col] if col]
        missing_cols = [col for col in required_cols if col not in df.columns]

        if missing_cols:
            return (
                f"Error: Columnas no encontradas: {missing_cols}. "
                f"Columnas disponibles: {list(df.columns)}"
            )
        return "OK"

    def _generate_plot(
        self,
        df: pd.DataFrame,
        plot_type: str,
        x_col: str,
        y_col: str,
        hue_col: str | None,
        title: str,
    ) -> str:
        """Genera la gráfica específica."""
        plt.figure(figsize=self.config.figure_size)

        try:
            if plot_type == "line":
                sns.lineplot(data=df, x=x_col, y=y_col, hue=hue_col)
            elif plot_type == "bar":
                if hue_col:
                    sns.barplot(
                        data=df, x=x_col, y=y_col, hue=hue_col, estimator="sum", errorbar=None
                    )
                else:
                    grouped_data = df.groupby(x_col)[y_col].sum().reset_index()
                    sns.barplot(data=grouped_data, x=x_col, y=y_col)
            elif plot_type == "scatter":
                sns.scatterplot(data=df, x=x_col, y=y_col, hue=hue_col)
            elif plot_type == "histogram":
                plt.hist(df[x_col].dropna(), bins=30, alpha=0.7)
                plt.xlabel(x_col)
                plt.ylabel("Frecuencia")
            elif plot_type == "boxplot":
                sns.boxplot(data=df, x=x_col, y=y_col, hue=hue_col)

            plt.title(title)
            if plot_type != "histogram":
                plt.xlabel(x_col)
                plt.ylabel(y_col)

            if df[x_col].nunique() > 10 or any(len(str(x)) > 10 for x in df[x_col].unique()[:10]):
                plt.xticks(rotation=45, ha="right")

            plt.tight_layout()

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_title = "".join(c for c in title if c.isalnum() or c in (" ", "_")).replace(
                " ", "_"
            )[:50]
            file_name = f"{plot_type}_{safe_title}_{timestamp}.png"
            file_path = Path(self.config.output_dir) / file_name

            plt.savefig(file_path, format="png", bbox_inches="tight", dpi=300)
            plt.close()

            logger.info("Gráfica guardada: %s", file_path)
            return f"Gráfica {plot_type} guardada exitosamente en: {file_path}"

        except Exception as e:
            plt.close()
            logger.error("Error al generar gráfica: %s", e)
            return f"Error al generar la gráfica: {e}"
