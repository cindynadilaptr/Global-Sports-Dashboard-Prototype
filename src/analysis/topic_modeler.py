import re
import string
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
from collections import Counter
import matplotlib.pyplot as plt
import seaborn as sns
from src.analysis.text_preprocessor import preprocess_for_topic_modeling

# Ekstraksi frekuensi kata kunci
def extract_top_keywords(texts, top_n=20):
    texts = [preprocess_for_topic_modeling(t) for t in texts if isinstance(t, str)]
    vectorizer = TfidfVectorizer(stop_words=list(ENGLISH_STOP_WORDS) + [
        "yang", "dan", "untuk", "dengan", "pada", "dari", "ini", "itu", "kami", "mereka"
    ])
    tfidf_matrix = vectorizer.fit_transform(texts)
    tfidf_sum = tfidf_matrix.sum(axis=0)
    tfidf_scores = [(word, tfidf_sum[0, idx]) for word, idx in vectorizer.vocabulary_.items()]
    sorted_keywords = sorted(tfidf_scores, key=lambda x: x[1], reverse=True)
    return sorted_keywords[:top_n]

# Visualisasi
def plot_top_keywords(keywords, title="Top Keywords"):
    if not keywords:
        print("[INFO] Tidak ada keyword untuk divisualisasikan.")
        return
    words, scores = zip(*keywords)
    plt.figure(figsize=(10, 5))
    sns.barplot(x=scores, y=words, palette="viridis")
    plt.title(title)
    plt.xlabel("TF-IDF Score")
    plt.ylabel("Keyword")
    plt.tight_layout()
    plt.show()

#  Testing
if __name__ == "__main__":
    sample_data = pd.DataFrame({
        "judul": [
            "Timnas Indonesia Menang 2-0 atas Vietnam!",
            "PSSI resmi umumkan pelatih baru timnas.",
            "Suporter bangga dengan performa timnas semalam.",
            "Turnamen sepak bola Asia segera dimulai bulan depan.",
            "Timnas u-23 tampil luar biasa di pertandingan perdana."
        ]
    })

    top_keywords = extract_top_keywords(sample_data["judul"].tolist(), top_n=10)
    print("Top Keywords:")
    for word, score in top_keywords:
        print(f"{word}: {score:.4f}")

    plot_top_keywords(top_keywords, title="Trending Keywords dari Judul Berita")
