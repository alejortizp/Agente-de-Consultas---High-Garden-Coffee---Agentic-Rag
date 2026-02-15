"""Configuración centralizada del agente de datos."""

import logging
from dataclasses import dataclass, field
from pathlib import Path


def setup_logging(log_file: str = "data_agent.log") -> logging.Logger:
    """Configura y retorna el logger principal."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler(),
        ],
    )
    return logging.getLogger("agente_consultas")


logger = setup_logging()


@dataclass
class Config:
    """Configuración centralizada del agente de datos."""

    csv_file: str = "coffee_final.csv"
    model: str = "gpt-4o"
    temperature: float = 0.0
    output_dir: str = "plots"
    max_rows_display: int = 10000
    figure_size: tuple[int, int] = (12, 8)
    supported_plot_types: list[str] = field(
        default_factory=lambda: ["line", "bar", "scatter", "histogram", "boxplot"]
    )
    allow_dangerous_code: bool = True

    def __post_init__(self) -> None:
        """Crea el directorio de salida si no existe."""
        Path(self.output_dir).mkdir(exist_ok=True)
