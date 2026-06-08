"""
C Learn — 即学即写的 C 语言学习平台
Web 前端 + Python 后端 + 桌面壳 → 单 exe
"""
import sys
import os
import time
import threading
from pathlib import Path

# Ensure project root on path (also works inside PyInstaller _MEIPASS)
BASE = Path(getattr(sys, "_MEIPASS", Path(__file__).parent))
if str(BASE) not in sys.path:
    sys.path.insert(0, str(BASE))
os.chdir(BASE)

import webview
from server import app, start_server


def main():
    # Start Flask server in background
    port = 8765
    url = start_server(port)

    # Wait for server to be ready
    import urllib.request
    for _ in range(30):
        try:
            urllib.request.urlopen(f"http://127.0.0.1:{port}/api/health", timeout=0.5)
            break
        except Exception:
            time.sleep(0.1)

    # Open desktop window
    window = webview.create_window(
        title="C 语言学习平台",
        url=url,
        width=1280,
        height=820,
        min_size=(960, 600),
        resizable=True,
    )
    webview.start(debug=False)


if __name__ == "__main__":
    main()
