import re, string, emoji
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from Sastrawi.Stemmer.StemmerFactory import StemmerFactory

# Init
factory = StemmerFactory()
stemmer = factory.create_stemmer()
stop_words_id = set(stopwords.words('indonesian')) - {'tidak', 'kurang', 'bukan'}
stop_words_en = set(stopwords.words('english')) - {'not', 'no'}

common_english_words = set([
    "good", "great", "best", "bad", "worst", "love", "like", "hate", "awesome", "cool",
    "amazing", "sucks", "nice", "team", "support", "win", "lose", "goal", "champion"
])

slang_dict = {
    "gk": "tidak", "gak": "tidak", "ga": "tidak", "nggak": "tidak", "bgt": "banget", "tp": "tapi",
    "tdk": "tidak", "sy": "saya", "aq": "aku", "pdhl": "padahal", "klo": "kalau",
    "sm": "sama", "bbrp": "beberapa", "dr": "dari", "lg": "lagi"
}

ambiguous_phrases = {
    "biasa aja sih": "biasa",
    "nothing special": "biasa",
    "so-so": "biasa",
    "meh": "biasa",
    "yaudah lah": "biasa",
    "gpp aja": "biasa",
    "ya gapapa": "biasa"
}

def normalize_slang(text):
    return ' '.join([slang_dict.get(word, word) for word in text.split()])

def normalize_phrases(text):
    for phrase, replacement in ambiguous_phrases.items():
        text = text.replace(phrase, replacement)
    return text

def remove_repeated_chars(text):
    return re.sub(r'(\w)\1{2,}', r'\1', text)

def remove_emojis(text):
    return emoji.replace_emoji(text, replace='')

def preprocess_text(text: str) -> str:
    if not isinstance(text, str):
        return ""

    text = text.lower()
    text = remove_emojis(text)
    text = normalize_phrases(text)
    text = normalize_slang(text)
    text = remove_repeated_chars(text)
    text = re.sub(r"http\S+|www\S+", '', text)
    text = re.sub(f"[{re.escape(string.punctuation)}]", "", text)
    tokens = word_tokenize(text)

    cleaned_tokens = []
    for word in tokens:
        if not word.isalpha():
            continue
        if word in common_english_words:
            cleaned_tokens.append(word)
        elif word in stop_words_id or word in stop_words_en:
            continue
        else:
            cleaned_tokens.append(stemmer.stem(word))

    return " ".join(cleaned_tokens)

def preprocess_light(text: str) -> str:
    if not isinstance(text, str):
        return ""
    text = text.lower()
    text = remove_emojis(text)
    text = normalize_phrases(text)
    text = normalize_slang(text)
    text = re.sub(r"http\S+|www\S+", '', text)
    return text
