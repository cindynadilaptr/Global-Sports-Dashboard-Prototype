# main.py
import os
from config import OUTPUT_CSV_PATH
from src.data_collection.news_collector import fetch_all_news
# from src.analysis.sentiment_analyzer import analyze_sentiment_from_dataframe

def run_pipeline():
    print("Memulai pipeline data intelijen olahraga...")

    # Mengambil data berita
    df_berita = fetch_all_news()

    if not df_berita.empty:
        print("\n=== Menampilkan 5 Berita Pertama yang Terkumpul ===")
        print(df_berita.head())

    # (Memanggil fungsi analisis sentimen, dll.)

    # Menyimpan hasil akhir
    os.makedirs(os.path.dirname(OUTPUT_CSV_PATH), exist_ok=True)
    df_berita.to_csv(OUTPUT_CSV_PATH, index=False, encoding='utf-8')
    print(f"Data berhasil disimpan di {OUTPUT_CSV_PATH}")

    print("Pipeline selesai.")

if __name__ == "__main__":
    run_pipeline()