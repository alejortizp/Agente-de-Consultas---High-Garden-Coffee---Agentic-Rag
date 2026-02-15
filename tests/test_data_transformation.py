"""Tests para el módulo de transformación de datos."""

import pandas as pd
import pytest

from data_transformation import transform_coffee_data


class TestTransformCoffeeData:
    @pytest.fixture
    def transformed_df(self, tmp_path):
        """Ejecuta la transformación y retorna el DataFrame resultante."""
        output_path = tmp_path / "test_output.csv"
        return transform_coffee_data(
            input_path="coffee_db.parquet",
            output_path=str(output_path),
        )

    def test_expected_columns(self, transformed_df):
        expected = {"Fecha", "Country", "Ventas", "Coffee type"}
        assert set(transformed_df.columns) == expected

    def test_coffee_type_normalized(self, transformed_df):
        coffee_types = transformed_df["Coffee type"].unique()
        assert "Robusta/Arabica" not in coffee_types
        assert "Arabica/Robusta" not in coffee_types

    def test_has_rows(self, transformed_df):
        assert len(transformed_df) > 0

    def test_output_csv_created(self, tmp_path):
        output_path = tmp_path / "output.csv"
        transform_coffee_data(
            input_path="coffee_db.parquet",
            output_path=str(output_path),
        )
        assert output_path.exists()
        df = pd.read_csv(output_path)
        assert len(df) > 0

    def test_fecha_column_is_datetime(self, transformed_df):
        assert pd.api.types.is_datetime64_any_dtype(transformed_df["Fecha"])
