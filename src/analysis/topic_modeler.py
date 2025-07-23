import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from src.analysis import text_preprocessor
from src.analysis.text_preprocessor import preprocess_for_topic_modeling
from src.analysis.data_processor import standardize_dates

def extract_top_keywords(df, text_column, date_column=None, start_date=None, end_date=None, top_n=20, min_document_frequency=2):
    if df.empty:
        return []

    if date_column and start_date and end_date:
        df[date_column] = pd.to_datetime(df[date_column], errors='coerce', dayfirst=True)
        df_filtered = df[(df[date_column] >= start_date) & (df[date_column] <= end_date)].copy()
    else:
        df_filtered = df.copy()

    if df_filtered.empty:
        print("Tidak ada data dalam rentang waktu yang dipilih.")
        return []
    
    text_preprocessor.custom_stopwords = text_preprocessor.load_custom_stopwords()
    text_preprocessor.stemmed_custom_stopwords = set(
        text_preprocessor.stemmer.stem(w) for w in text_preprocessor.custom_stopwords
    )
    text_preprocessor.STOPWORDS_FOR_TOPICS = (
        text_preprocessor.stop_words_id |
        text_preprocessor.stop_words_en |
        text_preprocessor.custom_stopwords |
        text_preprocessor.stemmed_custom_stopwords |
        text_preprocessor.negation_words
    )

    processed_texts = df_filtered[text_column].apply(preprocess_for_topic_modeling).tolist()
    print("\nContoh hasil preprocessing:")
    for i in range(min(3, len(processed_texts))):
        print(f"- {processed_texts[i]}")

    vectorizer = TfidfVectorizer(
        max_df=0.90,
        min_df=min_document_frequency,
        use_idf=True,
        smooth_idf=True,
        norm='l2',
        ngram_range=(1, 2) 
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(processed_texts)
    except ValueError:
        print("Tidak cukup data untuk membuat vocabulary TF-IDF.")
        return []
        
    tfidf_sum = tfidf_matrix.sum(axis=0)
    tfidf_scores = [(word, tfidf_sum[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
    sorted_keywords = sorted(tfidf_scores, key=lambda x: x[1], reverse=True)
    
    top_keywords = sorted_keywords[:top_n]

    def is_meaningful(phrase):
        tokens = phrase.split()
        return all(token not in text_preprocessor.STOPWORDS_FOR_TOPICS for token in tokens)

    top_keywords = [kw for kw in top_keywords if is_meaningful(kw[0])]

    if not top_keywords:
        return []

    max_score = top_keywords[0][1] if top_keywords else 0
    normalized_keywords = [
        (word, (score / max_score) * 100) for word, score in top_keywords
    ]
    
    return normalized_keywords

def get_trending_keywords_last_30_days(df, text_column, date_column, top_n=15):
    print(f"[INFO] Menghitung keywords untuk 30 hari terakhir secara otomatis...")
    
    end_date = pd.to_datetime('today')
    start_date = end_date - pd.Timedelta(days=30)
    
    top_keywords = extract_top_keywords(
        df=df,
        text_column=text_column,
        date_column=date_column,
        start_date=start_date,
        end_date=end_date,
        top_n=top_n
    )
    
    return top_keywords

def plot_top_keywords(keywords, title="Top Keywords"):
    if not keywords:
        print("[INFO] Tidak ada keyword untuk divisualisasikan.")
        return
        
    words, scores = zip(*keywords)
    
    plt.figure(figsize=(12, 8))
    sns.barplot(x=list(scores), y=list(words), palette="viridis_r")
    plt.title(title, fontsize=16)
    plt.xlabel("Skor Relevansi (0-100)")
    plt.ylabel("Keyword", fontsize=12)
    plt.tight_layout()
    plt.show()

if __name__ == '__main__':
    
    DATASETS_TO_TEST = {
        "Berita Internal Kemenpora": {
            "file_path": "data/hasil_monitoring_internal.csv",
            "text_column": "judul",
            "date_column": "tanggal_terbit"
        },
        "Berita Industri Olahraga": {
            "file_path": "data/hasil_monitoring_industri.csv",
            "text_column": "judul",
            "date_column": "tanggal_terbit"
        },
        "Caption Instagram": {
            "file_path": "data/instagram_posts_performance.csv",
            "text_column": "caption",
            "date_column": "timestamp"
        },
        "Komentar Instagram": {
            "file_path": "data/instagram_comments_sentiment.csv",
            "text_column": "text",
            "date_column": "timestamp"
        }
    }

    print("="*50)
    print("--- MENJALANKAN SCRIPT ANALISIS TRENDING KEYWORDS ---")
    print("="*50)
    
    end_date_test = pd.to_datetime('today')
    start_date_test = end_date_test - pd.Timedelta(days=30)
    
    print(f"Menganalisis data dari: {start_date_test.strftime('%d-%m-%Y')} hingga {end_date_test.strftime('%d-%m-%Y')}\n")

    for source_name, config in DATASETS_TO_TEST.items():
        file_path = config["file_path"]
        text_column = config["text_column"]
        date_column = config["date_column"]

        print(f"--- MEMPROSES SUMBER: {source_name} ---")
        
        try:
            df = pd.read_csv(file_path)
            print(f"File '{file_path}' berhasil dibaca.")
        except FileNotFoundError:
            print(f"[ERROR] File testing tidak ditemukan di: {file_path}")
            continue

        if text_column not in df.columns or date_column not in df.columns:
            print(f"[ERROR] Kolom teks ('{text_column}') atau tanggal ('{date_column}') tidak ditemukan.")
            continue

        df_standardized = standardize_dates(df.copy(), date_column)
        top_keywords = extract_top_keywords(
            df=df_standardized,
            text_column=text_column,
            date_column=date_column,
            start_date=start_date_test,
            end_date=end_date_test,
            top_n=15)
        
        print("\nTOP KEYWORDS DITEMUKAN:")
        if not top_keywords:
            print("Tidak ada keyword yang memenuhi syarat.")
        else:
            for word, score in top_keywords:
                print(f"- {word} (Skor: {score:.2f})")
        print("-" * 20)      
    print("\n--- SEMUA PROSES SELESAI ---")