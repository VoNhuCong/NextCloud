### `autotunel.py`

#!/usr/bin/env python3

import subprocess
import re
import time
import socket
import urllib.request
import urllib.parse
import json
import os
import signal
import sys

# ============================================================
# CONFIG
# ============================================================

NEXTCLOUD_CONTAINER = "nextcloud_app_1"
NEXTCLOUD_URL = "http://192.168.0.6:8080"

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN",
    "7726886920:cfgjbj"
)

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID",
    "678945678"
)

CHECK_INTERVAL = 5

# ============================================================
# GLOBAL
# ============================================================

cloudflared_process = None


# ============================================================
# CHECK INTERNET
# ============================================================

def internet_available():

    try:
        socket.create_connection(
            ("1.1.1.1", 53),
            timeout=3
        )
        return True

    except OSError:
        return False


# ============================================================
# TELEGRAM
# ============================================================

def send_telegram(message):

    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    )

    data = urllib.parse.urlencode({
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message
    }).encode()

    request = urllib.request.Request(
        url,
        data=data,
        method="POST"
    )

    # Sử dụng vòng lặp để thử gửi telegram nhiều lần nếu thất bại
    max_retries = 30

    for attempt in range(1, max_retries + 1):

        try:

            with urllib.request.urlopen(
                request,
                timeout=15
            ) as response:

                result = json.loads(
                    response.read().decode()
                )

            if result.get("ok"):

                print("✅ Telegram: gửi thành công")
                return True

            print(f"❌ Telegram error (attempt {attempt}/{max_retries}):")
            print(result)

        except Exception as e:

            print(
                f"❌ Không thể gửi Telegram (attempt {attempt}/{max_retries}):",
                e
            )

        if attempt < max_retries:
            time.sleep(5)
            
    print(
        f"❌ Đã thử gửi Telegram {max_retries} lần nhưng vẫn thất bại"
    )

    # Reset service autotunel.service if Telegram sending fails after max retries
    try:
        subprocess.run(
            ["systemctl", "restart", "autotunel.service"],
            check=False,
            capture_output=True,
            text=True,
            timeout=30
        )
        print("✅ Đã chạy lệnh: systemctl restart autotunel.service")
    except Exception as e:
        print("❌ Không thể chạy lệnh restart autotunel.service:", e)
    
    return False


# ============================================================
# STOP CLOUDFLARED
# ============================================================

def stop_cloudflared():

    global cloudflared_process

    if cloudflared_process is None:
        return

    print("🛑 Đang dừng Cloudflare Tunnel...")

    try:

        cloudflared_process.terminate()

        cloudflared_process.wait(
            timeout=5
        )

    except subprocess.TimeoutExpired:

        cloudflared_process.kill()

    except Exception as e:

        print(
            "Lỗi khi dừng cloudflared:",
            e
        )

    cloudflared_process = None

    print("✅ Cloudflare Tunnel đã dừng")


# ============================================================
# START CLOUDFLARE
# ============================================================

def start_cloudflared():

    global cloudflared_process

    print("")
    print("🚀 Đang khởi động Cloudflare Tunnel...")

    command = [
        "cloudflared",
        "tunnel",
        "--url",
        NEXTCLOUD_URL
    ]

    cloudflared_process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    cloudflare_url = None

    start_time = time.time()

    while time.time() - start_time < 30:

        line = cloudflared_process.stdout.readline()

        if not line:
            continue

        line = line.strip()

        if line:
            print(
                "[cloudflared]",
                line
            )

        # Tìm URL trycloudflare
        match = re.search(
            r"https://[a-zA-Z0-9.-]+\.trycloudflare\.com",
            line
        )

        if match:

            cloudflare_url = (
                match.group(0)
                .rstrip("/")
            )

            break

    if not cloudflare_url:

        print(
            "❌ Không tìm thấy Cloudflare URL"
        )

        stop_cloudflared()

        return None

    print("")
    print("======================================")
    print("🌐 Cloudflare URL:")
    print(cloudflare_url)
    print("======================================")

    return cloudflare_url


# ============================================================
# UPDATE NEXTCLOUD
# ============================================================

def update_nextcloud(cloudflare_url):

    domain = cloudflare_url.replace(
        "https://",
        ""
    ).rstrip("/")

    print("")
    print(
        "🔧 Đang cập nhật Nextcloud:"
    )

    print(
        f"   trusted_domains = {domain}"
    )

    command = [
        "docker",
        "exec",
        "-u",
        "www-data",
        NEXTCLOUD_CONTAINER,
        "php",
        "occ",
        "config:system:set",
        "trusted_domains",
        "1",
        f"--value={domain}"
    ]

    try:

        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            timeout=30
        )

    except Exception as e:

        print(
            "❌ Không chạy được occ:",
            e
        )

        return False

    if result.stdout:
        print(result.stdout)

    if result.stderr:
        print(result.stderr)

    if result.returncode != 0:

        print(
            "❌ Cập nhật trusted_domains thất bại"
        )

        return False

    print(
        "✅ Nextcloud đã được cập nhật"
    )

    return True


# ============================================================
# START EVERYTHING
# ============================================================

def start_tunnel():

    print("")
    print("======================================")
    print("🌐 INTERNET ĐÃ TRỞ LẠI")
    print("======================================")

    cloudflare_url = start_cloudflared()

    if not cloudflare_url:

        print(
            "❌ Không thể tạo Cloudflare Tunnel"
        )

        return

    # Cho tunnel ổn định
    time.sleep(2)

    # Cập nhật Nextcloud
    nextcloud_ok = update_nextcloud(
        cloudflare_url
    )

    # Gửi Telegram
    if nextcloud_ok:

        message = (
            "🚀 Nextcloud Tunnel đã sẵn sàng\n\n"
            f"🔗 {cloudflare_url}\n\n"
            "✅ Nextcloud trusted_domains: OK"
        )

    else:

        message = (
            "⚠️ Cloudflare Tunnel đã tạo\n\n"
            f"🔗 {cloudflare_url}\n\n"
            "❌ Nextcloud trusted_domains: FAILED"
        )

    send_telegram(message)


# ============================================================
# MAIN MONITOR
# ============================================================

def main():

    global cloudflared_process

    print("")
    print("======================================")
    print("   INTERNET + CLOUDFLARE MONITOR")
    print("======================================")
    print("")

    previous_status = internet_available()

    if previous_status:

        print(
            "🌐 Internet: ONLINE"
        )

        start_tunnel()

    else:

        print(
            "🔴 Internet: OFFLINE"
        )

    while True:

        time.sleep(CHECK_INTERVAL)

        current_status = internet_available()

        # ----------------------------------------------------
        # INTERNET BỊ MẤT
        # ----------------------------------------------------

        if previous_status and not current_status:

            print("")
            print(
                "🔴 INTERNET ĐÃ MẤT"
            )

            stop_cloudflared()

        # ----------------------------------------------------
        # INTERNET TRỞ LẠI
        # ----------------------------------------------------

        elif not previous_status and current_status:

            start_tunnel()

        previous_status = current_status


# ============================================================
# CTRL+C
# ============================================================

def signal_handler(
    sig,
    frame
):

    print("")
    print(
        "🛑 Đang thoát chương trình..."
    )

    stop_cloudflared()

    sys.exit(0)


signal.signal(
    signal.SIGINT,
    signal_handler
)

signal.signal(
    signal.SIGTERM,
    signal_handler
)


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()
