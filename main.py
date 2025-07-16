import nltk
nltk.download('stopwords')
nltk.download('punkt')
nltk.download('wordnet')
from dotenv import load_dotenv
load_dotenv()
import sys
import os
import pandas as pd
import config
import gspread
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
from gspread_dataframe import set_with_dataframe

from src.data_collection.insta_scraper import scrape_from_instagram_api
from src.analysis.data_processor import filter_berita_relevan, standardize_dates
from src.analysis.sentiment_analyzer import analisis_sentimen_dataframe
from src.analysis.topic_modeler import extract_top_keywords

def save_and_upload(df_new: pd.DataFrame, output_path: str, unique_key: str, gsheet_tab_name: str):
    if df_new is None or df_new.empty:
        print(f"[INFO] Tidak ada data baru untuk diproses di {output_path}")
        return

    print(f"[PROCESS] Memperbarui file lokal: {output_path}...")
    final_df_to_save = df_new
    if os.path.exists(output_path):
        try:
            df_lama = pd.read_csv(output_path)
            df_lama[unique_key] = df_lama[unique_key].astype(str)
            df_new[unique_key] = df_new[unique_key].astype(str)
            combined_df = pd.concat([df_lama, df_new], ignore_index=True)
            final_df_to_save = combined_df.drop_duplicates(subset=[unique_key], keep='last')
        except (FileNotFoundError, pd.errors.EmptyDataError):
             print(f"[WARNING] File lama {output_path} tidak ditemukan/kosong. Membuat file baru.")
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    final_df_to_save.to_csv(output_path, index=False, encoding='utf-8')
    print(f"[SAVED] {output_path} diperbarui. Total data sekarang: {len(final_df_to_save)}.")

    print(f"Mengunggah data ke Google Sheet tab: '{gsheet_tab_name}'...")
    try:
        gc = gspread.service_account(filename='google-api-credentials.json')
        spreadsheet = gc.open(config.GOOGLE_SHEET_NAME)
        worksheet = spreadsheet.worksheet(gsheet_tab_name)
        worksheet.clear()
        set_with_dataframe(worksheet, final_df_to_save, include_index=False, include_column_header=True, resize=True)
        print(f"[SUCCESS] Google Sheet tab '{gsheet_tab_name}' berhasil di-update.")
    except gspread.exceptions.WorksheetNotFound:
        print(f"[ERROR] Tab '{gsheet_tab_name}' tidak ditemukan di Google Sheet '{config.GOOGLE_SHEET_NAME}'.")
    except Exception as e:
        print(f"[ERROR] Gagal meng-update Google Sheet: {e}")

def proses_trending_keywords(df_source: pd.DataFrame, text_column: str, output_path: str, gsheet_tab_name: str):
    if df_source is None or df_source.empty or text_column not in df_source.columns:
        print(f"[INFO] Tidak ada data untuk analisis keywords di {gsheet_tab_name}")
        return
        
    print(f"\n Menganalisis Trending Keywords untuk: {gsheet_tab_name}")
    
    texts = df_source[text_column].dropna().tolist()
    top_keywords_list = extract_top_keywords(texts, top_n=20)
    
    if not top_keywords_list:
        print(f"[INFO] Tidak ada keyword yang dihasilkan untuk {gsheet_tab_name}")
        return

    df_keywords = pd.DataFrame(top_keywords_list, columns=['keyword', 'skor_relevansi'])
    
    save_and_upload(df_keywords, output_path, 'keyword', gsheet_tab_name)

def process_all_data():
    print("\n" + "="*20 + " MEMPROSES DATA WEBSITE " + "="*20)
    all_website_dataframes = []
    for source_name, source_config in config.TARGET_URLS.items():
        scraper_func = source_config.get('scraper_function')
        if scraper_func:
            try:
                df = scraper_func()
                if df is not None and not df.empty:
                    df['source'] = source_name
                    df['tipe_sumber'] = 'internal' if source_name in config.INTERNAL_SOURCES_NAMES else 'eksternal'
                    all_website_dataframes.append(df)
            except Exception as e:
                print(f"[ERROR] Scraping gagal dari '{source_name}': {e}")
    
    if all_website_dataframes:
        raw_df = pd.concat(all_website_dataframes, ignore_index=True)
        clean_df = standardize_dates(raw_df, column_name='tanggal_terbit')
        
        df_internal = clean_df[clean_df['tipe_sumber'] == 'internal'].copy()
        df_internal_analyzed = analisis_sentimen_dataframe(df_internal, text_column='judul')
        save_and_upload(df_internal_analyzed, config.OUTPUT_PATH_INTERNAL, 'link', config.GCP_SHEET_TABS['internal'])
        proses_trending_keywords(df_internal_analyzed, 'judul', config.OUTPUT_PATH_KEYWORDS_INTERNAL, config.GCP_SHEET_TABS['keywords_internal'])

        df_industry_filtered = filter_berita_relevan(clean_df)
        df_industry_analyzed = analisis_sentimen_dataframe(df_industry_filtered, text_column='judul')
        save_and_upload(df_industry_analyzed, config.OUTPUT_PATH_INDUSTRY, 'link', config.GCP_SHEET_TABS['industry'])
        proses_trending_keywords(df_industry_analyzed, 'judul', config.OUTPUT_PATH_KEYWORDS_INDUSTRY, config.GCP_SHEET_TABS['keywords_industry'])
    else:
        print("[INFO] Tidak ada data website yang berhasil di-scrape.")

    print("\n" + "="*20 + " MEMPROSES DATA INSTAGRAM " + "="*20)
    try:
        df_profile, df_posts, df_comments = scrape_from_instagram_api(target_account_key="personal")

        if df_profile is not None:
            save_and_upload(df_profile, config.OUTPUT_PATH_IG_PROFILE, 'id', config.GCP_SHEET_TABS['profile'])
        
        if df_posts is not None:
            df_posts_analyzed = analisis_sentimen_dataframe(df_posts, text_column='caption')
            save_and_upload(df_posts_analyzed, config.OUTPUT_PATH_IG_POSTS, 'id', config.GCP_SHEET_TABS['posts'])
            proses_trending_keywords(df_posts_analyzed, 'caption', config.OUTPUT_PATH_KEYWORDS_POSTS, config.GCP_SHEET_TABS['keywords_posts'])

        if df_comments is not None:
            df_comments_analyzed = analisis_sentimen_dataframe(df_comments, text_column='text')
            save_and_upload(df_comments_analyzed, config.OUTPUT_PATH_IG_COMMENTS, 'id', config.GCP_SHEET_TABS['comments'])
            proses_trending_keywords(df_comments_analyzed, 'text', config.OUTPUT_PATH_KEYWORDS_COMMENTS, config.GCP_SHEET_TABS['keywords_comments'])

    except Exception as e:
        print(f"[ERROR] Scraping Instagram gagal: {e}")

if __name__ == "__main__":
    process_all_data()
    print("\n" + "="*20 + " SEMUA PROSES SELESAI " + "="*20)