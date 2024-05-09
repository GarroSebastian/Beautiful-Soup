import sys
from PyQt5.QtCore import QUrl
from PyQt5.QtWebEngineWidgets import QWebEnginePage
from PyQt5.QtWidgets import QApplication
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import csv
from time import sleep

# Configura el webdriver
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_argument('--disable-extensions')
options.add_argument('--disable-gpu')
options.add_argument('--disable-dev-shm-usage')
options.add_argument('--no-sandbox')
driver = webdriver.Chrome(options=options)

class WebEngineClient(QWebEnginePage):
    def __init__(self, url):
        self.app = QApplication(sys.argv)
        super().__init__()
        self.html = ''
        self.loadFinished.connect(self.on_page_load)
        self.load(QUrl(url))
        self.app.exec_()

    def on_page_load(self):
        sleep(10)
        self.toHtml(self._store_html)
    
    def _store_html(self, html):
        self.html = html
        self.app.quit()

# Función para hacer clic en el botón "Mostrar más comentarios"
def click_show_more_reviews_button():
    while True:
        try:
            # Espera a que el botón "Mostrar más comentarios" esté presente
            load_more_button = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'button.bv-content-btn-pages-load-more'))
            )
            # Haz clic en el botón
            load_more_button.click()
            # Espera unos segundos para permitir que cargue más reseñas
            sleep(5)
        except Exception:
            # Rompe el bucle si el botón no está presente (ya no hay más comentarios)
            break

# Función para extraer reseñas de un enlace de producto
def extract_reviews_from_product_page(url):
    try:
        driver.get(url)
        sleep(10)  # Espera unos segundos para cargar la página completamente

        # Haz clic en el botón "Mostrar más comentarios" hasta que desaparezca
        click_show_more_reviews_button()

        # Obtén el HTML de la página con Selenium
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Extrae la información relevante del producto
        title = soup.find('h1').text.strip() if soup.find('h1') else 'Desconocido'
        brand = soup.find('span', {'class': 'jsx-2175409722 product-brand'}).text.strip() if soup.find('span', {'class': 'jsx-2175409722 product-brand'}) else 'Desconocida'
        model = soup.find('span', {'class': 'jsx-2175409722 product-model'}).text.strip() if soup.find('span', {'class': 'jsx-2175409722 product-model'}) else 'Desconocido'

        # Extrae las reseñas
        reviews = []
        review_items = soup.find_all('li', {'class': 'bv-content-item'})
        for item in review_items:
            rating = item.find('abbr', {'class': 'bv-rating bv-rating-stars bv-rating-stars-off'})['title'] if item.find('abbr', {'class': 'bv-rating bv-rating-stars bv-rating-stars-off'}) else 'Sin calificación'
            date = item.find('span', {'class': 'bv-content-datetime-stamp'}).text.strip() if item.find('span', {'class': 'bv-content-datetime-stamp'}) else 'Sin fecha'
            text = item.find('p').text.strip() if item.find('p') else 'Sin texto'

            reviews.append({
                'Producto': title,
                'Marca': brand,
                'Modelo': model,
                'Calificación': rating,
                'Fecha': date,
                'Texto': text
            })

        return reviews

    except Exception as e:
        print(f"No se encontraron reseñas en {url} o ocurrió un error: {e}")
        return []  # Devuelve una lista vacía para evitar errores

# URL principal de Falabella donde se listan los productos
url = 'https://www.falabella.com.pe/falabella-pe/category/cat760706/Celulares-y-Telefonos'
client_response = WebEngineClient(url)
source = client_response.html

# Analiza el HTML con BeautifulSoup para extraer los enlaces de producto
soup = BeautifulSoup(source, 'html.parser')
product_divs = soup.find_all('div', {'class': 'jsx-1484439449 search-results-2-grid grid-pod'})
product_links = []
for div in product_divs:
    a_tag = div.find('a', {'role': 'button'})
    if a_tag:
        product_links.append(a_tag['href'])

# Recopila todas las reseñas de cada producto
all_reviews = []
for link in product_links:
    full_url = link  # Asegúrate de usar la URL completa
    reviews = extract_reviews_from_product_page(full_url)
    all_reviews.extend(reviews)

# Guarda las reseñas en un archivo CSV
if all_reviews:
    keys = all_reviews[0].keys()
    with open('reseñas_falabella.csv', 'w', newline='', encoding='utf-8', errors='replace') as file:
        dict_writer = csv.DictWriter(file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(all_reviews)

print(f"Se han guardado {len(all_reviews)} reseñas en 'reseñas_falabella.csv'.")

# Cierra el navegador
driver.quit()
