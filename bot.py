import os
import requests
import time
from datetime import datetime

# ============ AMBIL DARI ENV (GITHUB SECRETS) ============
TOKEN_AKUN = os.environ.get("TOKEN_AKUN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

# 2 Channel ID tujuan yang berbeda
SERVER_FORWARD_ID_1 = os.environ.get("SERVER_FORWARD_ID_1")
SERVER_FORWARD_ID_2 = os.environ.get("SERVER_FORWARD_ID_2")

if not TOKEN_AKUN or not CHANNEL_ID or not SERVER_FORWARD_ID_1 or not SERVER_FORWARD_ID_2:
    raise Exception("Environment variable ada yang kosong! Cek kembali Secrets Anda.")

# Pesan untuk Channel ID Utama
PESAN_UTAMA = """
**SURG E 3 <:WL:880251447470596157>
SELL GO <:Arrow:850540193626193941>  **ORUHC<:Verified:1000267030550827128>**
Note: Not In Vend = <:Sold:1432438946184298566> <:Sold:1432438946184298566>"""

# Pesan berbeda yang akan dikirim ke SERVER_FORWARD_ID_2 (misal: Log / Pesan Lain)
PESAN_KHUSUS_CHANNEL_2 = """
**SELL MEGAPHONE 2000  **<:WL:880251447470596157>  OR 20 <:DL:880251434380165130> 
AT <:Arrow:850540193626193941> ORUHC
Note: Not In Vend = <:Sold:1432438946184298566> <:Sold:1432438946184298566>**"""

headers = {
    "Authorization": TOKEN_AKUN,
    "Content-Type": "application/json"
}

def kirim_pesan(target_channel_id, konten):
    url = f"https://discord.com/api/v9/channels/{target_channel_id.strip()}/messages"
    payload = {"content": konten}
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            return True
        elif response.status_code == 429:
            data = response.json()
            wait = data.get("retry_after", 60)
            print(f"[RATE LIMIT] Tunggu {wait}s")
            time.sleep(wait)
            return kirim_pesan(target_channel_id, konten)
        else:
            print(f"[GAGAL] {response.status_code} – {response.text}")
            with open("error_log.txt", "a") as f:
                f.write(f"{datetime.now()} - Gagal kirim: {response.text}\n")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def periksa_dan_teruskan_dm():
    res_me = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
    my_id = res_me.json().get("id") if res_me.status_code == 200 else None

    url_dm = "https://discord.com/api/v9/users/@me/channels"
    try:
        res = requests.get(url_dm, headers=headers)
        if res.status_code != 200:
            print(f"[FORWARD] Gagal ambil DM – {res.status_code}")
            return
        
        dms = res.json()
        forwarded = 0
        
        for chat in dms[:30]:
            if chat.get("type") != 1:  
                continue
            
            ch_id = chat["id"]
            recipients = chat.get("recipients", [{}])
            if not recipients:
                continue
                
            user = recipients[0]
            name = user.get("username", "Unknown")
            is_user_bot = user.get("bot", False)  

            url_msg = f"https://discord.com/api/v9/channels/{ch_id}/messages?limit=3"
            r_msg = requests.get(url_msg, headers=headers)
            
            if r_msg.status_code == 200 and r_msg.json():
                messages = r_msg.json()
                target_msg = None
                
                for msg in messages:
                    author = msg.get("author", {})
                    author_id = author.get("id")
                    is_author_bot = author.get("bot", False)

                    if author_id == my_id or is_author_bot or is_user_bot:
                        continue
                    
                    konten = msg.get("content", "")
                    if konten.strip():
                        target_msg = konten
                        break 
                
                if target_msg:
                    teks = f"📩 DM DARI MANUSIA **{name}** (`{ch_id}`):\n> {target_msg}"
                    
                    # Teruskan DM ke Channel 1 dan Channel 2 (bisa dikirim dengan teks sama atau dibedakan)
                    kirim_pesan(SERVER_FORWARD_ID_1, teks)
                    kirim_pesan(SERVER_FORWARD_ID_2, f"📢 **[Log Terusan DM]**\n{teks}")
                            
                    print(f"[FORWARD] DM terbaru dari {name} berhasil diteruskan ke kedua channel.")
                    forwarded += 1
                    break  

        if forwarded == 0:
            print("[FORWARD] Tidak ada DM baru dari manusia.")
            
    except Exception as e:
        print(f"[ERROR DM] {e}")

if __name__ == "__main__":
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    test = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
    if test.status_code != 200:
        print(f"[{now}] TOKEN TIDAK VALID atau REVOKED! Stop.")
        exit(1)
        
    # Kirim iklan ke channel utama
    if kirim_pesan(CHANNEL_ID, PESAN_UTAMA):
        print(f"[{now}] Iklan utama sukses.")
    else:
        print(f"[{now}] Iklan utama gagal.")
        
    # Kirim pesan berbeda ke SERVER_FORWARD_ID_2 (opsional, misal pesan inisialisasi)
    kirim_pesan(SERVER_FORWARD_ID_2, PESAN_KHUSUS_CHANNEL_2)
        
    # Jalankan pengecekan DM
    periksa_dan_teruskan_dm()
