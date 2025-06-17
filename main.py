import pandas as pd
import os
import config
from src.data_collection.insta_scraper import scrape_from_instagram_api
from src.analysis.data_processor import filter_berita_relevan, standardize_dates

def save_or_append_data(df_new: pd.DataFrame, output_path: str, unique_key: str):
    if df_new is None or df_new.empty:
        print(f"[INFO] Tidak ada data baru untuk {output_path}")
        return

    if unique_key not in df_new.columns:
        print(f"[WARNING] Kolom '{unique_key}' tidak ditemukan. Lewati {output_path}")
        return

    df_new[unique_key] = df_new[unique_key].astype(str)
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    try:
        df_lama = pd.read_csv(output_path)
        df_lama[unique_key] = df_lama[unique_key].astype(str)
        df_updated = pd.concat([df_lama, df_new], ignore_index=True)
    except FileNotFoundError:
        df_updated = df_new

    df_final = df_updated.drop_duplicates(subset=[unique_key], keep='last')
    df_final.to_csv(output_path, index=False, encoding='utf-8')
    print(f"[SAVED] {output_path} diperbarui dengan {len(df_new)} data baru.")

def run_pipeline():
    all_website_dataframes = []
    website_sources = {k: v for k, v in config.TARGET_URLS.items() if v.get('type') != 'instagram_api'}

    for source_name, source_config in website_sources.items():
        scraper_func = source_config.get('scraper_function')
        if scraper_func:
            try:
                df = scraper_func()
                if df is not None and not df.empty:
                    if 'tanggal_terbit' not in df.columns:
                        print(f"[WARNING] '{source_name}' tidak punya kolom tanggal_terbit")
                    df['tipe_sumber'] = 'internal' if source_name in config.INTERNAL_SOURCES_NAMES else 'eksternal'
                    all_website_dataframes.append(df)
            except Exception as e:
                print(f"[ERROR] Scraping gagal dari '{source_name}': {e}")

    df_posts_ig, df_comments_ig = pd.DataFrame(), pd.DataFrame()
    try:
        df_posts_ig, df_comments_ig = scrape_from_instagram_api(target_account_key="personal")
    except Exception as e:
        print(f"[ERROR] Scraping IG gagal: {e}")

    if all_website_dataframes:
        raw_df_websites = pd.concat(all_website_dataframes, ignore_index=True)
    print("Contoh format tanggal dari internal:")
    for df in all_website_dataframes:
        if 'tipe_sumber' in df.columns and 'tanggal_terbit' in df.columns:
            internal_sample = df[df['tipe_sumber'] == 'internal']['tanggal_terbit'].dropna().unique()
            print(internal_sample[:5])  # cetak contoh 5 format
        clean_df_websites = standardize_dates(raw_df_websites, column_name='tanggal_terbit')

        df_internal = clean_df_websites[clean_df_websites['tipe_sumber'] == 'internal'].copy()
        save_or_append_data(df_internal, config.OUTPUT_PATH_INTERNAL, unique_key='link')

        df_industry_filtered = filter_berita_relevan(clean_df_websites)
        save_or_append_data(df_industry_filtered, config.OUTPUT_PATH_INDUSTRY, unique_key='link')
    else:
        print("[INFO] Tidak ada data website yang tersedia.")

    save_or_append_data(df_posts_ig, config.OUTPUT_PATH_IG_POSTS, unique_key='id')
    # df_comments_final = analisis_sentimen_dataframe(df_comments_ig, text_column='text')
    save_or_append_data(df_comments_ig, config.OUTPUT_PATH_IG_COMMENTS, unique_key='id')

if __name__ == "__main__":
    run_pipeline()
