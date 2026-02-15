"""Punto de entrada principal del agente de consultas."""

import logging

from dotenv import load_dotenv

from agente_consultas.agent import DataAgent
from agente_consultas.config import Config

logger = logging.getLogger("agente_consultas")


def main() -> None:
    """Función principal - REPL interactivo del agente."""
    load_dotenv()

    try:
        config = Config()

        print("AVISO DE SEGURIDAD:")
        print("   Este agente puede ejecutar código Python para análisis de datos.")
        print("   Solo usa datos de fuentes confiables.")
        print("   En producción, considera usar un entorno sandboxed.\n")

        agent = DataAgent(config)
        agent.load_data()

        print(agent.get_data_summary())

        print("\nAgente de Análisis de Datos listo!")
        print("Puedes hacer preguntas sobre los datos o solicitar visualizaciones")
        print("Ejemplos:")
        print("   - 'Cuáles son las ventas totales por país?'")
        print("   - 'Muestra un gráfico de ventas por mes'")
        print("   - 'Compara las ventas de Colombia y Brasil'")
        print("   - 'Haz un histograma de los precios'")
        print("Escribe 'salir' para terminar\n")

        while True:
            try:
                query = input("Tu consulta: ").strip()

                if query.lower() in ("salir", "exit", "quit"):
                    print("Hasta luego!")
                    break

                if not query:
                    continue

                print("\nProcesando...")
                response = agent.query(query)
                print(f"\nRespuesta:\n{response}")
                print("-" * 50)

            except KeyboardInterrupt:
                print("\nHasta luego!")
                break
            except Exception as e:
                logger.error("Error en el bucle principal: %s", e)
                print(f"Error: {e}")

    except Exception as e:
        logger.error("Error crítico: %s", e)
        print(f"Error crítico: {e}")


if __name__ == "__main__":
    main()
