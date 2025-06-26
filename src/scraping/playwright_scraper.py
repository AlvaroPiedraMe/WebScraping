# src/scraping/playwright_scraper.py
from playwright.sync_api import sync_playwright, Page, expect
import logging
import time  # Para pausas (útil para depuración y simular comportamiento humano)
import re  # Necesario por si Playwright genera expresiones regulares o para uso futuro

# Configuración básica del logger
logger = logging.getLogger(__name__)
# Evita configurar handlers múltiples veces si el módulo se importa varias veces
if not logger.handlers:
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')


class WallapopScraper:
    """
    Clase para realizar scraping en Wallapop, simulando una búsqueda y aplicando filtros.
    """

    def __init__(self, base_url: str = "https://es.wallapop.com/"):
        self.base_url = base_url
        logger.info(f"Scraper inicializado para: {self.base_url}")

    def _navigate_to_url(self, page: Page, url: str):
        """Metodo privado para navegar a una URL y esperar a la carga."""
        try:
            logger.info(f"Navegando a: {url}")
            page.goto(url)
            page.wait_for_load_state('domcontentloaded')
            logger.info(f"Página cargada: {page.url}")
            time.sleep(1)  # Pausa para asegurar el renderizado inicial
        except Exception as e:
            logger.error(f"Error al navegar a {url}: {e}", exc_info=True)
            raise

    def scrape_furgonetas_espana(self, item_name: str = "Furgonetas"):
        """
        Navega a Wallapop, realiza la secuencia de acciones generada por codegen:
        acepta cookies, selecciona categoría 'Coches', busca 'Furgonetas' y filtra por 'Gijón'.
        """
        # Esta lista almacenará solo las tuplas (título, URL)
        titles_and_urls = []

        with sync_playwright() as p:
            browser = None
            try:
                browser = p.chromium.launch(headless=False)
                page = browser.new_page()


                self._navigate_to_url(page, self.base_url)


                logger.info("Aceptando cookies...")
                page.get_by_role("button", name="Aceptar todo").click()
                time.sleep(1)  # Pequeña pausa despues de clic


                logger.info("Haciendo clic en 'Todas las categorías'.")
                page.get_by_role("button", name="Todas las categorías").click()
                time.sleep(1)  # Pausa para que el menú de categorías se abra

                logger.info("Seleccionando la categoría 'Coches'.")
                page.get_by_role("navigation", name="All Categories").get_by_label("Coches").click()
                time.sleep(4)  # Pausa para que la página se estabilice


                logger.info("Haciendo clic en el campo de búsqueda.")
                expect(page.locator("#searchbox-form-input")).to_be_visible(timeout=10000)
                page.locator("#searchbox-form-input").click()

                logger.info(f"Escribiendo '{item_name}' en el campo de búsqueda.")
                page.locator("#searchbox-form-input").fill(item_name)

                logger.info("Presionando Enter para iniciar la búsqueda.")
                page.locator("#searchbox-form-input").press("Enter")

                #page.wait_for_url(re.compile(r"furgonetas"))  # Espera una URL que contenga "furgonetas"
                time.sleep(4)


                # --- Logica filtrado de Ubicacion: España ---
                logger.info("Haciendo clic en el botón 'Cambiar' ubicación.")
                change_location_button = page.get_by_role("button", name="Cambiar")
                expect(change_location_button).to_be_visible(timeout=10000)
                change_location_button.click()
                time.sleep(1)

                logger.info("Haciendo clic en el campo de búsqueda de ubicación.")
                location_searchbox = page.get_by_role("searchbox", name="¿Dónde?")
                expect(location_searchbox).to_be_visible(timeout=5000)
                location_searchbox.click()

                logger.info("Configurando la ubicación para 'España'")
                location_searchbox.fill("España")
                # Esperar y hacer clic en la sugerencia "España"
                espana_suggestion = page.get_by_text("España", exact=True)
                expect(espana_suggestion).to_be_visible(timeout=10000)
                espana_suggestion.click()
                time.sleep(1)

                logger.info("Haciendo clic en el botón 'Aplicar' filtro de ubicación.")
                page.get_by_role("button", name="Aplicar").click()
                time.sleep(1)


                # --- Extraer URLs y Títulos de los anuncios de la lista ---
                logger.info("Extrayendo títulos y URLs de los anuncios de la página de lista...")

                ad_containers_selector = 'a.item-card_ItemCard--horizontal__zLpZu'

                try:
                    page.wait_for_selector(ad_containers_selector, state='visible', timeout=20000)
                    logger.info("Al menos un anuncio visible, procediendo a extraer todos.")
                except Exception as e:
                    logger.warning(
                        f"No se encontraron anuncios visibles con el selector '{ad_containers_selector}' después de 20s. La lista de anuncios puede estar vacía. Error: {e}")
                    return []  # Salir si no hay anuncios que procesar.

                ad_elements = page.locator(ad_containers_selector).all()
                logger.info(f"Encontrados {len(ad_elements)} elementos con el selector '{ad_containers_selector}'.")

                # Recolectar solo la tupla (título, URL)
                for i, ad_element in enumerate(ad_elements):
                    try:
                        ad_url_suffix = ad_element.get_attribute('href')
                        # Asegúrate de que la URL sea completa
                        full_ad_url = f"https://es.wallapop.com{ad_url_suffix}" if ad_url_suffix else "N/A"

                        title_element = ad_element.locator('h3.item-card_ItemCard__title__8eq2b')
                        title = title_element.text_content().strip() if title_element else "N/A"

                        # Añadir la tupla (título, URL) a la lista
                        if title != "N/A" and full_ad_url != "N/A":
                            titles_and_urls.append((title, full_ad_url))
                            logger.debug(f"Anuncio {i + 1} extraído: ('{title}', '{full_ad_url}')")
                        else:
                            logger.warning(f"Título o URL no encontrados para el anuncio {i + 1}. Saltando.")

                    except Exception as e:
                        logger.warning(f"Error al extraer título/URL del anuncio {i + 1}: {e}", exc_info=True)

                logger.info(f"Total de títulos y URLs recolectados: {len(titles_and_urls)}")

                # --- FIN DE LA ETAPA 1 ---
                # Se ha eliminado toda la lógica de la ETAPA 2 para la extracción de detalles.

            except Exception as e:
                logger.critical(f"Fallo crítico durante el scraping de Wallapop: {e}", exc_info=True)
                # En caso de fallo crítico, devolver una lista vacía o con un error.
                return [("Error crítico", str(e))]
            finally:
                if browser:
                    browser.close()
                    logger.info("Navegador cerrado.")

        return titles_and_urls


# Este bloque se ejecuta solo si el script se corre directamente
if __name__ == "__main__":
    print("--- Iniciando Wallapop Scraper con Búsqueda en Toda España (Solo Títulos y URLs) ---")
    scraper = WallapopScraper()

    item_to_search = "Furgonetas"

    # ¡CORRECCIÓN AQUÍ! Llamando a la función correcta y sin el parámetro location
    results_list = scraper.scrape_furgonetas_espana(item_name=item_to_search)

    if results_list and not any("Error" in t for t, u in results_list):  # Comprueba si hay errores en las tuplas
        print(f"\n--- Resultados de búsqueda para '{item_to_search}' en TODA ESPAÑA (Títulos y URLs) ---")
        # ¡CORRECCIÓN AQUÍ! Desempaquetando la tupla directamente en el bucle
        for i, (title, url) in enumerate(results_list[:10]):  # Mostrar solo los primeros 10 para un resumen
            print(f"{i + 1}. Título: {title}")
            print(f"   URL: {url}")
        if len(results_list) > 10:
            print(f"\n... (Mostrando los primeros 10 de {len(results_list)} tuplas totales)")
        else:
            print(f"\nSe encontraron {len(results_list)} tuplas de título y URL.")
    else:
        print(f"\n--- No se pudieron obtener resultados para '{item_to_search}' en TODA ESPAÑA ---")
        if results_list and any("Error" in t for t, u in results_list):
            for title_or_error, url_or_message in results_list:
                if "Error" in title_or_error:
                    print(f"Error: {url_or_message}")  # La URL contendrá el mensaje de error en este caso
        else:
            print("No se encontraron anuncios o hubo un problema desconocido.")
