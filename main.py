import logging
from src.scraping.playwright_scraper import WallapopScraper

# Configuración básica del logger para la aplicación
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_wallapop_scraper():
    """
    Función principal para ejecutar el scraper de Wallapop, buscando siempre en España.
    """
    logger.info("Iniciando la aplicación de scraping de Wallapop...")

    scraper = WallapopScraper()

    try:
        item_to_search = "Furgonetas"
        # Ahora la función asume que la búsqueda es en España, no se necesita pasar 'location'
        # scraped_data ahora será una lista de tuplas (título, url)
        scraped_data = scraper.scrape_furgonetas_espana(item_name=item_to_search)

        logger.info("Scraping de Wallapop completado.")

        # --- CAMBIOS CRÍTICOS AQUÍ PARA MANEJAR LAS TUPLAS ---
        # El any() también debe ser ajustado si los errores vienen como tuplas ("Error crítico", "mensaje")
        if scraped_data and not any("Error" in t for t, u in scraped_data):
            print(f"\n--- RESUMEN DE RESULTADOS DE WALLAPOP para '{item_to_search}' en TODA ESPAÑA ---")
            # El conteo ahora es de tuplas (títulos/URLs)
            print(f"Número total de anuncios encontrados: {len(scraped_data)}")
            print("\nPrimeros 10 títulos y URLs:")
            # Aquí es donde se desempaqueta la tupla (title, url)
            for i, (title, url) in enumerate(scraped_data[:10]):
                print(f"  {i + 1}. Título: {title}")
                print(f"     URL: {url}") # También puedes imprimir la URL aquí si lo deseas
            if len(scraped_data) > 10:
                print(f"  ...y {len(scraped_data) - 10} más.")
        else:
            print("\n--- NO SE PUDIERON OBTENER RESULTADOS ---")
            # Ajuste en la lógica de errores para tuplas si se devuelve ("Error crítico", "mensaje")
            if scraped_data and any("Error" in t for t, u in scraped_data):
                for t_or_err, u_or_msg in scraped_data: # Desempaqueta también aquí
                    if "Error" in t_or_err:
                        print(f"Error detallado: {u_or_msg}") # El mensaje de error estará en la segunda parte de la tupla
            else:
                print("No se encontraron anuncios o hubo un problema desconocido.")

    except Exception as e:
        logger.critical(f"La aplicación de scraping de Wallapop falló con un error crítico: {e}", exc_info=True)
    finally:
        logger.info("Aplicación de scraping de Wallapop finalizada.")


if __name__ == "__main__":
    run_wallapop_scraper()