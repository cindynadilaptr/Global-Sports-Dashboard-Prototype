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
        "fields": "id,username,media_count,followers_count,follows_count",
        "access_token": access_token
    }

    try:
        response = requests.get(url, params=params)
        print(f"[DEBUG] Status Code: {response.status_code}")
        print(f"[DEBUG] Response: {response.text}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as e:
        print(f"[ERROR] HTTP Error saat mengambil profil: {e}")
    except Exception as e:
        print(f"[ERROR] Gagal mengambil profil IG: {e}")
    return None

def get_post_comments(post_id: str, access_token: str, permalink: str):
    url = f"https://graph.facebook.com/{API_VERSION}/{post_id}/comments"
    params = {"fields": "id,text,username,timestamp", "access_token": access_token, "limit": 100}
    all_comments = []
    try:
        while url:
            response = requests.get(url, params=params)
            data = response.json()
            comments = data.get('data', [])
            for comment in comments:
                comment['post_id'] = post_id
                comment['permalink'] = permalink
            all_comments.extend(comments)
            if 'paging' in data and 'next' in data['paging']:
                url = data['paging']['next']
                params = {}  
            else:
                break
    except Exception as e:
        print(f"[WARNING] Gagal ambil komentar dari post {post_id}: {e}")
    return all_comments

def scrape_from_instagram_api(target_account_key: str = "personal"):
    print(f"\n=== MEMULAI SCRAPING INSTAGRAM untuk: @{target_account_key} ===")

    access_token = config.ACCESS_TOKEN
    ig_user_id = config.USER_ID.get(target_account_key)

    if not ig_user_id or "NANTI" in ig_user_id:
        print(f"[ERROR] USER_ID untuk '{target_account_key}' tidak valid di config.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    user_profile = get_user_profile(ig_user_id, access_token)
    if not user_profile:
        print("[STOP] Tidak bisa lanjut karena profil tidak ditemukan.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    print("\nMengambil daftar postingan...")
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
            data = response.json()
            response.raise_for_status()
            posts = data.get('data', [])
            all_posts.extend(posts)
            if 'paging' in data and 'next' in data['paging']:
                url = data['paging']['next']
                params = {}  
            else:
                break
        except Exception as e:
            print(f"[ERROR] Gagal ambil postingan: {e}")
            break

    df_posts = pd.DataFrame(all_posts)
    if df_posts.empty:
        print("[INFO] Tidak ada postingan ditemukan.")
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    df_posts['timestamp'] = pd.to_datetime(df_posts['timestamp'], errors='coerce').dt.strftime('%d/%m/%Y')
    df_posts['like_count'] = df_posts['like_count'].fillna(0)
    df_posts['comments_count'] = df_posts['comments_count'].fillna(0)
    df_posts['id'] = df_posts['id'].astype(str)

    followers = user_profile.get("followers_count", 1) or 1
    df_posts['engagement'] = ((df_posts['like_count'] + df_posts['comments_count']) / followers) * 100

    total_likes = df_posts['like_count'].sum()
    total_comments = df_posts['comments_count'].sum()
    total_posts = len(df_posts)
    account_engagement = ((total_likes + total_comments) / (followers * total_posts)) * 100 if total_posts else 0

    profile_df = pd.DataFrame([{
        "id": user_profile.get("id"),
        "username": user_profile.get("username"),
        "followers_count": user_profile.get("followers_count"),
        "following_count": user_profile.get("follows_count"),
        "media_count": user_profile.get("media_count"),
        "total_likes": total_likes,
        "total_comments": total_comments,
        "account_engagement": round(account_engagement, 2)
    }])

    os.makedirs(os.path.dirname(config.OUTPUT_PATH_IG_PROFILE), exist_ok=True)
    profile_df.to_csv(config.OUTPUT_PATH_IG_PROFILE, index=False, encoding='utf-8')
    print(f"[SAVED] Data profil IG disimpan di {config.OUTPUT_PATH_IG_PROFILE}")

    print("\nMulai mengambil komentar dari tiap post...")
    all_comments_total = []
    for index, row in df_posts.iterrows():
        post_id = row['id']
        permalink = row.get('permalink', '')
        comments = get_post_comments(post_id, access_token, permalink)
        all_comments_total.extend(comments)
        time.sleep(0.5)

    df_comments = pd.DataFrame(all_comments_total)
    if not df_comments.empty:
        df_comments['id'] = df_comments['id'].astype(str)
        df_comments['timestamp'] = pd.to_datetime(df_comments['timestamp'], errors='coerce').dt.strftime('%d/%m/%Y')

    print(f"\nTotal {len(df_comments)} komentar berhasil dikumpulkan.")

    return profile_df, df_posts, df_comments


if __name__ == '__main__':
    scrape_from_instagram_api()
