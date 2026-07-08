import requests
from datetime import datetime

# ==================== CONFIGURATION ====================
TOKEN_AKUN = "TOKEN_REDACTED "
CHANNEL_IKLAN_ID = "733050809314705458"
SERVER_FORWARD_ID = "1521338078407430158" # Channel di server Anda untuk menerima terusan DM

PESAN_IKLAN = """
**SURG-E 3 <:WL:880251447470596157>   
SELL GO <:Arrow:850540193626193941>  **QWIFO<:Verified:1000267030550827128>**
SEll DROPPED UR RATE DM ME
Note: Not In Vend  = <:Sold:1432438946184298566> <:Sold:1432438946184298566>"""
# =======================================================

headers = {
    "Authorization": TOKEN_AKUN,
    "Content-Type": "application/json"
}

def kirim_pesan(channel_id, konten):
    """Fungsi untuk mengirim pesan ke Discord"""
    url = f"https://discord.com/api/v9/channels/{channel_id}/messages"
    payload = {"content": konten}
    try:
        res = requests.post(url, json=payload, headers=headers)
        if res.status_code == 429:
            import time
            jeda = res.json().get("retry_after", 5)
            time.sleep(jeda)
            return kirim_pesan(channel_id, konten)
        return res.status_code == 200
    except Exception as e:
        print(f"[ERROR SEND] {e}")
        return False

def periksa_dan_teruskan_dm():
    """Mengambil daftar DM masuk terbaru dan meneruskannya ke server Anda"""
    # Mengambil daftar chat/DM terakhir (Private Channels)
    url_dm_list = "https://discord.com/api/v9/users/@me/channels"
    waktu_sekarang = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    try:
        res_dm = requests.get(url_dm_list, headers=headers)
        if res_dm.status_code != 200:
            print(f"[{waktu_sekarang}] [FORWARD] Gagal mengambil daftar DM. Status: {res_dm.status_code}")
            return
            
        dm_channels = res_dm.json()
        
        # Periksa pesan terakhir di setiap obrolan DM (maksimal 5 DM teratas agar hemat limit)
        for chat in dm_channels[:5]:
            channel_id = chat["id"]
            
            # Jika ini adalah DM grup atau tipenya bukan DM personal (type 1 = DM personal)
            if chat.get("type") != 1:
                continue
                
            # Ambil detail user pengirim DM
            user_info = chat.get("recipients", [{}])[0]
            username = user_info.get("username", "Unknown")
            
            # Ambil pesan paling terakhir dari channel DM ini
            url_messages = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=1"
            res_msg = requests.get(url_messages, headers=headers)
            
            if res_msg.status_code == 200 and res_msg.json():
                last_msg = res_msg.json()[0]
                # Pastikan pesan terakhir BUKAN dari Anda sendiri
                if last_msg.get("author", {}).get("id") != "1076319992498372680":
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
    if kirim_pesan(CHANNEL_IKLAN_ID, PESAN_IKLAN):
        print(f"[{waktu}] [IKLAN] Sukses terkirim.")
    else:
        print(f"[{waktu}] [IKLAN] Gagal kirim iklan.")
        
    # 2. Cek apakah ada DM baru masuk untuk diteruskan
    periksa_dan_teruskan_dm()
