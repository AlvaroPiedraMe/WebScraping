import logging
from src.scraping.playwright_scraper import WallapopScraper

# Configuración básica del logger para la aplicación
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_wallapop_scraper():
    """
    Función principal para ejecutar el scraper de Wallapop.
    """
    logger.info("Iniciando la aplicación de scraping de Wallapop...")

    # Instancia de tu scraper
    # La base_url y los parámetros de búsqueda/ubicación están ya predefinidos en la clase
    # pero puedes pasarlos aquí si quieres hacerlos configurables desde main.py
    scraper = WallapopScraper()

    try:
        # Llama al metodo que ejecuta la secuencia de scraping
        # Los valores por defecto de "Furgonetas" y "Gijon" se usarán si no se pasan
        # Si quieres cambiarlos, puedes hacerlo aquí:
        # scraped_data = scraper.scrape_furgonetas_gijon(item_name="Coches", location="Madrid")
        scraped_data = scraper.scrape_furgonetas_gijon()

        logger.info("Scraping de Wallapop completado.")

        # Imprimir los resultados
        if scraped_data and not any("error" in res for res in scraped_data):
            print("\n--- RESUMEN DE RESULTADOS DE WALLAPOP ---")
            print(f"Número total de anuncios encontrados: {len(scraped_data)}")
            print("\nPrimeros 10 títulos de anuncios:")
            for i, item in enumerate(scraped_data[:10]):
                print(f"  {i + 1}. {item['title']}")
            if len(scraped_data) > 10:
                print(f"  ...y {len(scraped_data) - 10} más.")
        else:
            print("\n--- NO SE PUDIERON OBTENER RESULTADOS ---")
            if scraped_data and any("error" in res for res in scraped_data):
                for res in scraped_data:
                    if "error" in res:
                        print(f"Error detallado: {res['error']}")
            else:
                print("No se encontraron anuncios o hubo un problema desconocido.")

    except Exception as e:
        logger.critical(f"La aplicación de scraping de Wallapop falló con un error crítico: {e}", exc_info=True)
    finally:
        logger.info("Aplicación de scraping de Wallapop finalizada.")


if __name__ == "__main__":
    run_wallapop_scraper()
