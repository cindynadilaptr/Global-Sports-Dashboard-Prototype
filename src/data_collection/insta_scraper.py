import requests
import pandas as pd
import time
import sys
import os
script_dir = os.path.dirname(__file__)
project_root = os.path.abspath(os.path.join(script_dir, '..', '..'))
sys.path.append(project_root)
import config 

API_VERSION = "v23.0"

def get_user_profile(user_id: str, access_token: str):
    print(f"Mengambil info profil untuk User ID: {user_id}")
    url = f"https://graph.facebook.com/{API_VERSION}/{user_id}"
    params = {
        "fields": "id,username,media_count,followers_count",
        "access_token": access_token
    }
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Gagal mengambil profil IG: {e}")
        return None

def get_instagram_posts(user_id: str, access_token: str, limit: int):
    print(f"Mengambil {limit} postingan terakhir")
    url = f"https://graph.facebook.com/{API_VERSION}/{user_id}/media"
    params = {"fields": "id,caption,like_count,comments_count,permalink,timestamp", "limit": limit, "access_token": access_token}
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        posts = response.json().get('data', [])
        print(f"Berhasil mendapatkan {len(posts)} postingan.")
        return pd.DataFrame(posts)
    except Exception as e:
        print(f"Gagal mengambil postingan IG: {e}")
        return pd.DataFrame()

def get_post_comments(post_id: str, access_token: str):
    url = f"https://graph.facebook.com/{API_VERSION}/{post_id}/comments"
    params = {"fields": "id,text,username,timestamp", "access_token": access_token, "limit": 100}
    all_comments = []
    try:
        while url:
            response = requests.get(url, params=params).json()
            comments_on_page = response.get('data', [])
            all_comments.extend(comments_on_page)
            if 'paging' in response and 'next' in response['paging']:
                url = response['paging']['next']
                params = {}
            else:
                break
    except Exception:
        pass
    return all_comments

def scrape_from_instagram_api(target_account_key: str = "personal"):
    print(f"\n=== MEMULAI SCRAPING INSTAGRAM untuk: @{target_account_key} ===")
    
    access_token = config.ACCESS_TOKEN
    ig_user_id = config.USER_ID.get(target_account_key)
    
    if not ig_user_id or "NANTI" in ig_user_id:
        print(f"ID Instagram untuk '{target_account_key}' tidak valid di config.")
        return pd.DataFrame(), pd.DataFrame()

    # Ambil semua postingan tanpa limit
    all_posts = []
    url = f"https://graph.facebook.com/{API_VERSION}/{ig_user_id}/media"
    params = {
        "fields": "id,caption,like_count,comments_count,permalink,timestamp",
        "access_token": access_token,
        "limit": 100
    }
    while url:
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            posts = data.get('data', [])
            all_posts.extend(posts)
            if 'paging' in data and 'next' in data['paging']:
                url = data['paging']['next']
                params = {}
            else:
                break
        except Exception as e:
            print(f"Gagal mengambil postingan IG: {e}")
            break

    df_posts = pd.DataFrame(all_posts)
    if df_posts.empty:
        return pd.DataFrame(), pd.DataFrame()

    all_comments_total = []
    print("\n>>> Memulai pengambilan komentar untuk setiap post...")
    for index, post_row in df_posts.iterrows():
        post_id = post_row['id']
        comments = get_post_comments(post_id, access_token)
        for comment in comments:
            comment['post_id'] = post_id
            comment['post_caption'] = post_row.get('caption', '')
        all_comments_total.extend(comments)
        time.sleep(0.5)

    df_comments = pd.DataFrame(all_comments_total)
    print(f"\nTotal {len(df_comments)} komentar berhasil dikumpulkan.")
    return df_posts, df_comments

# BLOK UNTUK TESTING LANGSUNG FILE INI 
if __name__ == '__main__':
    scrape_from_instagram_api()
        