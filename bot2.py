import os
import requests
import time
from datetime import datetime

# ============ AMBIL DARI ENV (GITHUB SECRETS) ============
TOKEN_AKUN = os.environ.get("TOKEN_AKUN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")

# 2 Channel ID Tujuan Berbeda (Ganti nama Secret di GitHub sesuai ini)
SERVER_FORWARD_ID_1 = os.environ.get("SERVER_FORWARD_ID_1")
SERVER_FORWARD_ID_2 = os.environ.get("SERVER_FORWARD_ID_2")

if not TOKEN_AKUN or not CHANNEL_ID or not SERVER_FORWARD_ID_1 or not SERVER_FORWARD_ID_2:
    raise Exception("Missing env variables! Cek Secrets untuk BOT2 (Pastikan SERVER_FORWARD_ID_1 & 2 terisi).")

# Pesan iklan utama untuk CHANNEL_ID
PESAN_UTAMA = """
SURG E 3 **<:WL:880251447470596157>
AT QWIFO<:correct:999455082032672843>"""

# Pesan khusus / log yang dikirim ke SERVER_FORWARD_ID_2 (bisa diubah sesuai keinginan)
PESAN_KHUSUS_CHANNEL_2 = """
**[BOT 2 - STATUS LOG]**
Sistem pengecekan DM & Iklan Bot 2 Berjalan Normal 🟢"""

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
            print(f"[RATE LIMIT BOT2] Tunggu {wait}s")
            time.sleep(wait)
            return kirim_pesan(target_channel_id, konten)
        else:
            print(f"[GAGAL BOT2] {response.status_code} – {response.text}")
            with open("error_bot2.log", "a") as f:
                f.write(f"{datetime.now()} - Gagal kirim: {response.text}\n")
            return False
    except Exception as e:
        print(f"[ERROR BOT2] {e}")
        return False

def periksa_dan_teruskan_dm():
    # Ambil ID akun sendiri secara otomatis agar filter pengiriman akurat
    res_me = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
    my_id = res_me.json().get("id") if res_me.status_code == 200 else None

    url_dm = "https://discord.com/api/v9/users/@me/channels"
    try:
        res = requests.get(url_dm, headers=headers)
        if res.status_code != 200:
            print(f"[FORWARD BOT2] Gagal ambil DM – {res.status_code}")
            return
        
        dms = res.json()
        forwarded = 0
        
        # Ambil 30 channel teratas agar DM dari manusia tidak tertimbun bot lain
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

            # Ambil beberapa pesan terakhir untuk memastikan pesan valid terbaca
            url_msg = f"https://discord.com/api/v9/channels/{ch_id}/messages?limit=3"
            r_msg = requests.get(url_msg, headers=headers)
            
            if r_msg.status_code == 200 and r_msg.json():
                messages = r_msg.json()
                target_msg = None
                
                for last in messages:
                    author = last.get("author", {})
                    author_id = author.get("id")
                    is_author_bot = author.get("bot", False)

                    # Skip jika pesan dari diri sendiri atau bot
                    if author_id == my_id or is_author_bot or is_user_bot:
                        continue

                    konten = last.get("content", "")
                    if konten.strip():
                        target_msg = konten
                        break  # Dapatkan pesan valid dari manusia

                if target_msg:
                    teks = f"📩 [BOT2] DM DARI MANUSIA **{name}** (`{ch_id}`):\n> {target_msg}"
                    
                    # Kirim ke 2 Channel ID Tujuan yang berbeda
                    kirim_pesan(SERVER_FORWARD_ID_1, teks)
                    kirim_pesan(SERVER_FORWARD_ID_2, f"🔄 **[Forward Log Channel 2]**\n{teks}")

                    print(f"[FORWARD BOT2] DM terbaru dari {name} berhasil diteruskan ke 2 channel.")
                    forwarded += 1
                    break  # Hanya forward 1 DM terbaru dari manusia

        if forwarded == 0:
            print("[FORWARD BOT2] Tidak ada DM baru dari manusia.")
            
    except Exception as e:
        print(f"[ERROR DM BOT2] {e}")

if __name__ == "__main__":
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    # Validasi token
    test = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
    if test.status_code != 200:
        print(f"[{now}] BOT2 TOKEN TIDAK VALID/REVOKED! Stop.")
        exit(1)
        
    # Kirim iklan utama
    if kirim_pesan(CHANNEL_ID, PESAN_UTAMA):
        print(f"[{now}] Iklan BOT2 sukses.")
    else:
        print(f"[{now}] Iklan BOT2 gagal.")
        
    # Kirim pesan khusus ke channel tujuan kedua (Opsional)
    kirim_pesan(SERVER_FORWARD_ID_2, PESAN_KHUSUS_CHANNEL_2)

    # Forward DM
    periksa_dan_teruskan_dm()
