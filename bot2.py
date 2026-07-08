import requests
import time
from datetime import datetime

# ==================== CONFIGURATION ====================
TOKEN_AKUN = "TOKEN_REDACTED "
CHANNEL_ID = "733050809314705458"
PESAN = "Sell AT QWIFO
Legal brief 180:WL~6:  

AT QWIFO"
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
            print(f"[{waktu_sekarang}] [BERHASIL] Pesan otomatis terkirim ke channel.")
            return True
            
        elif response.status_code == 429:
            # Mengambil informasi berapa lama harus menunggu dari respon Discord
            data_respon = response.json()
            jeda_detik = data_respon.get("retry_after", 60) # Default 60 detik jika tidak ada data
            
            print(f"[{waktu_sekarang}] [RATE LIMIT] Terkena limit. Menunggu {jeda_detik} detik sebelum mencoba lagi...")
            time.sleep(jeda_detik)
            
            # Mencoba mengirim ulang sekali lagi setelah jeda selesai
            return kirim_pesan()
            
        else:
            print(f"[{waktu_sekarang}] [GAGAL] Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"[{waktu_sekarang}] [ERROR] Terjadi kesalahan: {e}")
        return False

if __name__ == "__main__":
    kirim_pesan()
