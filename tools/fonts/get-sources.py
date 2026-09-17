#!/usr/bin/env python3
"""Tải font gốc về tools/fonts/src/ và kiểm tra SHA256.

Font gốc rất nặng (Shippori Mincho B1 gần 15 MB) nên không commit vào repo.
Thay vào đó `fonts.lock.json` ghim đúng một commit của repo google/fonts kèm
SHA256 của từng file, nên lần tải nào cũng ra đúng bản font đó.

    python3 tools/fonts/get-sources.py
"""
import hashlib
import json
import pathlib
import sys
import urllib.parse
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
LOCK = ROOT / "tools/fonts/fonts.lock.json"
SRC = ROOT / "tools/fonts/src"


def sha256(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    lock = json.loads(LOCK.read_text())
    SRC.mkdir(parents=True, exist_ok=True)
    base = f"https://raw.githubusercontent.com/{lock['repo']}/{lock['commit']}/"
    ok = True

    for item in lock["files"]:
        target = SRC / item["local"]
        if target.exists() and sha256(target) == item["sha256"]:
            print(f"  có sẵn   {item['local']}")
            continue

        url = base + urllib.parse.quote(item["remote"])
        print(f"  tải      {item['local']} …", end="", flush=True)
        try:
            with urllib.request.urlopen(url, timeout=300) as response:
                data = response.read()
        except Exception as error:                      # noqa: BLE001 — báo lỗi cho người dùng, không cần phân loại
            print(f" lỗi: {error}")
            ok = False
            continue

        got = hashlib.sha256(data).hexdigest()
        if got != item["sha256"]:
            print(f" SHA256 không khớp!\n    mong đợi {item['sha256']}\n    nhận được {got}")
            ok = False
            continue

        target.write_bytes(data)
        print(f" xong ({len(data) // 1024} KB)")

    if not ok:
        sys.exit("Có file tải lỗi hoặc sai SHA256. Không build font khi chưa sửa xong.")
    print("Font gốc đã đủ và đúng checksum.")


if __name__ == "__main__":
    main()
