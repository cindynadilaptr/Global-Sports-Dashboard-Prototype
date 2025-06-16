import pandas as pd
import os
import config
from src.analysis.data_processor import filter_berita_relevan
from src.data_collection.insta_scraper import scrape_from_instagram_api
# from src.analysis.sentiment_analyzer import analisis_sentimen_dataframe

def save_or_append_data(df_new: pd.DataFrame, output_path: str, unique_key: str):
    """
    Fungsi pembantu yang lebih andal untuk menyimpan atau menggabungkan data,
    dengan memastikan konsistensi tipe data.
    """
    if df_new is None or df_new.empty:
        print(f"Tidak ada data baru yang valid untuk disimpan ke {output_path}")
        return
    
    if unique_key not in df_new.columns:
        print(f"Error: Kunci unik '{unique_key}' tidak ada di data baru. Melewati penyimpanan.")
        return
    df_new[unique_key] = df_new[unique_key].astype(str)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    try:
        df_lama = pd.read_csv(output_path)
        print(f"Data lama ditemukan di {output_path}, berisi {len(df_lama)} baris.")
        if unique_key in df_lama.columns:
            df_lama[unique_key] = df_lama[unique_key].astype(str)
        df_updated = pd.concat([df_lama, df_new], ignore_index=True)
        
    except FileNotFoundError:
        print(f"File {output_path} tidak ditemukan. Membuat file baru.")
        df_updated = df_new

    df_final = df_updated.drop_duplicates(subset=[unique_key], keep='last')
    df_final.to_csv(output_path, index=False, encoding='utf-8')
    print(f"Data di {output_path} berhasil diperbarui. Total sekarang: {len(df_final)} baris.")

def run_pipeline():
    print("Mulai proses pengumpulan dan analisis berita")
    """all_scraped_data = {}

    # Pengumpulan data dinamis
    for source_name, source_config in config.TARGET_URLS.items():
        scraper_func = source_config.get('scraper_function')
        
        if scraper_func and callable(scraper_func):
            try:
                df = scraper_func()
                if df is not None and not df.empty:
                    df['tipe_sumber'] = 'internal' if source_name in config.INTERNAL_SOURCES_NAMES else 'eksternal'
                    all_scraped_data[source_name] = df
            except Exception as e:
                print(f"GAGAL scraping {source_name}. Error: {e}")
        else:
            break

        if not all_scraped_data:
            print("Tidak ada data yang berhasil dikumpulkan dari sumber manapun.")
            return

        raw_df_combined = pd.concat(all_scraped_data.values(), ignore_index=True)
        print(f"Total data yang dikumpulkan: {len(raw_df_combined)} baris")

    # Monitoring Internal Website Kemenpora
    print("\n Monitoring Internal Website Kemenpora...")
    df_internal_raw = raw_df_combined[raw_df_combined['tipe_sumber'] == 'internal'].copy()
    
    if not df_internal_raw.empty:
        df_internal_final = df_internal_raw
        os.makedirs(os.path.dirname(config.OUTPUT_PATH_INTERNAL), exist_ok=True)
        df_internal_final.to_csv(config.OUTPUT_PATH_INTERNAL, index=False, encoding='utf-8')
        print(f"Data internal berhasil disimpan ke: {config.OUTPUT_PATH_INTERNAL}")
    else:
        print("Tidak ada data internal yang terkumpul.")
    
    # Monitoring Berita Industri Olahraga
    print("\n Monitoring Berita Seputar Industri Olahraga...")
    df_industry_filtered = filter_berita_relevan(raw_df_combined)

    if not df_industry_filtered.empty:
        df_industry_final = df_industry_filtered
        os.makedirs(os.path.dirname(config.OUTPUT_PATH_INDUSTRY), exist_ok=True)
        df_industry_final.to_csv(config.OUTPUT_PATH_INDUSTRY, index=False, encoding='utf-8')
        print(f"Data industri olahraga relevan berhasil disimpan ke: {config.OUTPUT_PATH_INDUSTRY}")
    else:
        print("Tidak ada berita industri yang relevan setelah filtering.")
    
    print("\n Proses pengumpulan dan analisis berita selesai.")"""

    # Monitoring Instagram
    print("\n Monitoring Media Sosial Instagram Deputi Industri Olahraga Kemenpora...")
    print("\n--- Menjalankan scraper untuk: Instagram ---")
    try:
        df_posts_ig, df_comments_ig = scrape_from_instagram_api()
    except Exception as e:
        print(f"GAGAL scraping Instagram. Error: {e}")
        df_posts_ig, df_comments_ig = pd.DataFrame(), pd.DataFrame()
    save_or_append_data(df_posts_ig, 'data/instagram_posts_performance.csv', unique_key='id')
    save_or_append_data(df_comments_ig, 'data/instagram_comments_sentiment.csv', unique_key='id')

        
if __name__ == '__main__':
    run_pipeline()
    print("Pipeline selesai dijalankan.")
