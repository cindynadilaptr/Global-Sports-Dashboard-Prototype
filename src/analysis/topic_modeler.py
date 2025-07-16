import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from src.analysis.text_preprocessor import preprocess_for_topic_modeling, STOPWORDS_FOR_TOPICS

def extract_top_keywords(texts, top_n=20, min_document_frequency=5):
    if not texts:
        return []

    processed_texts = [preprocess_for_topic_modeling(t) for t in texts if isinstance(t, str)]
    
    vectorizer = TfidfVectorizer(
        stop_words=list(STOPWORDS_FOR_TOPICS),
        max_df=0.90,
        min_df=min_document_frequency,
        use_idf=True,
        smooth_idf=True,
        norm='l2'
    )

    try:
        tfidf_matrix = vectorizer.fit_transform(processed_texts)
    except ValueError:
        return []
        
    tfidf_sum = tfidf_matrix.sum(axis=0)
    tfidf_scores = [(word, tfidf_sum[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
    sorted_keywords = sorted(tfidf_scores, key=lambda x: x[1], reverse=True)
    
    top_keywords = sorted_keywords[:top_n]

    if not top_keywords:
        return []

    max_score = top_keywords[0][1]
    normalized_keywords = [
        (word, (score / max_score) * 100) for word, score in top_keywords
    ]
    
    return normalized_keywords

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
    import pandas as pd

    DATASETS_TO_TEST = {
        "Berita Industri (Eksternal)": {
            "file_path": "data/hasil_monitoring_industri.csv",
            "text_column": "judul"
        },
        "Berita Internal Kemenpora": {
            "file_path": "data/hasil_monitoring_internal.csv",
            "text_column": "judul"
        },
        "Caption Instagram": {
            "file_path": "data/instagram_posts_performance.csv",
            "text_column": "caption"
        },
        "Komentar Instagram": {
            "file_path": "data/instagram_comments_sentiment.csv",
            "text_column": "text"
        }
    }

    print("="*50)
    print("--- MENJALANKAN SCRIPT DALAM MODE TESTING (ANALISIS KESELURUHAN DATA) ---")
    print("="*50)

    for source_name, config in DATASETS_TO_TEST.items():
        file_path = config["file_path"]
        text_column = config["text_column"]

        print(f"\n--- MENGUJI SUMBER: {source_name} ---")
        print(f"File: {file_path}")

        try:
            df = pd.read_csv(file_path)
        except FileNotFoundError:
            print(f"[ERROR] File testing tidak ditemukan.")
            continue

        if text_column not in df.columns:
            print(f"[ERROR] Kolom '{text_column}' tidak ditemukan.")
            continue

        texts_to_analyze = df[text_column].dropna().tolist()
        print(f"Ditemukan {len(texts_to_analyze)} baris teks untuk dianalisis.")

        top_keywords = extract_top_keywords(texts_to_analyze, top_n=15, min_document_frequency=5)

        print("\nTOP KEYWORDS DITEMUKAN:")
        if not top_keywords:
            print("Tidak ada keyword yang memenuhi syarat.")
        else:
            for word, score in top_keywords:
                print(f"- {word} (Skor: {score:.2f})")
            
            plot_top_keywords(top_keywords, title=f"Top Keywords dari {source_name}")
