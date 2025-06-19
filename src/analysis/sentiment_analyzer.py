import os
import sys
import pandas as pd
from textblob import TextBlob

# Setup path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))
from SentiStrength_ID.sentistrength_id import sentistrength, config
from src.analysis.text_preprocessor import preprocess_text, preprocess_light

# Inisialisasi SentiStrength_ID
senti = sentistrength(config)

def analisis_sentimen_text(text: str) -> str:
    if not isinstance(text, str) or text.strip() == "":
        return 'netral'

    # SentiStrength_ID
    raw_text = preprocess_light(text)
    scores = senti.main(raw_text)
    if scores['max_positive'] > abs(scores['max_negative']):
        label_senti = 'positif'
    elif scores['max_negative'] < 0:
        label_senti = 'negatif'
    else:
        label_senti = 'netral'

    # TextBlob
    cleaned_text = preprocess_text(text)
    try:
        polarity = TextBlob(cleaned_text).sentiment.polarity
    except:
        polarity = 0
    if polarity > 0.2:
        label_blob = 'positif'
    elif polarity < -0.2:
        label_blob = 'negatif'
    else:
        label_blob = 'netral'

    # === VOTING Hybrid ===
    if label_senti == label_blob:
        return label_senti  
    elif label_blob != 'netral':
        return label_blob 
    else:
        return label_senti 

def analisis_sentimen_dataframe(df: pd.DataFrame, text_column: str) -> pd.DataFrame:
    df = df.copy()
    df['sentimen'] = df[text_column].apply(analisis_sentimen_text)
    return df

# Testing manual
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

    hasil = analisis_sentimen_dataframe(sample_data, text_column='text')
    print(hasil)
