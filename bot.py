import requests
from datetime import datetime

# ==================== CONFIGURATION ====================
TOKEN_AKUN = "TOKEN_REDACTED "
CHANNEL_ID = "1521338078407430158"
PESAN = "Sell surg-e 3 WL EACH AT ORUHC, STOCK 3K AND NEAR VEND"
# =======================================================

def kirim_pesan():
    url = f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages"
    
    headers = {
        "Authorization": TOKEN_AKUN,
        "Content-Type": "application/json"
    }
    
    payload = {
        "content": PESAN
    }
    
    waktu_sekarang = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            print(f"[{waktu_sekarang}] [BERHASIL] Pesan otomatis terkirim.")
        elif response.status_code == 429:
            print(f"[{waktu_sekarang}] [RATE LIMIT] Terlalu banyak request. Discord meminta jeda.")
        else:
            print(f"[{waktu_sekarang}] [GAGAL] Status {response.status_code}: {response.text}")
            
    except Exception as e:
        print(f"[{waktu_sekarang}] [ERROR] Terjadi kesalahan: {e}")

if __name__ == "__main__":
    kirim_pesan()
