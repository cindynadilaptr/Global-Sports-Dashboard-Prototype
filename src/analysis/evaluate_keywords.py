import sys
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dateutil.relativedelta import relativedelta
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from src.analysis.topic_modeler import extract_top_keywords
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

ANALYSIS_TITLE = "Analisis Tema Umum (3 Bulan Terakhir)"
END_DATE_ANALYSIS = pd.to_datetime('today').date()
START_DATE_ANALYSIS = END_DATE_ANALYSIS - relativedelta(months=3)

DATASETS_CONFIG = {
    'Berita Industri Olahraga (Eksternal)': {
        'file_path': os.path.join(BASE_DIR, 'data/hasil_monitoring_industri.csv'),
        'text_column': 'judul', 'date_column': 'tanggal_terbit', 'title_column': 'judul'
    },
    'Berita Internal Kemenpora': {
        'file_path': os.path.join(BASE_DIR, 'data/hasil_monitoring_internal.csv'),
        'text_column': 'judul', 'date_column': 'tanggal_terbit', 'title_column': 'judul'
    },
    'Caption Instagram': {
        'file_path': os.path.join(BASE_DIR, 'data/instagram_posts_performance.csv'),
        'text_column': 'caption', 'date_column': 'timestamp', 'title_column': 'caption'
    },
    'Komentar Instagram': {
        'file_path': os.path.join(BASE_DIR, 'data/instagram_comments_sentiment.csv'),
        'text_column': 'text', 'date_column': 'timestamp'
    }
}

def analyze_source(source_name, config):
    print(f"\n[INFO] Menganalisis sumber: {source_name}...")
    try:
        df = pd.read_csv(config['file_path'])
    except FileNotFoundError:
        print(f"[ERROR] File tidak ditemukan: {config['file_path']}")
        return None

    date_col, text_col = config['date_column'], config['text_column']
    if date_col not in df.columns or text_col not in df.columns:
        print(f"[ERROR] Kolom tidak ditemukan.")
        return None
        
    df[date_col] = pd.to_datetime(df[date_col], format='%d/%m/%Y', errors='coerce').dt.date
    
    df_filtered = df[(df[date_col] >= START_DATE_ANALYSIS) & (df[date_col] <= END_DATE_ANALYSIS)]

    if df_filtered.empty:
        print(f"[INFO] Tidak ada data ditemukan dalam rentang waktu analisis.")
        return None

    print(f"Ditemukan {len(df_filtered)} data untuk dianalisis.")
    
    list_teks = df_filtered[text_col].dropna().tolist()
    keywords = extract_top_keywords(list_teks, top_n=15, min_document_frequency=5)
    return keywords

if __name__ == "__main__":
    all_results = {}
    for source_name, config in DATASETS_CONFIG.items():
        keywords = analyze_source(source_name, config)
        if keywords:
            all_results[source_name] = keywords

    print("\n\n" + "="*50)
    print(f"HASIL ANALISIS KEYWORDS: {ANALYSIS_TITLE}")
    print("="*50)

    website_sources_names = ['Berita Industri Olahraga (Eksternal)', 'Berita Internal Kemenpora']
    medsos_sources_names = ['Caption Instagram', 'Komentar Instagram']

    print("\n--- SUMBER WEBSITE ---")
    for source in website_sources_names:
        if source in all_results:
            print(f"\nTop Keywords untuk '{source}':")
            for word, score in all_results[source]:
                print(f"- {word} ({score:.4f})")
    print("\n\n--- SUMBER MEDIA SOSIAL ---")
    for source in medsos_sources_names:
        if source in all_results:
            print(f"\nTop Keywords untuk '{source}':")
            for word, score in all_results[source]:
                print(f"- {word} ({score:.4f})")
    
    print("\n[INFO] Menyiapkan grafik perbandingan...")
    website_results = {k: v for k, v in all_results.items() if k in website_sources_names}
    medsos_results = {k: v for k, v in all_results.items() if k in medsos_sources_names}

    if website_results:
        num_plots = len(website_results)
        fig, axes = plt.subplots(1, num_plots, figsize=(8 * num_plots, 7), squeeze=False)
        fig.suptitle(f'Keywords Umum dari Sumber Website\n({START_DATE_ANALYSIS} - {END_DATE_ANALYSIS})', fontsize=16)
        for i, (source, keywords) in enumerate(website_results.items()):
            words, scores = zip(*keywords)
            sns.barplot(ax=axes[0, i], x=list(scores), y=list(words), palette='plasma')
            axes[0, i].set_title(source)
        plt.tight_layout(rect=[0, 0, 1, 0.96])
    
    if medsos_results:
        num_plots = len(medsos_results)
        fig, axes = plt.subplots(1, num_plots, figsize=(8 * num_plots, 7), squeeze=False)
        fig.suptitle(f'Keywords Umum dari Sumber Media Sosial\n({START_DATE_ANALYSIS} - {END_DATE_ANALYSIS})', fontsize=16)
        for i, (source, keywords) in enumerate(medsos_results.items()):
            words, scores = zip(*keywords)
            sns.barplot(ax=axes[0, i], x=list(scores), y=list(words), palette='viridis')
            axes[0, i].set_title(source)
        plt.tight_layout(rect=[0, 0, 1, 0.96])

    if website_results or medsos_results:
        plt.show()