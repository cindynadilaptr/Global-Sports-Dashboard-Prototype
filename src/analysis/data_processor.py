import pandas as pd
import re
from datetime import datetime, timedelta
import sys
import os

script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.append(project_root)
import config

def translate_date_ind_to_eng(text):
    ind_to_eng_months = {
        'Januari': 'January', 'Jan': 'Jan',
        'Februari': 'February', 'Feb': 'Feb', 'Peb': 'Feb',
        'Maret': 'March', 'Mar': 'Mar',
        'April': 'April', 'Apr': 'Apr',
        'Mei': 'May', 'May': 'May',
        'Juni': 'June', 'Jun': 'Jun',
        'Juli': 'July', 'Jul': 'Jul',
        'Agustus': 'August', 'Ags': 'Aug', 'Agst': 'Aug', 'Agt': 'Aug',
        'September': 'September', 'Sep': 'Sep', 'Sept': 'Sep',
        'Oktober': 'October', 'Okt': 'Oct',
        'November': 'November', 'Nov': 'Nov',
        'Desember': 'December', 'Des': 'Dec'
    }

    ind_to_eng_days = {
        'Senin': 'Monday', 'Selasa': 'Tuesday', 'Rabu': 'Wednesday',
        'Kamis': 'Thursday', 'Jumat': 'Friday', 'Sabtu': 'Saturday',
        'Minggu': 'Sunday'
    }

    for indo, eng in ind_to_eng_days.items():
        text = re.sub(rf'\b{indo}\b', eng, text, flags=re.IGNORECASE)
    for indo, eng in ind_to_eng_months.items():
        text = re.sub(rf'\b{indo}\b', eng, text, flags=re.IGNORECASE)
    return text

def standardize_dates(df: pd.DataFrame, column_name: str = 'tanggal_terbit'):
    if df.empty or column_name not in df.columns:
        return df

    def parse_date(date_str):
        if not isinstance(date_str, str):
            return ''
        original = date_str
        date_str = date_str.replace('WIB', '').strip()
        date_str = translate_date_ind_to_eng(date_str)
        date_str_lower = date_str.lower()
        now = datetime.now()
        try:
            if 'minutes ago' in date_str_lower or 'menit yang lalu' in date_str_lower:
                minutes = int(re.search(r'\d+', date_str_lower).group())
                return (now - timedelta(minutes=minutes)).strftime('%d/%m/%Y')
            elif 'hours ago' in date_str_lower or 'jam yang lalu' in date_str_lower:
                hours = int(re.search(r'\d+', date_str_lower).group())
                return (now - timedelta(hours=hours)).strftime('%d/%m/%Y')
            elif 'days ago' in date_str_lower or 'hari yang lalu' in date_str_lower:
                days = int(re.search(r'\d+', date_str_lower).group())
                return (now - timedelta(days=days)).strftime('%d/%m/%Y')

            possible_formats = [
                "%d %B %Y", "%d %b %Y", "%Y/%m/%d", "%Y-%m-%d",
                "%d-%m-%Y", "%A, %d %B %Y", "%A, %d %b %Y",
                "%d/%m/%Y", "%Y-%m-%dT%H:%M:%S%z"
            ]

            for fmt in possible_formats:
                try:
                    return datetime.strptime(date_str, fmt).strftime('%d/%m/%Y')
                except:
                    continue

            parsed = pd.to_datetime(date_str, errors='coerce')
            return parsed.strftime('%d/%m/%Y') if not pd.isna(parsed) else ''
        except:
            return ''

    df[column_name] = df[column_name].apply(parse_date)
    print("Standarisasi tanggal selesai. Semua baris dipertahankan dan diformat seragam.")
    return df

def filter_berita_relevan(df: pd.DataFrame):
    if df.empty:
        return df

    print("\n Memulai filtering berita relevan")

    df['teks_lengkap'] = df['judul'].str.lower()

    if 'ringkasan' in df.columns:
        print("Kolom 'ringkasan' ditemukan, menambahkan ke teks untuk filtering.")
        df['teks_lengkap'] = df['teks_lengkap'] + ' ' + df['ringkasan'].fillna('').str.lower()

    kata_kunci_wajib_pattern = '|'.join(config.KATA_KUNCI_WAJIB)
    df_filtered = df[df['teks_lengkap'].str.contains(kata_kunci_wajib_pattern, na=False)].copy()

    if not df_filtered.empty:
        kata_kunci_negatif_pattern = '|'.join(config.KATA_KUNCI_NEGATIF)
        df_filtered = df_filtered[~df_filtered['teks_lengkap'].str.contains(kata_kunci_negatif_pattern, na=False)]

    print(f"Filtering selesai. Dari {len(df)} berita, ditemukan {len(df_filtered)} berita yang relevan.")

    df_filtered = df_filtered.drop(columns=['teks_lengkap'])
    return df_filtered
