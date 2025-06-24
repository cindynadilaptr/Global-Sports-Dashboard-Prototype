import os
import pandas as pd
import config
import matplotlib.pyplot as plt

from src.data_collection.insta_scraper import scrape_from_instagram_api
from src.analysis.data_processor import filter_berita_relevan, standardize_dates
from src.analysis.sentiment_analyzer import analisis_sentimen_dataframe
from src.analysis.topic_modeler import extract_top_keywords, plot_top_keywords


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


def tampilkan_distribusi_sentimen(df: pd.DataFrame, sumber: str):
    if 'sentimen' not in df.columns:
        print(f"[INFO] Tidak ada kolom sentimen untuk {sumber}")
        return

    print(f"\n📊 Distribusi Sentimen - {sumber}")
    print(df['sentimen'].value_counts())

    plt.figure(figsize=(6, 4))
    df['sentimen'].value_counts().plot(kind='bar', color=['red', 'gray', 'green'])
    plt.title(f'Distribusi Sentimen - {sumber}')
    plt.xlabel('Kategori Sentimen')
    plt.ylabel('Jumlah')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.show()


def tampilkan_topik_trending(texts, sumber: str):
    if texts.empty:
        print(f"[INFO] Tidak ada teks tersedia untuk topik dari {sumber}")
        return
    print(f"\n🔥 Trending Keywords - {sumber}")
    top_keywords = extract_top_keywords(texts.tolist(), top_n=15)
    for word, score in top_keywords:
        print(f"{word}: {score:.4f}")
    plot_top_keywords(top_keywords, title=f"Trending Keywords - {sumber}")


def proses_website_data():
    all_website_dataframes = []
    website_sources = {
        k: v for k, v in config.TARGET_URLS.items() if v.get('type') != 'instagram_api'
    }

    for source_name, source_config in website_sources.items():
        scraper_func = source_config.get('scraper_function')
        if scraper_func:
            try:
                df = scraper_func()
                if df is not None and not df.empty:
                    if 'tanggal_terbit' not in df.columns:
                        print(f"[WARNING] '{source_name}' tidak punya kolom tanggal_terbit")
                    df['tipe_sumber'] = (
                        'internal' if source_name in config.INTERNAL_SOURCES_NAMES else 'eksternal'
                    )
                    all_website_dataframes.append(df)
            except Exception as e:
                print(f"[ERROR] Scraping gagal dari '{source_name}': {e}")

    if all_website_dataframes:
        raw_df = pd.concat(all_website_dataframes, ignore_index=True)
        print("Contoh format tanggal dari internal:")
        for df in all_website_dataframes:
            if 'tipe_sumber' in df.columns and 'tanggal_terbit' in df.columns:
                sample = df[df['tipe_sumber'] == 'internal']['tanggal_terbit'].dropna().unique()
                print(sample[:5])

        clean_df = standardize_dates(raw_df, column_name='tanggal_terbit')

        # Internal
        df_internal = clean_df[clean_df['tipe_sumber'] == 'internal'].copy()
        df_internal = analisis_sentimen_dataframe(df_internal, text_column='judul')
        tampilkan_distribusi_sentimen(df_internal, "Berita Internal")
        tampilkan_topik_trending(df_internal['judul'], "Berita Internal")
        save_or_append_data(df_internal, config.OUTPUT_PATH_INTERNAL, unique_key='link')

        # Industri
        df_industry = filter_berita_relevan(clean_df)
        df_industry = analisis_sentimen_dataframe(df_industry, text_column='judul')
        tampilkan_distribusi_sentimen(df_industry, "Berita Industri")
        tampilkan_topik_trending(df_industry['judul'], "Berita Industri")
        save_or_append_data(df_industry, config.OUTPUT_PATH_INDUSTRY, unique_key='link')
    else:
        print("[INFO] Tidak ada data website yang tersedia.")


def proses_instagram_data():
    try:
        df_profile, df_posts, df_comments = scrape_from_instagram_api(target_account_key="personal")
    except Exception as e:
        print(f"[ERROR] Scraping IG gagal: {e}")
        return

    if not df_profile.empty:
        save_or_append_data(df_profile, config.OUTPUT_PATH_IG_PROFILE, unique_key='id')

    if not df_posts.empty:
        df_posts = analisis_sentimen_dataframe(df_posts, text_column='caption')
        tampilkan_distribusi_sentimen(df_posts, "IG Posts")
        tampilkan_topik_trending(df_posts['caption'], "IG Posts")
        save_or_append_data(df_posts, config.OUTPUT_PATH_IG_POSTS, unique_key='id')

    if not df_comments.empty:
        df_comments = analisis_sentimen_dataframe(df_comments, text_column='text')
        tampilkan_distribusi_sentimen(df_comments, "IG Comments")
        tampilkan_topik_trending(df_comments['text'], "IG Comments")
        save_or_append_data(df_comments, config.OUTPUT_PATH_IG_COMMENTS, unique_key='id')


def run_pipeline():
    proses_website_data()
    proses_instagram_data()


if __name__ == "__main__":
    run_pipeline()
