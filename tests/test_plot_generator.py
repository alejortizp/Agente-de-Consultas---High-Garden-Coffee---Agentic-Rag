"""Tests para el módulo de generación de gráficas."""

from pathlib import Path

from agente_consultas.plot_generator import PlotGenerator


class TestPlotGenerator:
    def test_line_plot(self, config, sample_df):
        gen = PlotGenerator(config, sample_df)
        result = gen.create_and_save_plot(
            plot_type="line", x_col="Fecha", y_col="Ventas", title="Test Line"
        )
        assert "guardada exitosamente" in result
        plots = list(Path(config.output_dir).glob("*.png"))
        assert len(plots) == 1

    def test_invalid_plot_type(self, config, sample_df):
        gen = PlotGenerator(config, sample_df)
        result = gen.create_and_save_plot(plot_type="invalid")
        assert "no soportado" in result

    def test_filters(self, config, sample_df):
        gen = PlotGenerator(config, sample_df)
        result = gen.create_and_save_plot(
            plot_type="bar",
            x_col="Country",
            y_col="Ventas",
            filters={"Country": ["Colombia"]},
            title="Filtered",
        )
        assert "guardada exitosamente" in result

    def test_auto_detect_columns(self, config, sample_df):
        gen = PlotGenerator(config, sample_df)
        result = gen.create_and_save_plot(plot_type="line", title="Auto Detect")
        assert "guardada exitosamente" in result

    def test_histogram(self, config, sample_df):
        gen = PlotGenerator(config, sample_df)
        result = gen.create_and_save_plot(plot_type="histogram", x_col="Ventas", title="Hist Test")
        assert "guardada exitosamente" in result

    def test_missing_column(self, config, sample_df):
        gen = PlotGenerator(config, sample_df)
        result = gen.create_and_save_plot(plot_type="line", x_col="NoExiste", y_col="Ventas")
        assert "no encontradas" in result

    def test_empty_after_filter(self, config, sample_df):
        gen = PlotGenerator(config, sample_df)
        result = gen.create_and_save_plot(
            plot_type="line",
            filters={"Country": ["PaisInexistente"]},
        )
        assert "No hay datos" in result
