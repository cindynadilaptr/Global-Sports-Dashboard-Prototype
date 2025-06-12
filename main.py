# main.py
import pandas as pd
import os
import config
from src.data_collection.national_news_scraper import (
    scrape_from_kompas,
    scrape_from_bola,
    scrape_from_detik,
    scrape_from_indoor)
# from src.analysis.sentiment_analyzer import analisis_sentimen_dataframe
from src.analysis.data_processor import filter_berita_relevan

def run_pipeline():
    print("Mulai proses pengumpulan dan analisis berita")
    all_dataframes = []
    df_kompas = scrape_from_kompas()
    all_dataframes.append(df_kompas)
    df_bola = scrape_from_bola()
    all_dataframes.append(df_bola)
    df_detik = scrape_from_detik()
    all_dataframes.append(df_detik)
    df_indoor = scrape_from_indoor()
    all_dataframes.append(df_indoor) 

    valid_dataframes = [df for df in all_dataframes if not df.empty]
    if not valid_dataframes:
        print("\nPipeline selesai, namun tidak ada data yang berhasil dikumpulkan dari semua sumber.")
        return
    
    raw_df = pd.concat(all_dataframes, ignore_index=True)
    print(f"\n Semua data mentah terkumpul: Total {len(raw_df)} berita")

    filtered_df = filter_berita_relevan(raw_df)
    if not filtered_df.empty:
        # final_df = analisis_sentimen_dataframe(filtered_df, text_column='judul')
        final_df = filtered_df


    # Simpan hasil akhir ke CSV
    if not final_df.empty:
        try:
            df_lama = pd.read_csv(config.OUTPUT_CSV_PATH)
            print(f"\nData lama ditemukan, berisi {len(df_lama)} berita.")
            
            df_update = pd.concat([df_lama, final_df], ignore_index=True)
            print(f"Data digabungkan. Total sementara: {len(df_update)} berita.")

        except FileNotFoundError:
            print("\nFile data historis tidak ditemukan. Ini adalah proses pertama kali.")
            df_update = final_df

        print("Menghapus duplikat...")
        df_bersih = df_update.drop_duplicates(subset=['link'], keep='last')
        print(f"Setelah menghapus duplikat, total berita di database: {len(df_bersih)} berita.")

        # Simpan hasil akhir ke file CSV
        print("\nMenyimpan data historis yang sudah diperbarui...")
        os.makedirs(os.path.dirname(config.OUTPUT_CSV_PATH), exist_ok=True)
        df_bersih.to_csv(config.OUTPUT_CSV_PATH, index=False, encoding='utf-8')
        print(f"Data telah berhasil diperbarui di: {config.OUTPUT_CSV_PATH}")
    else:
        print("\nTidak ada berita baru yang relevan untuk ditambahkan hari ini.")

if __name__ == "__main__":
    run_pipeline()