"""Fixtures compartidas para el test suite."""

import matplotlib
import pandas as pd
import pytest

from agente_consultas.config import Config

# Usar backend no interactivo para tests
matplotlib.use("Agg")


@pytest.fixture
def sample_df() -> pd.DataFrame:
    """DataFrame de ejemplo con datos de café."""
    return pd.DataFrame(
        {
            "Fecha": pd.to_datetime(["2020-01-01", "2020-02-01", "2020-03-01", "2020-04-01"]),
            "Country": ["Colombia", "Brasil", "Colombia", "Brasil"],
            "Ventas": [100.0, 200.0, 150.0, 250.0],
            "Coffee type": ["Arabica", "Robusta", "Arabica", "Robusta"],
        }
    )


@pytest.fixture
def config(tmp_path) -> Config:
    """Config con directorio temporal para plots."""
    return Config(output_dir=str(tmp_path / "plots"))


@pytest.fixture
def sample_csv(tmp_path, sample_df) -> str:
    """Crea un CSV temporal con datos de ejemplo y retorna la ruta."""
    csv_path = tmp_path / "test_data.csv"
    sample_df.to_csv(csv_path, index=False)
    return str(csv_path)
