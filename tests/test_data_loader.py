"""Tests para el módulo de carga de datos."""

import pandas as pd
import pytest

from agente_consultas.data_loader import DataLoader


class TestDataLoader:
    def test_load_data_success(self, sample_csv):
        df = DataLoader.load_data(sample_csv)
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 4
        assert "Fecha" in df.columns

    def test_load_data_file_not_found(self):
        with pytest.raises(FileNotFoundError, match="no encontrado"):
            DataLoader.load_data("archivo_inexistente.csv")

    def test_load_data_empty_csv(self, tmp_path):
        empty_csv = tmp_path / "empty.csv"
        empty_csv.write_text("col1,col2\n")
        with pytest.raises(pd.errors.EmptyDataError):
            DataLoader.load_data(str(empty_csv))

    def test_detect_date_columns(self, sample_df):
        date_cols = DataLoader._detect_date_columns(sample_df)
        assert "Fecha" in date_cols

    def test_detect_numeric_columns_from_strings(self):
        # Forzar dtype object para simular columnas string con valores numéricos
        df = pd.DataFrame({
            "valor": pd.array(["1", "2", "3"], dtype="object"),
            "texto": ["a", "b", "c"],
        })
        numeric_cols = DataLoader._detect_numeric_columns(df)
        assert "valor" in numeric_cols
        assert "texto" not in numeric_cols

    def test_fillna_on_ventas_column(self, sample_csv):
        result = DataLoader.load_data(sample_csv)
        # Ventas ya viene como numérica, verificar que no tiene NaN
        assert result["Ventas"].isna().sum() == 0
