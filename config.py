# Konfigurasi untuk Web Scraping
import os
from src.data_collection.national_news_scraper import (
scrape_from_kompas,
scrape_from_bola,
scrape_from_detik,
scrape_from_kemenpora,
scrape_from_pelayanan,
scrape_from_pembudayaan,
scrape_from_presor,
scrape_from_indoor)

# URL Target Utama
TARGET_URLS = {
    "kompas": {
        'scraper_function': scrape_from_kompas,
        'type': 'single_category_pagination',
        'url': 'https://olahraga.kompas.com',
        'pagination_format': '/page/{}'},
    "bola": {
        'scraper_function': scrape_from_bola,
        'categories': {
            'sepak_bola_nasional': 'https://www.bola.com/',
            'ragam':'https://www.bola.com/ragam'}},
    "detik": {
        'scraper_function': scrape_from_detik,
        'type': 'hybrid_scroll_and_click',
        'categories': {
            'indeks': 'https://sport.detik.com/indeks'}},
    "kemenpora": {
        'scraper_function': scrape_from_kemenpora,
        'type': 'hybrid_scroll_and_click',
        'categories': {
            'berita': 'https://www.kemenpora.go.id/berita'}},
    "pelayanan_kemenpora": {
        'scraper_function': scrape_from_pelayanan,
        'type': 'hybrid_scroll_and_click',
        'categories': {
            'berita': 'https://deputi1.kemenpora.go.id/berita',
            'artikel': 'https://deputi1.kemenpora.go.id/artikel'}},
    "pembudayaan_kemenpora": {
        'scraper_function': scrape_from_pembudayaan,
        'type': 'hybrid_scroll_and_click',
        'categories': {
            'berita': 'https://deputi2.kemenpora.go.id/berita',
            'artikel': 'https://deputi2.kemenpora.go.id/artikel'}},
    "presor_kemenpora": {
        'scraper_function': scrape_from_presor,
        'type': 'hybrid_scroll_and_click',
        'categories': {
            'berita': 'https://deputi3.kemenpora.go.id/berita',
            'artikel': 'https://deputi3.kemenpora.go.id/artikel'}},
    "indoor_kemenpora": {
        'scraper_function': scrape_from_indoor,
        'type': 'hybrid_scroll_and_click',
        'categories': {
            'berita': 'https://deputi4.kemenpora.go.id/berita',
            'artikel': 'https://deputi4.kemenpora.go.id/artikel'}}

}

# Daftar Sumber Internal
INTERNAL_SOURCES_NAMES = ['kemenpora', 'pelayanan_kemenpora', 'pembudayaan_kemenpora', 'presor_kemenpora', 'indoor_kemenpora']

# Parameter scraping
MAX_SCROLLS = 5 # Jumlah maksimal scroll ke bawah pada halaman dinamis
MAX_PAGES_PER_CATEGORY = 10 # Jumlah maksimal halaman yang akan diambil per kategori
SLEEP_TIME = 5 # Waktu jeda (detik) antar scroll


# Konfigurasi untuk Filtering Berita
KATA_KUNCI_WAJIB = [
    'sponsor', 'investasi', 'bisnis', 'regulasi', 'kebijakan',
    'pembangunan', 'venue', 'stadion', 'apparel', 'kontrak',
    'hak siar', 'sport tourism', 'umkm olahraga', 'liga profesional', 'dbon'
]

KATA_KUNCI_NEGATIF = [
    'skor akhir', 'hasil pertandingan', 'klasemen sementara', 'jadwal pertandingan',
    'cedera pemain', 'prediksi skor', 'live streaming', 'susunan pemain'
]

OUTPUT_PATH_INTERNAL = 'data/hasil_monitoring_internal.csv'
OUTPUT_PATH_INDUSTRY = 'data/hasil_monitoring_industri.csv'
OUTPUT_PATH_IG_PROFILE = 'data/instagram_profile_info.csv'
OUTPUT_PATH_IG_POSTS = 'data/instagram_posts_performance.csv'
OUTPUT_PATH_IG_COMMENTS = 'data/instagram_comments_sentiment.csv'

# Konfigurasi API Instagram
ACCESS_TOKEN = os.getenv('IG_ACCESS_TOKEN')
USER_ID = {'personal': '17841406566514449'}

# Konfigurasi Google Cloud & Google Sheets
GOOGLE_SHEET_NAME = "Dashboard_Monitoring_Industri_Olahraga"  

# Path hasil Trending Keywords
OUTPUT_PATH_KEYWORDS_INTERNAL = 'data/keywords_internal.csv'
OUTPUT_PATH_KEYWORDS_INDUSTRY = 'data/keywords_industry.csv'
OUTPUT_PATH_KEYWORDS_POSTS = 'data/keywords_posts.csv'
OUTPUT_PATH_KEYWORDS_COMMENTS = 'data/keywords_comments.csv'

# Tambahkan nama tab baru ke GCP_SHEET_TABS
GCP_SHEET_TABS = {
    "internal": "internal_kemenpora",
    "industry": "industri_olahraga",
    "profile": "profile_ig",
    "posts": "caption_ig",
    "comments": "komentar_ig",
    "keywords_internal": "keywords_internal",
    "keywords_industry": "keywords_industry",
    "keywords_posts": "keywords_posts",
    "keywords_comments": "keywords_comments"
}