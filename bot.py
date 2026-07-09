import os
import requests
import time
from datetime import datetime

# ============ AMBIL DARI ENV (GITHUB SECRETS) ============
TOKEN_AKUN = os.environ.get("TOKEN_AKUN")
CHANNEL_ID = os.environ.get("CHANNEL_ID")
SERVER_FORWARD_ID = os.environ.get("SERVER_FORWARD_ID")

if not TOKEN_AKUN or not CHANNEL_ID or not SERVER_FORWARD_ID:
    raise Exception("Environment variable kosong! Cek Secrets.")

PESAN = """
**SURG-E 3 <:WL:880251447470596157>   
SELL GO <:Arrow:850540193626193941>  **ORUHC<:Verified:1000267030550827128>**
Note: Not In Vend = <:Sold:1432438946184298566> <:Sold:1432438946184298566>"""

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
            data = response.json()
            wait = data.get("retry_after", 60)
            print(f"[RATE LIMIT] Tunggu {wait}s")
            time.sleep(wait)
            return kirim_pesan(target_channel_id, konten)
        else:
            print(f"[GAGAL] {response.status_code} – {response.text}")
            # Simpan error ke log biar keliatan di Actions
            with open("error_log.txt", "a") as f:
                f.write(f"{datetime.now()} - Gagal kirim: {response.text}\n")
            return False
    except Exception as e:
        print(f"[ERROR] {e}")
        return False

def periksa_dan_teruskan_dm():
    url_dm = "https://discord.com/api/v9/users/@me/channels"
    try:
        res = requests.get(url_dm, headers=headers)
        if res.status_code != 200:
            print(f"[FORWARD] Gagal ambil DM – {res.status_code}")
            return
        dms = res.json()
        for chat in dms[:5]:
            if chat.get("type") != 1:
                continue
            channel_id = chat["id"]
            user = chat.get("recipients", [{}])[0]
            name = user.get("username", "Unknown")
            url_msg = f"https://discord.com/api/v9/channels/{channel_id}/messages?limit=1"
            r_msg = requests.get(url_msg, headers=headers)
            if r_msg.status_code == 200 and r_msg.json():
                last = r_msg.json()[0]
                if last.get("author", {}).get("id") != "1437652796391292998":  # ID akun lo
                    konten = last.get("content", "")
                    teks = f"📩 DM dari **{name}** (`{channel_id}`):\n> {konten}"
                    kirim_pesan(SERVER_FORWARD_ID, teks)
                    print(f"[FORWARD] DM dari {name} terkirim")
    except Exception as e:
        print(f"[ERROR DM] {e}")

if __name__ == "__main__":
    now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    # Cek token valid
    test = requests.get("https://discord.com/api/v9/users/@me", headers=headers)
    if test.status_code != 200:
        print(f"[{now}] TOKEN TIDAK VALID atau REVOKED! Stop.")
        exit(1)
    # Kirim iklan
    if kirim_pesan(CHANNEL_ID, PESAN):
        print(f"[{now}] Iklan sukses.")
    else:
        print(f"[{now}] Iklan gagal.")
    # Forward DM
    periksa_dan_teruskan_dm()
