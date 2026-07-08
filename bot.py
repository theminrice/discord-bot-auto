import requests
import time
from datetime import datetime

# ==================== CONFIGURATION ====================
TOKEN_AKUN = "TOKEN_REDACTED "
CHANNEL_ID = "733050809314705458"
SERVER_FORWARD_ID = "1521338078407430158" # Channel server Anda untuk menerima terusan DM

PESAN = """
**SURG-E 3 <:WL:880251447470596157>   
SELL GO <:Arrow:850540193626193941>  **ORUHC<:Verified:1000267030550827128>**

Note: Not In Vend = <:Sold:1432438946184298566> <:Sold:1432438946184298566>"""
# =======================================================

headers = {
    "Authorization": TOKEN_AKUN,
    "Content-Type": "application/json"
}

def kirim_pesan(target_channel_id, konten):
    url = f"https://discord.com/api/v9/channels/{target_channel_id}/messages"
    payload = {"content": konten}
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        
        if response.status_code == 200:
            return True
            
        elif response.status_code == 429:
            data_respon = response.json()
            jeda_detik = data_respon.get("retry_after", 60)
            print(f"[RATE LIMIT] Menunggu {jeda_detik} detik...")
            time.sleep(jeda_detik)
            return kirim_pesan(target_channel_id, konten)
            
        else:
            print(f"[GAGAL] Status {response.status_code}: {response.text}")
            return False
            
    except Exception as e:
        print(f"[ERROR] Terjadi kesalahan: {e}")
        return False

def periksa_dan_teruskan_dm():
    """Mengambil daftar DM masuk terbaru dan meneruskannya ke server Anda"""
    url_dm_list = "https://discord.com/api/v9/users/@me/channels"
    waktu_sekarang = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        res_dm = requests.get(url_dm_list, headers=headers)
        if res_dm.status_code != 200:
            print(f"[{waktu_sekarang}] [FORWARD] Gagal mengambil daftar DM.")
            return
            
        dm_channels = res_dm.json()
        
        # Periksa pesan terakhir di 5 DM teratas
        for chat in dm_channels[:5]:
            if chat.get("type") != 1: # Pastikan ini DM personal
                continue
                
            channel_id = chat["id"]
            user_info = chat.get("recipients", [{}])[0]
            username = user_info.get("username", "Unknown")
            
            # Ambil pesan paling terakhir dari channel DM ini
            url_messages = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=1"
            res_msg = requests.get(url_messages, headers=headers)
            
            if res_msg.status_code == 200 and res_msg.json():
                last_msg = res_msg.json()[0]
                
                # Pastikan pesan terakhir BUKAN dari Anda sendiri (ID Akun Anda)
                if last_msg.get("author", {}).get("id") != "1437652796391292998":
                    konten_dm = last_msg.get("content", "")
                    
                    # Kirim laporan terusan ke server Anda
                    teks_terusan = f"📩 **[DM TERBARU DETEKSI]** dari **{username}** (Channel ID: `{channel_id}`):\n> {konten_dm}"
                    kirim_pesan(SERVER_FORWARD_ID, teks_terusan)
                    print(f"[{waktu_sekarang}] [FORWARD] Berhasil meneruskan DM dari {username}")
                    
    except Exception as e:
        print(f"[ERROR DM] Terjadi kesalahan saat membaca DM: {e}")

if __name__ == "__main__":
    waktu = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # 1. Jalankan pengiriman iklan otomatis
    if kirim_pesan(CHANNEL_ID, PESAN):
        print(f"[{waktu}] [IKLAN] Sukses terkirim.")
    else:
        print(f"[{waktu}] [IKLAN] Gagal kirim iklan.")
        
    # 2. Jalankan pembacaan DM (Otomatis diteruskan jika ada DM baru)
    periksa_dan_teruskan_dm()
