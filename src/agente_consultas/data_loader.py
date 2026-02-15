"""Carga y preprocesamiento de datos CSV."""

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger("agente_consultas")


class DataLoader:
    """Clase para manejar la carga y preprocesamiento de datos."""

    @staticmethod
    def load_data(file_path: str) -> pd.DataFrame:
        """Carga datos desde un archivo CSV con validación robusta.

        Args:
            file_path: Ruta al archivo CSV.

        Returns:
            DataFrame preprocesado.

        Raises:
            FileNotFoundError: Si el archivo no existe.
            pd.errors.EmptyDataError: Si el archivo está vacío.
        """
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"Archivo {file_path} no encontrado en {Path.cwd()}")

        try:
            df = pd.read_csv(path)
            logger.info(
                "Archivo cargado exitosamente: %d filas, %d columnas",
                len(df),
                len(df.columns),
            )

            if df.empty:
                raise pd.errors.EmptyDataError("El archivo CSV está vacío")

            return DataLoader._preprocess_dataframe(df)

        except pd.errors.EmptyDataError:
            raise
        except Exception as e:
            logger.error("Error al cargar CSV: %s", e)
            raise RuntimeError(f"Error al cargar o procesar el archivo CSV: {e}") from e

    @staticmethod
    def _preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Preprocesa el DataFrame detectando automáticamente tipos de datos."""
        df_processed = df.copy()

        date_columns = DataLoader._detect_date_columns(df_processed)
        for col in date_columns:
            df_processed[col] = pd.to_datetime(df_processed[col], errors="coerce")
            logger.info("Columna '%s' convertida a datetime", col)

        numeric_columns = DataLoader._detect_numeric_columns(df_processed)
        for col in numeric_columns:
            df_processed[col] = pd.to_numeric(df_processed[col], errors="coerce")
            keywords = ("venta", "cantidad", "precio", "total", "amount", "sales")
            if any(keyword in col.lower() for keyword in keywords):
                df_processed[col] = df_processed[col].fillna(0)
            logger.info("Columna '%s' convertida a numérica", col)

        df_processed = df_processed.dropna(how="all")
        logger.info("Preprocesamiento completado: %d filas restantes", len(df_processed))
        return df_processed

    @staticmethod
    def _detect_date_columns(df: pd.DataFrame) -> list[str]:
        """Detecta columnas que probablemente contienen fechas."""
        date_keywords = ("fecha", "date", "time", "dia", "mes", "año", "year", "month", "day")
        date_columns: list[str] = []

        for col in df.columns:
            if any(keyword in col.lower() for keyword in date_keywords):
                sample = df[col].dropna().head(100)
                if not sample.empty:
                    try:
                        pd.to_datetime(sample, errors="coerce")
                        date_columns.append(col)
                    except (ValueError, TypeError):
                        pass

        return date_columns

    @staticmethod
    def _detect_numeric_columns(df: pd.DataFrame) -> list[str]:
        """Detecta columnas que deberían ser numéricas."""
        numeric_columns: list[str] = []

        for col in df.columns:
            if pd.api.types.is_string_dtype(df[col]):
                sample = df[col].dropna().head(100)
                if not sample.empty:
                    try:
                        pd.to_numeric(sample, errors="raise")
                        numeric_columns.append(col)
                    except (ValueError, TypeError):
                        pass

        return numeric_columns
