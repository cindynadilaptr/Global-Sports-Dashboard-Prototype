import instaloader
import os

IG_USERNAME = "kovee.idn" 
SESSION_FILE = os.path.join(os.path.dirname(__file__), IG_USERNAME)

L = instaloader.Instaloader()

try:
    L.load_session_from_file(IG_USERNAME, SESSION_FILE)
    print(f"Session untuk user '{IG_USERNAME}' sudah ada. Tidak perlu login ulang.")

except FileNotFoundError:
    print("File session tidak ditemukan. Silakan login di terminal...")
    L.interactive_login(IG_USERNAME)  
    L.save_session_to_file(SESSION_FILE)
    
    print(f"Session berhasil disimpan ke file di lokasi: {SESSION_FILE}")