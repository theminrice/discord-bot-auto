import os
import requests
import time
from datetime import datetime

# ============ AMBIL DARI ENV (GITHUB SECRETS) ============
TOKEN_AKUN = os.environ.get("BOT2_TOKEN")
CHANNEL_ID = os.environ.get("CHANNEL_PROMOSI_1")
SERVER_FORWARD_ID_2 = os.environ.get("CHANNEL_PROMOSI_2")
SERVER_FORWARD_ID_1 = os.environ.get("SERVER_FORWARD_ID")

if not TOKEN_AKUN or not CHANNEL_ID or not SERVER_FORWARD_ID_1 or not SERVER_FORWARD_ID_2:
    raise Exception("Environment variable ada yang kosong! Cek kembali GitHub Secrets Anda.")

# Pesan iklan utama untuk Channel Promosi 1
PESAN_UTAMA = """
SURG E 3 **<:WL:880251447470596157>
AT QWIFO<:correct:999455082032672843>"""

# Pesan untuk Channel Promosi 2
PESAN_KHUSUS_CHANNEL_2 = """
**SELL MEGAPHONE 1900  **<:WL:880251447470596157> OR 19 <:DL:880251434380165130>
AT QWIFO <:correct:999455082032672843>""" 

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
            with open("error_bot.log", "a") as f:
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
                
                for last in messages:
                    author = last.get("author", {})
                    author_id = author.get("id")
                    is_author_bot = author.get("bot", False)

                    if author_id == my_id or is_author_bot or is_user_bot:
                        continue

                    konten = last.get("content", "")
                    if konten.strip():
                        target_msg = konten
                        break  

                if target_msg:
                    teks = f"📩 **DM MASUK DARI PEMBELI ({name})** (`{ch_id}`):\n> {target_msg}"
                    kirim_pesan(SERVER_FORWARD_ID_1, teks)

                    print(f"[FORWARD] DM dari {name} berhasil diteruskan ke server.")
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
        print(f"[{now}] TOKEN TIDAK VALID/REVOKED! Stop.")
        exit(1)
        
    # 1. Kirim Promosi 1 ke CHANNEL_PROMOSI_1
    if kirim_pesan(CHANNEL_ID, PESAN_UTAMA):
        print(f"[{now}] Promosi 1 sukses.")
    else:
        print(f"[{now}] Promosi 1 gagal.")
        
    print("[INFO] Menunggu jeda sebelum mengirim promosi kedua...")
    time.sleep(10)

    # 2. Kirim Promosi 2 ke CHANNEL_PROMOSI_2
    if kirim_pesan(SERVER_FORWARD_ID_2, PESAN_KHUSUS_CHANNEL_2):
        print(f"[{now}] Promosi 2 sukses.")
    else:
        print(f"[{now}] Promosi 2 gagal.")
        
    # 3. Cek dan Teruskan DM Pembeli ke SERVER_FORWARD_ID
    periksa_dan_teruskan_dm()
