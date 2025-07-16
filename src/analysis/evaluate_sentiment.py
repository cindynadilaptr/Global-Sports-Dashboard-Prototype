import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from src.analysis.sentiment_analyzer import analisis_sentimen_text

FILE_PATH = 'data/evaluasi_sentimen_dataset.csv'
MANUAL_LABEL_COL = 'sentiment'
TEXT_COL = 'text'
PREDICTED_LABEL_COL = 'label_prediksi'

print(f"[INFO] Memuat data evaluasi dari: {FILE_PATH}")
try:
    df = pd.read_csv(FILE_PATH)
except FileNotFoundError:
    print(f"[ERROR] File evaluasi tidak ditemukan. Pastikan file '{FILE_PATH}' sudah ada.")
    exit()

if MANUAL_LABEL_COL not in df.columns or TEXT_COL not in df.columns:
    print(f"[ERROR] Kolom '{MANUAL_LABEL_COL}' atau '{TEXT_COL}' tidak ditemukan. Pastikan nama kolom di CSV dan di skrip sudah sama.")
    exit()

print("[INFO] Menjalankan prediksi sentimen (dari model Anda) pada data sampel...")
df[PREDICTED_LABEL_COL] = df[TEXT_COL].apply(analisis_sentimen_text)

accuracy = accuracy_score(df[MANUAL_LABEL_COL], df[PREDICTED_LABEL_COL])
report = classification_report(df[MANUAL_LABEL_COL], df[PREDICTED_LABEL_COL], zero_division=0)
conf_matrix = confusion_matrix(df[MANUAL_LABEL_COL], df[PREDICTED_LABEL_COL], labels=['positif', 'negatif', 'netral'])

print("\n\n" + "="*50)
print("HASIL EVALUASI MODEL ANALISIS SENTIMEN ANDA")
print("="*50)
print(f"\nAKURASI KESELURUHAN: {accuracy:.2%}")
print("\nLAPORAN KLASIFIKASI:")
print(report)
print("="*50)

print("\n[INFO] Menampilkan Confusion Matrix...")
plt.figure(figsize=(8, 6))
sns.heatmap(conf_matrix, annot=True, fmt='d', cmap='Blues', 
            xticklabels=['positif', 'negatif', 'netral'], 
            yticklabels=['positif', 'negatif', 'netral'])
plt.title('Confusion Matrix', fontsize=16)
plt.ylabel('Label Aktual (Manual)', fontsize=12)
plt.xlabel('Label Prediksi (Model Anda)', fontsize=12)
plt.show()