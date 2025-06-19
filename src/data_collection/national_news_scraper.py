import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import pandas as pd
import sys
import os

# Setup path
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.append(project_root)
import config

def init_driver():
    service = Service()
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # opsional, headless
    return webdriver.Chrome(service=service, options=options)

def safe_get_text(element):
    return element.get_text(strip=True) if element else ''

def scrape_from_kompas():
    driver = init_driver()
    data = []
    try:
        base_url = config.TARGET_URLS['kompas']['url']
        pagination_format = config.TARGET_URLS['kompas']['pagination_format']

        for page_num in range(1, config.MAX_PAGES_PER_CATEGORY + 1):
            driver.get(f"{base_url}{pagination_format.format(page_num)}")
            time.sleep(config.SLEEP_TIME)
            soup = BeautifulSoup(driver.page_source, 'html.parser')
            articles = soup.find_all('div', class_='article__list clearfix')

            for article in articles:
                title = safe_get_text(article.find('div', class_='article__list__title'))
                link_tag = article.find('a')
                link = link_tag['href'] if link_tag else ''
                tanggal = safe_get_text(article.find('div', class_='article__date'))
                if title and link:
                    data.append({
                        'sumber': 'Kompas.com',
                        'judul': title,
                        'link': link,
                        'tanggal_terbit': tanggal
                    })
    finally:
        driver.quit()
    return pd.DataFrame(data)

def scrape_bola_page(url, driver):
    data = []
    driver.get(url)
    for _ in range(config.MAX_SCROLLS):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(config.SLEEP_TIME)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    articles = soup.select('article.articles--iridescent-list--item')
    for article in articles:
        try:
            link_tag = article.find('a', class_='articles--iridescent-list--text-item__title-link')
            link = link_tag['href'] if link_tag else ''
            title = safe_get_text(link_tag.find('span')) if link_tag else ''
            tanggal = article.find('time')['datetime'] if article.find('time') else ''
            if title and link:
                data.append({
                    'sumber': 'Bola.com',
                    'judul': title,
                    'link': link,
                    'tanggal_terbit': tanggal
                })
        except:
            continue
    return data

def scrape_from_bola():
    driver = init_driver()
    data = []
    try:
        for _, url in config.TARGET_URLS['bola']['categories'].items():
            data.extend(scrape_bola_page(url, driver))
    finally:
        driver.quit()
    return pd.DataFrame(data)

def scrape_detik_category(url, driver):
    data = []
    driver.get(url)
    for _ in range(config.MAX_PAGES_PER_CATEGORY):
        time.sleep(config.SLEEP_TIME)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        articles = soup.select('article.list-content__item')
        for article in articles:
            title = safe_get_text(article.find('h3', class_='media__title'))
            link_tag = article.find('a', class_='media__link')
            link = link_tag['href'] if link_tag else ''
            tanggal = safe_get_text(article.find('div', class_='media__date'))
            if title and link:
                data.append({
                    'sumber': 'Detik.com',
                    'judul': title,
                    'link': link,
                    'tanggal_terbit': tanggal
                })
        try:
            next_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//a[text()='Next']")))
            driver.execute_script("arguments[0].click();", next_btn)
        except:
            break
    return data

def scrape_from_detik():
    driver = init_driver()
    data = []
    try:
        for _, url in config.TARGET_URLS['detik']['categories'].items():
            data.extend(scrape_detik_category(url, driver))
    finally:
        driver.quit()
    return pd.DataFrame(data)

def scrape_template(target_key, sumber_nama):
    driver = init_driver()
    data = []
    try:
        for _, url in config.TARGET_URLS[target_key]['categories'].items():
            driver.get(url)
            next_clicks = 0
            while next_clicks < config.MAX_PAGES_PER_CATEGORY:
                for _ in range(config.MAX_SCROLLS):
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(config.SLEEP_TIME)
                soup = BeautifulSoup(driver.page_source, 'html.parser')
                articles = soup.select('div.newsrow__row')
                for article in articles:
                    title_tag = article.find('h2', class_='newsrow__title')
                    link_tag = title_tag.find('a') if title_tag else None
                    title = safe_get_text(title_tag)
                    link = link_tag['href'] if link_tag else ''
                    tanggal = safe_get_text(article.find('span', class_='date'))
                    if title and link:
                        data.append({
                            'sumber': sumber_nama,
                            'judul': title,
                            'link': link,
                            'tanggal_terbit': tanggal
                        })
                try:
                    next_btn = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.XPATH, "//a[text()='→']")))
                    driver.execute_script("arguments[0].click();", next_btn)
                    time.sleep(config.SLEEP_TIME)
                    next_clicks += 1
                except:
                    break
    finally:
        driver.quit()
    return pd.DataFrame(data)

scrape_from_kemenpora = lambda: scrape_template('kemenpora', 'kemenpora.go.id')
scrape_from_pelayanan = lambda: scrape_template('pelayanan_kemenpora', 'deputi1.kemenpora.go.id')
scrape_from_pembudayaan = lambda: scrape_template('pembudayaan_kemenpora', 'deputi2.kemenpora.go.id')
scrape_from_presor = lambda: scrape_template('presor_kemenpora', 'deputi3.kemenpora.go.id')
scrape_from_indoor = lambda: scrape_template('indoor_kemenpora', 'deputi4.kemenpora.go.id')
