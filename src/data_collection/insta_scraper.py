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
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Gagal mengambil profil IG: {e}")
        return None

def get_post_comments(post_id: str, access_token: str, permalink: str):
    url = f"https://graph.facebook.com/{API_VERSION}/{post_id}/comments"
    params = {"fields": "id,text,username,timestamp", "access_token": access_token, "limit": 100}
    all_comments = []
    try:
        while url:
            response = requests.get(url, params=params).json()
            comments_on_page = response.get('data', [])
            for comment in comments_on_page:
                comment['post_id'] = post_id
                comment['permalink'] = permalink
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
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # --- AMBIL PROFIL ---
    user_profile = get_user_profile(ig_user_id, access_token)
    if not user_profile:
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    # --- AMBIL POSTINGAN ---
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
        return pd.DataFrame(), pd.DataFrame(), pd.DataFrame()

    df_posts['timestamp'] = pd.to_datetime(df_posts['timestamp'], errors='coerce').dt.strftime('%d/%m/%Y')
    df_posts['id'] = df_posts['id'].astype(str)
    df_posts['like_count'] = df_posts['like_count'].fillna(0)
    df_posts['comments_count'] = df_posts['comments_count'].fillna(0)

    followers = user_profile.get("followers_count", 1) or 1
    df_posts['engagement'] = ((df_posts['like_count'] + df_posts['comments_count']) / followers) * 100

    # Hitung total engagement akun
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

    # Simpan profile_df juga
    os.makedirs(os.path.dirname(config.OUTPUT_PATH_IG_PROFILE), exist_ok=True)
    profile_df.to_csv(config.OUTPUT_PATH_IG_PROFILE, index=False, encoding='utf-8')

    # --- AMBIL KOMENTAR ---
    all_comments_total = []
    print("\n>>> Memulai pengambilan komentar untuk setiap post...")
    for index, post_row in df_posts.iterrows():
        post_id = post_row['id']
        permalink = post_row.get('permalink', '')
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
