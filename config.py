# Konfigurasi untuk Web Scraping
# URL Target Utama
TARGET_URLS = {
    "kompas": {
        'type': 'single_category_pagination',
        'url': 'https://olahraga.kompas.com',
        'pagination_format': '/page/{}'},
    "bola": {
        'categories': {
            'sepak_bola_nasional': 'https://www.bola.com/',
            'ragam':'https://www.bola.com/ragam'}},
    "detik": {
        'type': 'hybrid_scroll_and_click',
        'categories': {
            'indeks': 'https://sport.detik.com/indeks'}}, 
    "indoor_kemenpora": {
        'type': 'hybrid_scroll_and_click', 
        'categories': {
            'berita': 'https://deputi4.kemenpora.go.id/berita',
            'artikel': 'https://deputi4.kemenpora.go.id/artikel'}}
}


# Parameter scraping
MAX_SCROLLS = 5  # Jumlah maksimal scroll ke bawah pada halaman dinamis
MAX_PAGES_PER_CATEGORY = 5  # Jumlah maksimal halaman yang akan diambil per kategori
SLEEP_TIME = 5   # Waktu jeda (detik) antar scroll

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
OUTPUT_CSV_PATH = 'data/berita_nasional_tersaring.csv'