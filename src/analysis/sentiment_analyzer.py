import os
import sys
import pandas as pd
from textblob import TextBlob
from sklearn.metrics import classification_report, confusion_matrix, accuracy_score
import emoji

# Setup path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from SentiStrength_ID.sentistrength_id import sentistrength, config
from src.analysis.text_preprocessor import preprocess_text, preprocess_light, is_english

# Inisialisasi SentiStrength_ID
senti = sentistrength(config)

POSITIVE_EMOJIS = {"👍", "❤️", "🔥", "😁", "😊", "😎", "🎉", "✨", "😍", "🙌", "💯"}

def has_positive_emoji(text: str) -> bool:
    return any(e in text for e in POSITIVE_EMOJIS)

def analisis_sentimen_text(text: str) -> str:
    if not isinstance(text, str) or text.strip() == "":
        return 'netral'

    # SentiStrength_ID
    raw_text = preprocess_light(text)
    scores = senti.main(raw_text)
    sk_id = scores['max_positive'] + scores['max_negative']
    if scores['max_positive'] >= 2 and scores['max_positive'] > abs(scores['max_negative']):
        label_senti = 'positif'
    elif scores['max_negative'] <= -2 and abs(scores['max_negative']) > scores['max_positive']:
        label_senti = 'negatif'
    else:
        label_senti = 'netral'

    # TextBlob
    cleaned_text = preprocess_text(text)
    try:
        polarity = TextBlob(cleaned_text).sentiment.polarity
    except:
        polarity = 0

    if polarity > 0.02:
        label_blob = 'positif'
    elif polarity < -0.02:
        label_blob = 'negatif'
    else:
        label_blob = 'netral'

    # Fallback Emoji Detection
    if has_positive_emoji(text) and scores['max_negative'] >= -2:
        label_emoji = 'positif'
    else:
        label_emoji = 'netral'

    # Voting Hybrid
    if label_senti == label_blob:
        final_label = label_senti
    elif is_english(text):
        final_label = label_blob
    elif label_emoji == 'positif':
        final_label = 'positif'
    elif label_blob == 'positif' and scores['max_negative'] >= -3:
        final_label = 'positif'
    elif label_blob == 'negatif' and scores['max_positive'] <= 3:
        final_label = 'negatif'
    elif label_senti != 'netral':
        final_label = label_senti
    else:
        final_label = label_blob

    # LOG DETAIL PREDIKSI 
    print(f"[LOG] TEXT: {text}")
    print(f"      SentiStrength: max_pos={scores['max_positive']} max_neg={scores['max_negative']} -> {label_senti}")
    print(f"      TextBlob polarity={polarity:.3f} -> {label_blob}")
    print(f"      Emoji Detected: {has_positive_emoji(text)} -> {label_emoji}")
    print(f"      Final Sentiment: {final_label}")
    print("-" * 60)

    return final_label

def analisis_sentimen_dataframe(df: pd.DataFrame, text_column: str) -> pd.DataFrame:
    df = df.copy()
    df['sentimen'] = df[text_column].apply(analisis_sentimen_text)
    return df

# TESTING & EVALUASI 
if __name__ == "__main__":
    sample_data = pd.DataFrame({
        "text": [
            "Acara ini sangat keren dan bermanfaat!",
            "Gak suka sama sistemnya, buruk banget.",
            "Biasa aja sih, nothing special.",
            "This is an amazing sports program!",
            "Sangat kecewa dengan pelayanan kemarin.",
            "Good job team, proud of the result!",
            "Yaudah lah, gpp aja.",
            "gk suka bgt sama pelayanannya",
            "KERENNN BANGETTT",
            "mantap 👍🔥",
            "This game keren bgt sih!"
        ]
    })

    print("=== TESTING MANUAL ===")
    hasil = analisis_sentimen_dataframe(sample_data, text_column='text')
    print(hasil)