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

    def scrape_furgonetas_gijon(self, item_name: str = "Furgonetas", location: str = "Gijon"):
        """
        Navega a Wallapop, realiza la secuencia de acciones generada por codegen:
        acepta cookies, selecciona categoría 'Coches', busca 'Furgonetas' y filtra por 'Gijón'.
        """
        scraped_results = []

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


                # Filtrar por Ubicación
                logger.info("Haciendo clic en el botón 'Cambiar' ubicación.")
                change_location_button = page.get_by_role("button", name="Cambiar")
                expect(change_location_button).to_be_visible(timeout=10000)
                change_location_button.click()
                time.sleep(1)

                logger.info("Haciendo clic en el campo de búsqueda de ubicación.")
                location_searchbox = page.get_by_role("searchbox", name="¿Dónde?")
                expect(location_searchbox).to_be_visible(timeout=5000)
                location_searchbox.click()

                logger.info(f"Escribiendo '{location}' en el campo de ubicación.")
                location_searchbox.fill(location)

                logger.info(f"Seleccionando 'Gijón, Asturias, Principado de Asturias, ESP'.")
                page.get_by_text("Gijón, Asturias, Principado de Asturias, ESP", exact=True).click()
                time.sleep(1)

                logger.info("Haciendo clic en el botón 'Aplicar' filtro de ubicación.")
                page.get_by_role("button", name="Aplicar").click()

                time.sleep(3)

                # --- Extraer la información de los anuncios ---
                logger.info("Extrayendo detalles de los anuncios...")

                # Selector del contenedor de cada anuncio individual
                # Usamos el <a> que es el contenedor principal del HTML proporcionado
                ad_containers_selector = 'a.item-card_ItemCard--horizontal__zLpZu'

                try:
                    # Espera a que al menos UN elemento que coincida con el selector sea visible
                    page.wait_for_selector(ad_containers_selector, state='visible', timeout=20000)
                    logger.info("Al menos un anuncio visible, procediendo a extraer todos.")
                except Exception as e:
                    logger.warning(
                        f"No se encontraron anuncios visibles con el selector '{ad_containers_selector}' después de 20s. Continuando, pero la lista de anuncios puede estar vacía. Error: {e}")
                    # Si no hay anuncios visibles, ad_elements será una lista vacía, y el bucle for no se ejecutará.
                    # Esto es un comportamiento deseado si no hay resultados.

                ad_elements = page.locator(ad_containers_selector).all()
                logger.info(f"Encontrados {len(ad_elements)} elementos con el selector '{ad_containers_selector}'.")

                for i, ad_element in enumerate(ad_elements):
                    try:
                        # Extraer la URL del anuncio (del atributo href del contenedor principal <a>)
                        ad_url_suffix = ad_element.get_attribute('href')
                        full_ad_url = f"https://es.wallapop.com{ad_url_suffix}" if ad_url_suffix else "N/A"

                        # Extraer título
                        # Selector: h3.item-card_ItemCard__title__8eq2b
                        title_element = ad_element.locator('h3.item-card_ItemCard__title__8eq2b')
                        title = title_element.text_content().strip() if title_element else "N/A"

                        # Extraer precio
                        # Selector: strong.item-card_ItemCard__price__D3QWU
                        price_element = ad_element.locator('strong.item-card_ItemCard__price__D3QWU')
                        price = price_element.text_content().strip().replace('\xa0€',
                                                                             ' €') if price_element else "N/A"  # Reemplazar el espacio no-breaking por uno normal

                        # Extraer atributos (año, km, etc.)
                        # Selector: label.item-card_ItemCard__attributes__YhG0G
                        attributes_element = ad_element.locator('label.item-card_ItemCard__attributes__YhG0G')
                        attributes = attributes_element.text_content().strip() if attributes_element else "N/A"

                        # Extraer descripción
                        # Selector: p.item-card_ItemCard__description__qBkRh
                        description_element = ad_element.locator('p.item-card_ItemCard__description__qBkRh')
                        description = description_element.text_content().strip() if description_element else "N/A"

                        # (Opcional) Puedes parsear los atributos aquí mismo si quieres:
                        year = km = fuel = cv = "N/A"
                        if attributes != "N/A":
                            attr_parts = attributes.split('·')
                            if len(attr_parts) > 0: year = attr_parts[0].strip()
                            if len(attr_parts) > 1: km = attr_parts[1].strip()
                            if len(attr_parts) > 2: fuel = attr_parts[2].strip()
                            if len(attr_parts) > 3: cv = attr_parts[3].strip()

                        scraped_results.append({
                            "title": title,
                            "price": price,
                            "url": full_ad_url,
                            "attributes": attributes,  # O los campos parseados individualmente
                            "year": year,
                            "km": km,
                            "fuel": fuel,
                            "cv": cv,
                            "description": description
                        })
                        logger.debug(f"Anuncio {i + 1} extraído: {title}, {price}, {full_ad_url}")

                    except Exception as e:
                        logger.warning(f"Error al extraer datos del anuncio {i + 1}: {e}", exc_info=True)
                        scraped_results.append({"error": f"Error en anuncio {i + 1}: {e}"})

                logger.info(f"Total de anuncios procesados: {len(scraped_results)}")

            except Exception as e:
                logger.critical(f"Fallo crítico durante el scraping de Wallapop: {e}", exc_info=True)
                scraped_results = [{"error": f"Fallo crítico: {e}"}]
            finally:
                if browser:
                    browser.close()
                    logger.info("Navegador cerrado.")

        return scraped_results


# Este bloque se ejecuta solo si el script se corre directamente
if __name__ == "__main__":
    print("--- Iniciando Wallapop Scraper con Búsqueda y Ubicación ---")
    scraper = WallapopScraper()  # La URL base ya está definida en el constructor

    item_to_search = "Furgonetas"
    # El texto de la ubicación debe coincidir con el texto exacto que Playwright buscará en la UI
    location_to_filter = "Gijon"  # Se usará para escribir en el campo

    results = scraper.scrape_furgonetas_gijon(item_name=item_to_search, location=location_to_filter)

    if results and not any("error" in res for res in results):  # Comprueba si hay errores en cualquier resultado
        print(f"\n--- Resultados de búsqueda para '{item_to_search}' en '{location_to_filter}' ---")
        for i, item in enumerate(results):
            print(f"{i + 1}. Título: {item['title']}")
        print(f"\nSe encontraron {len(results)} anuncios.")
    else:
        print(f"\n--- No se pudieron obtener resultados para '{item_to_search}' en '{location_to_filter}' ---")
        if results and any("error" in res for res in results):
            for res in results:
                if "error" in res:
                    print(f"Error: {res['error']}")