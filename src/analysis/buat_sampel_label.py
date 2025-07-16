import pandas as pd
from transformers import pipeline
from tqdm import tqdm

INPUT_FILE = 'data/instagram_comments_sentiment.csv'
OUTPUT_FILE = 'data/evaluasi_sentimen_database.csv'
TEXT_COLUMN = 'text'
N_SAMPLES = 300

print(f"[INFO] Memuat dataset asli dari: {INPUT_FILE}")
try:
    df_full = pd.read_csv(INPUT_FILE)
except FileNotFoundError:
    print(f"[ERROR] File dataset tidak ditemukan. Pastikan path '{INPUT_FILE}' benar.")
    exit()

if TEXT_COLUMN not in df_full.columns:
    print(f"[ERROR] Kolom '{TEXT_COLUMN}' tidak ditemukan di dalam file.")
    exit()

print(f"Dataset asli berisi {len(df_full)} komentar.")
if len(df_full) < N_SAMPLES:
    print(f"[WARNING] Jumlah data ({len(df_full)}) lebih sedikit dari sampel yang diinginkan ({N_SAMPLES}). Semua data akan digunakan.")
    df_sample = df_full.copy()
else:
    print(f"Mengambil {N_SAMPLES} sampel acak untuk di-labeli...")
    df_sample = df_full.sample(n=N_SAMPLES, random_state=42)

print("\n[INFO] Memuat Model Sentimen Multibahasa...")
print("[CATATAN] Proses download model baru mungkin terjadi jika ini pertama kali dijalankan.")
classifier = pipeline(
    "sentiment-analysis",
    model="lxyuan/distilbert-base-multilingual-cased-sentiments-student",
    return_all_scores=False
)

print(f"\n[INFO] Memulai proses labeling untuk {len(df_sample)} data...")
predicted_labels = []
tqdm.pandas(desc="Labeling Progress")

label_map = {'positive': 'positif', 'negative': 'negatif', 'neutral': 'netral'}

for text in df_sample[TEXT_COLUMN].progress_apply(str):
    if not text.strip():
        predicted_labels.append(None)
        continue
    
    result = classifier(text)
    model_label = result[0]['label']
    final_label = label_map.get(model_label, 'netral')
    predicted_labels.append(final_label)

df_sample['label_otomatis'] = predicted_labels

final_df = df_sample[[TEXT_COLUMN, 'label_otomatis']]
final_df.to_csv(OUTPUT_FILE, index=False)

print(f"\n[SUKSES] Proses sampling dan labeling selesai.")
print(f"Hasilnya (sebanyak {len(final_df)} baris) telah disimpan di: {OUTPUT_FILE}")