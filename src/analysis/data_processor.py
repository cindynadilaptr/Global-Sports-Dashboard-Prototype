import pandas as pd
import sys
import os
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.append(project_root)
import config

def filter_berita_relevan(df: pd.DataFrame):
    if df.empty:
        return df

    print("\n Memulai filtering berita relevan")

    df['teks_lengkap'] = df['judul'].str.lower()

    if 'ringkasan' in df.columns:
        print("Kolom 'ringkasan' ditemukan, menambahkan ke teks untuk filtering.")
        df['teks_lengkap'] = df['teks_lengkap'] + ' ' + df['ringkasan'].fillna('').str.lower()

    # Filter berdasarkan keywords wajib
    kata_kunci_wajib_pattern = '|'.join(config.KATA_KUNCI_WAJIB)
    df_filtered = df[df['teks_lengkap'].str.contains(kata_kunci_wajib_pattern, na=False)].copy()

    # Filter berdasarkan keywords negatif
    if not df_filtered.empty:
        kata_kunci_negatif_pattern = '|'.join(config.KATA_KUNCI_NEGATIF)
        df_filtered = df_filtered[~df_filtered['teks_lengkap'].str.contains(kata_kunci_negatif_pattern, na=False)]

    print(f"Filtering selesai. Dari {len(df)} berita, ditemukan {len(df_filtered)} berita yang relevan.")

    df_filtered = df_filtered.drop(columns=['teks_lengkap'])
    return df_filtered