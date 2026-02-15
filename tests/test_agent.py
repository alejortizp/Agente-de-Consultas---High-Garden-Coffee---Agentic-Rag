"""Tests para el módulo del agente."""

from unittest.mock import MagicMock, patch

import pytest

from agente_consultas.agent import DataAgent, PlotToolInput


class TestPlotToolInput:
    def test_defaults(self):
        schema = PlotToolInput()
        assert schema.plot_type == "line"
        assert schema.x_col == ""
        assert schema.y_col == ""
        assert schema.hue_col is None
        assert schema.title == "Análisis de Datos"
        assert schema.filters is None

    def test_custom_values(self):
        schema = PlotToolInput(plot_type="bar", x_col="Country", y_col="Ventas", title="Custom")
        assert schema.plot_type == "bar"
        assert schema.x_col == "Country"


class TestDataAgent:
    def test_init_without_api_key(self, config, monkeypatch):
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        with pytest.raises(ValueError, match="OPENAI_API_KEY"):
            DataAgent(config)

    @patch("agente_consultas.agent.ChatOpenAI")
    def test_init_with_api_key(self, mock_llm, config, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        agent = DataAgent(config)
        assert agent.df is None
        assert agent.agent is None
        mock_llm.assert_called_once()

    @patch("agente_consultas.agent.create_pandas_dataframe_agent")
    @patch("agente_consultas.agent.ChatOpenAI")
    def test_load_data(self, mock_llm, mock_create_agent, config, sample_csv, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        agent = DataAgent(config)
        agent.load_data(sample_csv)
        assert agent.df is not None
        assert len(agent.df) == 4
        assert agent.plot_generator is not None
        mock_create_agent.assert_called_once()

    @patch("agente_consultas.agent.create_pandas_dataframe_agent")
    @patch("agente_consultas.agent.ChatOpenAI")
    def test_query(self, mock_llm, mock_create_agent, config, sample_csv, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        mock_agent_instance = MagicMock()
        mock_agent_instance.invoke.return_value = {"output": "Las ventas totales son 700"}
        mock_create_agent.return_value = mock_agent_instance

        agent = DataAgent(config)
        agent.load_data(sample_csv)
        result = agent.query("Cuáles son las ventas totales?")
        assert "ventas totales" in result.lower()

    @patch("agente_consultas.agent.create_pandas_dataframe_agent")
    @patch("agente_consultas.agent.ChatOpenAI")
    def test_get_data_summary(self, mock_llm, mock_create_agent, config, sample_csv, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        agent = DataAgent(config)
        agent.load_data(sample_csv)
        summary = agent.get_data_summary()
        assert "RESUMEN DEL DATASET" in summary
        assert "4" in summary

    @patch("agente_consultas.agent.ChatOpenAI")
    def test_get_data_summary_no_data(self, mock_llm, config, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        agent = DataAgent(config)
        assert agent.get_data_summary() == "No hay datos cargados"

    def test_query_without_agent(self, config, monkeypatch):
        monkeypatch.setenv("OPENAI_API_KEY", "test-key")
        with patch("agente_consultas.agent.ChatOpenAI"):
            agent = DataAgent(config)
            result = agent.query("test")
            assert "no inicializado" in result.lower()
