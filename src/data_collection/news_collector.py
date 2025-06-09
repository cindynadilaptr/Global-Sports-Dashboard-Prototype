import feedparser
import pandas as pd
from config import ESPN_RSS_URL, BBC_SPORT_RSS_URL

def fetch_all_news():

    all_news_list = []

    # Mengambil data dari ESPN
    try:
        feed_espn = feedparser.parse(ESPN_RSS_URL)
        for entry in feed_espn.entries:
            all_news_list.append({
                'sumber': 'ESPN',
                'judul': entry.title,
                'link': entry.link,
                'published': entry.get('published', 'Tidak ada tanggal')
            })
        print("Berhasil mengambil berita dari ESPN.")
    except Exception as e:
        pass

    # Mengambil data dari BBC Sport
    try:
        feed_bbc = feedparser.parse(BBC_SPORT_RSS_URL)
        for entry in feed_bbc.entries:
            all_news_list.append({
                'sumber': 'BBC Sport',
                'judul': entry.title,
                'link': entry.link,
                'published': entry.get('published', 'Tidak ada tanggal')
            })
        print("Berhasil mengambil berita dari BBC Sport.")
    except Exception as e:
        pass

    # Mengubah list menjadi DataFrame Pandas
    if not all_news_list:
        return pd.DataFrame() 

    df = pd.DataFrame(all_news_list)
    print(f"Total {len(df)} berita berhasil dikumpulkan.")
    
    # Mengembalikan hasil
    return df