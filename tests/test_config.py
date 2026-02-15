"""Tests para el módulo de configuración."""

from pathlib import Path

from agente_consultas.config import Config


class TestConfig:
    def test_defaults(self):
        config = Config(output_dir="/tmp/test_plots_default")
        assert config.csv_file == "coffee_final.csv"
        assert config.model == "gpt-4o"
        assert config.temperature == 0.0
        assert config.figure_size == (12, 8)
        assert "line" in config.supported_plot_types
        assert config.allow_dangerous_code is True

    def test_creates_output_dir(self, tmp_path):
        output_dir = tmp_path / "new_plots"
        Config(output_dir=str(output_dir))
        assert output_dir.exists()

    def test_custom_values(self, tmp_path):
        config = Config(
            csv_file="custom.csv",
            model="gpt-3.5-turbo",
            temperature=0.5,
            output_dir=str(tmp_path / "custom"),
            figure_size=(10, 6),
        )
        assert config.csv_file == "custom.csv"
        assert config.model == "gpt-3.5-turbo"
        assert config.temperature == 0.5
        assert config.figure_size == (10, 6)
        assert Path(config.output_dir).exists()
