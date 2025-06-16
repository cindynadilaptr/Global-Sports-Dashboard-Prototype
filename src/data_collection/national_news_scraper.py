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
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.append(project_root)
import config 

# Scraping Kompas.com
def scrape_from_kompas():
    print("Mencoba membuka browser...")

    service = Service()
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)
    try:
        sumber_target = config.TARGET_URLS
        kompas_config = sumber_target.get('kompas', {})
        base_url = kompas_config.get('url')
        pagination_format = kompas_config.get('pagination_format')
        MAX_PAGES = config.MAX_PAGES_PER_CATEGORY
    except Exception as e:
        print(f"Error saat membaca config.py: {e}")
        driver.quit()
        return pd.DataFrame() 

    if not base_url:
        print("Error: URL Kompas tidak ditemukan di config.TARGET_URLS.")
        driver.quit()
        return pd.DataFrame()
    

    list_berita_kompas = [] 
    try:
        for page_num in range(1, MAX_PAGES + 1):
            
            url_halaman_ini = f"{base_url}/page/{page_num}"

            print(f"\n--- Scraping Halaman {page_num}: {url_halaman_ini} ---")
            
            driver.get(url_halaman_ini)
            time.sleep(config.SLEEP_TIME) 

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            articles = soup.find_all('div', class_='article__list clearfix') 
            print(f"Ditemukan {len(articles)} wadah berita di halaman ini.")

            if not articles:
                break

            for article in articles:
                try:
                    title_element = article.find('div', class_='article__list__title')
                    
                    if title_element:
                        link_element = title_element.find('a') 
                        
                        if link_element:
                            judul = title_element.get_text(strip=True)
                            link = link_element.get('href')
                        
                            list_berita_kompas.append({
                                'sumber': 'Kompas.com',
                                'judul': judul,
                                'link': link
                            })
                except Exception as e:
                    print(f"Melewati satu artikel karena error: {e}")
                    continue

    except Exception as e:
        print(f"Terjadi error saat proses utama: {e}")
    
    finally:
        print("\nMenutup browser...")
        driver.quit()

    print(f"\nTotal berita yang berhasil dikumpulkan dari semua halaman: {len(list_berita_kompas)}")
    return pd.DataFrame(list_berita_kompas)

# Blok testing langsung
if __name__ == '__main__':
    df_hasil = scrape_from_kompas()
    if not df_hasil.empty:
        print("\n Hasil akhir scraping Kompas.com")
        print(df_hasil)


# Scraping Bola.com
def scrape_bola_page(url: str, driver):

    list_berita_halaman_ini = [] 
    try:
        driver.get(url)
        time.sleep(config.SLEEP_TIME) 

        for i in range(config.MAX_SCROLLS):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            print(f"Scroll ke-{i+1}, menunggu {config.SLEEP_TIME} detik...")
            time.sleep(config.SLEEP_TIME)

        page_source = driver.page_source


        soup = BeautifulSoup(page_source, 'html.parser')

        articles = soup.select('article.articles--iridescent-list--item.articles--iridescent-list--text-item') 
        print(f"Ditemukan {len(articles)} wadah berita di halaman ini.")


        for i, article in enumerate(articles):
            try:
                link_element = article.find('a', class_='articles--iridescent-list--text-item__title-link')
                    
                if link_element:
                    link = link_element.get('href')
                    title_span = link_element.find('span', class_='articles--iridescent-list--text-item__title-link-text')

                    judul = ''

                    if title_span:
                        judul = title_span.get_text(strip=True)
                    else:
                         judul = link_element.get_text(strip=True)

                    if judul and link:
                        list_berita_halaman_ini.append({
                            'sumber': 'bola.com',
                            'judul': judul,
                            'link': link
                        })

            except Exception as e:
                    print(f"Melewati satu artikel karena error: {e}")
                    continue

    except Exception as e:
        print(f"Terjadi error saat proses utama: {e}")
    
    return list_berita_halaman_ini
    
def scrape_from_bola():
    print("Mencoba membuka browser...")

    service = Service()
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    targets = config.TARGET_URLS.get('bola', {}).get('categories', {}) 

    semua_berita_bola = [] 
    try:
        for kategori, url_kategori in targets.items():
            print(f"\n Mengambil kategori: {kategori}")
            hasil_kategori = scrape_bola_page(url_kategori, driver)
            
            if hasil_kategori:
                semua_berita_bola.extend(hasil_kategori)

    except Exception as e:
        print(f"Terjadi error saat proses utama: {e}")

    finally:
        print("\nMenutup browser...")
        driver.quit()
    
    if not semua_berita_bola:
        print("Tidak ada berita yang berhasil dikumpulkan dari Bola.com.")
        return pd.DataFrame()
    
    final_df = pd.DataFrame(semua_berita_bola)
    print(f"\nTotal berita yang berhasil dikumpulkan dari Bola.com: {len(final_df)}")
    return final_df

# Blok testing langsung
if __name__ == '__main__':
    df_bola_hasil = scrape_from_bola()
    if not df_bola_hasil.empty:
        print("\n Hasil akhir scraping Bola.com")
        print(df_bola_hasil)


# Scraping Detik.com
def scrape_detik_category(category_url: str, driver):
    list_berita_kategori = []
    driver.get(category_url)
    
    for page_num in range(config.MAX_PAGES_PER_CATEGORY):
        print(f"\n Memproses Halaman {page_num + 1} di kategori {category_url.split('/')[-1]}")
        
        time.sleep(config.SLEEP_TIME)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        articles = soup.select('article.list-content__item')
        print(f"Ditemukan {len(articles)} wadah berita di halaman ini.")

        for i, article in enumerate(articles):
            try:
                link_element = article.find('a', class_='media__link')
                title_element = article.find('h3', class_='media__title') 
                
                if link_element and title_element:
                    link = link_element.get('href')
                    judul = title_element.get_text(strip=True)
                    
                    if judul and link:
                        list_berita_kategori.append({
                            'sumber': 'Detik.com',
                            'judul': judul,
                            'link': link
                        })
            except Exception as e:
                print(f"Melewati satu artikel karena error: {e}")
                continue

        try:
            xpath_selector = "//a[text()='Next']" 
            WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, xpath_selector)))
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath_selector)))
            
            print("Tombol 'Next' ditemukan. Melakukan klik...")
            driver.execute_script("arguments[0].click();", next_button)

        except Exception:
            print("Tombol 'Next' tidak ditemukan atau tidak bisa diklik. Scraping untuk kategori ini selesai.")
            break

    return list_berita_kategori

def scrape_from_detik():
    print("\n Mencoba membuka browser untuk Detik.com...")
    
    service = Service()
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    targets = config.TARGET_URLS.get('detik', {}).get('categories', {})
    semua_berita_detik = [] 

    try:
        for kategori, url_kategori in targets.items():
            print(f"\n--- Mengambil kategori: {kategori} ---")
            
            hasil_kategori = scrape_detik_category(url_kategori, driver)
            
            if hasil_kategori:
                semua_berita_detik.extend(hasil_kategori)
    except Exception as e:
        print(f"Terjadi error saat proses utama: {e}")
    finally:
        print("\nMenutup browser...")
        driver.quit()
    
    return pd.DataFrame(semua_berita_detik)

# --- Blok Testing Langsung ---
if __name__ == '__main__':
    df_hasil_detik = scrape_from_detik()
    if not df_hasil_detik.empty:
        print("\n Hasil akhir scraping Detik.com")
        print(df_hasil_detik)
    else:
        print("Tidak ada berita yang berhasil dikumpulkan dari Detik.com.")


# Scraping kemenpora.go.id
def scrape_kemenpora_page(url: str, driver):
    list_berita_kategori = []
    driver.get(url)
    
    for page_num in range(config.MAX_PAGES_PER_CATEGORY):
        print(f"\n Memproses Halaman {page_num + 1} di kategori {url.split('/')[-1]}")

    for _ in range(config.MAX_SCROLLS):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")    
        time.sleep(config.SLEEP_TIME)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        articles = soup.select('div.newsrow__row')
        print(f"Ditemukan {len(articles)} wadah berita di halaman ini.")

        for i, article in enumerate(articles):
            try:
                title_element = article.find('h2', class_='newsrow__title')
                    
                if title_element:
                    link_element = title_element.find('a') 
                        
                    if link_element:
                            judul = title_element.get_text(strip=True)
                            link = link_element.get('href')
                    
                    if judul and link:
                        list_berita_kategori.append({
                            'sumber': 'kemenpora.go.id',
                            'judul': judul,
                            'link': link
                        })
            except Exception as e:
                print(f"Melewati satu artikel karena error: {e}")
                continue

        try:
            xpath_selector = "//a[text()='→']" 
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath_selector)))
            
            print("Tombol 'Next' ditemukan. Melakukan klik...")
            driver.execute_script("arguments[0].click();", next_button)

        except Exception:
            print("Tombol 'Next' tidak ditemukan atau tidak bisa diklik. Scraping untuk kategori ini selesai.")
            break

    return list_berita_kategori

def scrape_from_kemenpora():
    print("\n Mencoba membuka browser untuk kemenpora.go.id...")
    
    service = Service()
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    targets = config.TARGET_URLS.get('kemenpora', {}).get('categories', {})
    semua_berita_kemenpora = [] 

    try:
        for kategori, url_kategori in targets.items():
            print(f"\n Mengambil kategori: {kategori}")
            
            hasil_kategori = scrape_kemenpora_page(url_kategori, driver) 
            
            if hasil_kategori:
                semua_berita_kemenpora.extend(hasil_kategori)
    except Exception as e:
        print(f"Terjadi error saat proses utama: {e}")
    finally:
        print("\nMenutup browser...")
        driver.quit()
    
    return pd.DataFrame(semua_berita_kemenpora)

# --- Blok Testing Langsung ---
if __name__ == '__main__':
    df_hasil_indoor = scrape_from_kemenpora()
    if not df_hasil_indoor.empty:
        print("\n Hasil akhir scraping kemenpora.go.id")
        print(df_hasil_indoor)
    else:
        print("Tidak ada berita yang berhasil dikumpulkan dari kemenpora.go.id")

# Scraping deputi1.kemenpora.go.id
def scrape_pelayanan_category(category_url: str, driver):
    list_berita_kategori = []
    driver.get(category_url)
    
    for page_num in range(config.MAX_PAGES_PER_CATEGORY):
        print(f"\n Memproses Halaman {page_num + 1} di kategori {category_url.split('/')[-1]}")

    for _ in range(config.MAX_SCROLLS):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")    
        time.sleep(config.SLEEP_TIME)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        articles = soup.select('div.newsrow__row')
        print(f"Ditemukan {len(articles)} wadah berita di halaman ini.")

        for i, article in enumerate(articles):
            try:
                title_element = article.find('h2', class_='newsrow__title')
                    
                if title_element:
                    link_element = title_element.find('a') 
                        
                    if link_element:
                            judul = title_element.get_text(strip=True)
                            link = link_element.get('href')
                    
                    if judul and link:
                        list_berita_kategori.append({
                            'sumber': 'deputi1.kemenpora.go.id',
                            'judul': judul,
                            'link': link
                        })
            except Exception as e:
                print(f"Melewati satu artikel karena error: {e}")
                continue

        try:
            xpath_selector = "//a[text()='→']" 
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath_selector)))
            
            print("Tombol 'Next' ditemukan. Melakukan klik...")
            driver.execute_script("arguments[0].click();", next_button)

        except Exception:
            print("Tombol 'Next' tidak ditemukan atau tidak bisa diklik. Scraping untuk kategori ini selesai.")
            break

    return list_berita_kategori

def scrape_from_pelayanan():
    print("\n Mencoba membuka browser untuk deputi1.kemenpora.go.id...")
    
    service = Service()
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    targets = config.TARGET_URLS.get('pelayanan_kemenpora', {}).get('categories', {})
    semua_berita_pelayanan = [] 

    try:
        for kategori, url_kategori in targets.items():
            print(f"\n Mengambil kategori: {kategori}")
            
            hasil_kategori = scrape_pelayanan_category(url_kategori, driver)
            
            if hasil_kategori:
                semua_berita_pelayanan.extend(hasil_kategori)
    except Exception as e:
        print(f"Terjadi error saat proses utama: {e}")
    finally:
        print("\nMenutup browser...")
        driver.quit()
    
    return pd.DataFrame(semua_berita_pelayanan)

# --- Blok Testing Langsung ---
if __name__ == '__main__':
    df_hasil_pelayanan = scrape_from_pelayanan()
    if not df_hasil_pelayanan.empty:
        print("\n Hasil akhir scraping deputi1.kemenpora.go.id")
        print(df_hasil_pelayanan)
    else:
        print("Tidak ada berita yang berhasil dikumpulkan dari deputi1.kemenpora.go.id")


# Scraping deputi2.kemenpora.go.id
def scrape_pembudayaan_category(category_url: str, driver):
    list_berita_kategori = []
    driver.get(category_url)
    
    for page_num in range(config.MAX_PAGES_PER_CATEGORY):
        print(f"\n Memproses Halaman {page_num + 1} di kategori {category_url.split('/')[-1]}")

    for _ in range(config.MAX_SCROLLS):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")    
        time.sleep(config.SLEEP_TIME)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        articles = soup.select('div.newsrow__row')
        print(f"Ditemukan {len(articles)} wadah berita di halaman ini.")

        for i, article in enumerate(articles):
            try:
                title_element = article.find('h2', class_='newsrow__title')
                    
                if title_element:
                    link_element = title_element.find('a') 
                        
                    if link_element:
                            judul = title_element.get_text(strip=True)
                            link = link_element.get('href')
                    
                    if judul and link:
                        list_berita_kategori.append({
                            'sumber': 'deputi2.kemenpora.go.id',
                            'judul': judul,
                            'link': link
                        })
            except Exception as e:
                print(f"Melewati satu artikel karena error: {e}")
                continue

        try:
            xpath_selector = "//a[text()='→']" 
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath_selector)))
            
            print("Tombol 'Next' ditemukan. Melakukan klik...")
            driver.execute_script("arguments[0].click();", next_button)

        except Exception:
            print("Tombol 'Next' tidak ditemukan atau tidak bisa diklik. Scraping untuk kategori ini selesai.")
            break

    return list_berita_kategori

def scrape_from_pembudayaan():
    print("\n Mencoba membuka browser untuk deputi2.kemenpora.go.id...")
    
    service = Service()
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    targets = config.TARGET_URLS.get('pembudayaan_kemenpora', {}).get('categories', {})
    semua_berita_pembudayaan = [] 

    try:
        for kategori, url_kategori in targets.items():
            print(f"\n Mengambil kategori: {kategori}")
            
            hasil_kategori = scrape_pembudayaan_category(url_kategori, driver)
            
            if hasil_kategori:
                semua_berita_pembudayaan.extend(hasil_kategori)
    except Exception as e:
        print(f"Terjadi error saat proses utama: {e}")
    finally:
        print("\nMenutup browser...")
        driver.quit()
    
    return pd.DataFrame(semua_berita_pembudayaan)

# --- Blok Testing Langsung ---
if __name__ == '__main__':
    df_hasil_pembudayaan = scrape_from_pembudayaan()
    if not df_hasil_pembudayaan.empty:
        print("\n Hasil akhir scraping deputi2.kemenpora.go.id")
        print(df_hasil_pembudayaan)
    else:
        print("Tidak ada berita yang berhasil dikumpulkan dari deputi2.kemenpora.go.id")


# Scraping deputi3.kemenpora.go.id
def scrape_presor_category(category_url: str, driver):
    list_berita_kategori = []
    driver.get(category_url)
    
    for page_num in range(config.MAX_PAGES_PER_CATEGORY):
        print(f"\n Memproses Halaman {page_num + 1} di kategori {category_url.split('/')[-1]}")

    for _ in range(config.MAX_SCROLLS):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")    
        time.sleep(config.SLEEP_TIME)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        articles = soup.select('div.newsrow__row')
        print(f"Ditemukan {len(articles)} wadah berita di halaman ini.")

        for i, article in enumerate(articles):
            try:
                title_element = article.find('h2', class_='newsrow__title')
                    
                if title_element:
                    link_element = title_element.find('a') 
                        
                    if link_element:
                            judul = title_element.get_text(strip=True)
                            link = link_element.get('href')
                    
                    if judul and link:
                        list_berita_kategori.append({
                            'sumber': 'deputi3.kemenpora.go.id',
                            'judul': judul,
                            'link': link
                        })
            except Exception as e:
                print(f"Melewati satu artikel karena error: {e}")
                continue

        try:
            xpath_selector = "//a[text()='→']" 
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath_selector)))
            
            print("Tombol 'Next' ditemukan. Melakukan klik...")
            driver.execute_script("arguments[0].click();", next_button)

        except Exception:
            print("Tombol 'Next' tidak ditemukan atau tidak bisa diklik. Scraping untuk kategori ini selesai.")
            break

    return list_berita_kategori

def scrape_from_presor():
    print("\n Mencoba membuka browser untuk deputi3.kemenpora.go.id...")
    
    service = Service()
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    targets = config.TARGET_URLS.get('presor_kemenpora', {}).get('categories', {})
    semua_berita_presor = [] 

    try:
        for kategori, url_kategori in targets.items():
            print(f"\n Mengambil kategori: {kategori}")
            
            hasil_kategori = scrape_presor_category(url_kategori, driver)
            
            if hasil_kategori:
                semua_berita_presor.extend(hasil_kategori)
    except Exception as e:
        print(f"Terjadi error saat proses utama: {e}")
    finally:
        print("\nMenutup browser...")
        driver.quit()
    
    return pd.DataFrame(semua_berita_presor)

# --- Blok Testing Langsung ---
if __name__ == '__main__':
    df_hasil_presor = scrape_from_presor()
    if not df_hasil_presor.empty:
        print("\n Hasil akhir scraping deputi3.kemenpora.go.id")
        print(df_hasil_presor)
    else:
        print("Tidak ada berita yang berhasil dikumpulkan dari deputi3.kemenpora.go.id")


# Scraping deputi4.kemenpora.go.id
def scrape_indoor_category(category_url: str, driver):
    list_berita_kategori = []
    driver.get(category_url)
    
    for page_num in range(config.MAX_PAGES_PER_CATEGORY):
        print(f"\n Memproses Halaman {page_num + 1} di kategori {category_url.split('/')[-1]}")

    for _ in range(config.MAX_SCROLLS):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")    
        time.sleep(config.SLEEP_TIME)
        page_source = driver.page_source
        soup = BeautifulSoup(page_source, 'html.parser')

        articles = soup.select('div.newsrow__row')
        print(f"Ditemukan {len(articles)} wadah berita di halaman ini.")

        for i, article in enumerate(articles):
            try:
                title_element = article.find('h2', class_='newsrow__title')
                    
                if title_element:
                    link_element = title_element.find('a') 
                        
                    if link_element:
                            judul = title_element.get_text(strip=True)
                            link = link_element.get('href')
                    
                    if judul and link:
                        list_berita_kategori.append({
                            'sumber': 'deputi4.kemenpora.go.id',
                            'judul': judul,
                            'link': link
                        })
            except Exception as e:
                print(f"Melewati satu artikel karena error: {e}")
                continue

        try:
            xpath_selector = "//a[text()='→']" 
            next_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, xpath_selector)))
            
            print("Tombol 'Next' ditemukan. Melakukan klik...")
            driver.execute_script("arguments[0].click();", next_button)

        except Exception:
            print("Tombol 'Next' tidak ditemukan atau tidak bisa diklik. Scraping untuk kategori ini selesai.")
            break

    return list_berita_kategori

def scrape_from_indoor():
    print("\n Mencoba membuka browser untuk deputi4.kemenpora.go.id...")
    
    service = Service()
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    targets = config.TARGET_URLS.get('indoor_kemenpora', {}).get('categories', {})
    semua_berita_indoor = [] 

    try:
        for kategori, url_kategori in targets.items():
            print(f"\n Mengambil kategori: {kategori}")
            
            hasil_kategori = scrape_indoor_category(url_kategori, driver)
            
            if hasil_kategori:
                semua_berita_indoor.extend(hasil_kategori)
    except Exception as e:
        print(f"Terjadi error saat proses utama: {e}")
    finally:
        print("\nMenutup browser...")
        driver.quit()
    
    return pd.DataFrame(semua_berita_indoor)

# --- Blok Testing Langsung ---
if __name__ == '__main__':
    df_hasil_indoor = scrape_from_indoor()
    if not df_hasil_indoor.empty:
        print("\n Hasil akhir scraping deputi4.kemenpora.go.id")
        print(df_hasil_indoor)
    else:
        print("Tidak ada berita yang berhasil dikumpulkan dari deputi4.kemenpora.go.id")

    df_hasil_indoor = scrape_from_indoor()
    if not df_hasil_indoor.empty:
        print("\n Hasil akhir scraping deputi4.kemenpora.com")
        print(df_hasil_indoor)
    else:
        print("Tidak ada berita yang berhasil dikumpulkan dari deputi4.kemenpora.com")
