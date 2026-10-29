# -*- coding: utf-8 -*-
"""Kiểm tra các kịch bản trong scenarios/ rồi ghi index.json (mục lục để app LVC Studio đọc).

Chạy:  python tools/build_index.py          (ghi index.json nếu có thay đổi)
       python tools/build_index.py --check  (chỉ kiểm tra, không ghi; thoát mã 1 nếu có lỗi)

Chỉ dùng thư viện chuẩn Python. Mỗi kịch bản phải:
  - là file JSON dạng {khoá_cấu_hình: giá_trị, ..., "_meta": {"name": ..., "desc": ..., "tag": ...}}
  - ≤ 400 KB, KHÔNG có ảnh xem trước nhúng (_meta.avatar) và KHÔNG chứa đường dẫn ổ đĩa / email / khoá bí mật.
Tên file = mã (id) của kịch bản; dùng chữ thường không dấu, số và dấu gạch ngang (vd: review-phim-trung-quoc.json).
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SCEN_DIR = os.path.join(ROOT, "scenarios")
INDEX_PATH = os.path.join(ROOT, "index.json")
SCHEMA = 1
MAX_BYTES = 400 * 1024
ID_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,78}$")
FORBIDDEN = [
    ("đường dẫn ổ đĩa", re.compile(r"[A-Za-z]:[\\/]")),
    ("thư mục người dùng", re.compile(r"[\\/]Users[\\/]", re.I)),
    ("email", re.compile(r"[\w.+-]+@[\w-]+\.[\w.]{2,}")),
    ("khoá bí mật", re.compile(r"(ghp_[A-Za-z0-9]{10,}|AIza[0-9A-Za-z_-]{20,}|sk-[A-Za-z0-9]{16,}|AKIA[0-9A-Z]{12,})")),
]


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def check_scenario(path: str) -> tuple[dict, bytes, list[str]]:
    errs: list[str] = []
    with open(path, "rb") as f:
        raw = f.read()
    if len(raw) > MAX_BYTES:
        errs.append(f"file quá lớn ({len(raw) // 1024} KB > {MAX_BYTES // 1024} KB)")
    try:
        data = json.loads(raw.decode("utf-8"))
    except Exception as e:  # noqa: BLE001
        return {}, raw, [f"không đọc được JSON: {e}"]
    if not isinstance(data, dict):
        return {}, raw, ["gốc JSON phải là một đối tượng {...}"]
    meta = data.get("_meta")
    if not isinstance(meta, dict) or not str(meta.get("name") or "").strip():
        errs.append("thiếu _meta.name (tên hiển thị)")
        meta = meta if isinstance(meta, dict) else {}
    if meta.get("avatar"):
        errs.append("có ảnh xem trước nhúng (_meta.avatar) — bỏ đi: ảnh cắt từ phim có thể vi phạm bản quyền")
    text = raw.decode("utf-8", "replace")
    for label, rx in FORBIDDEN:
        m = rx.search(text)
        if m:
            errs.append(f"chứa {label}: «{m.group(0)[:40]}»")
    return data, raw, errs


def build() -> tuple[dict, list[str]]:
    items, problems = [], []
    if not os.path.isdir(SCEN_DIR):
        return {}, ["không thấy thư mục scenarios/"]
    for fn in sorted(os.listdir(SCEN_DIR)):
        if not fn.lower().endswith(".json"):
            continue
        sid = fn[:-5]
        if not ID_RE.match(sid):
            problems.append(f"{fn}: tên file chỉ gồm chữ thường không dấu, số, dấu '-' (tối đa 79 ký tự)")
            continue
        data, raw, errs = check_scenario(os.path.join(SCEN_DIR, fn))
        problems += [f"{fn}: {e}" for e in errs]
        if errs:
            continue
        meta = data["_meta"]
        items.append({
            "id": sid,
            "file": f"scenarios/{fn}",
            "name": str(meta.get("name")).strip(),
            "desc": str(meta.get("desc") or "").strip(),
            "tag": str(meta.get("tag") or "").strip(),
            "sha256": sha256_bytes(raw),
            "size": len(raw),
        })
    items.sort(key=lambda x: x["id"])
    return {"schema": SCHEMA, "items": items}, problems


def main(argv: list[str]) -> int:
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    index, problems = build()
    for p in problems:
        print("❌", p)
    if problems:
        return 1
    if "--check" in argv:
        print(f"✅ {len(index['items'])} kịch bản hợp lệ.")
        return 0
    old = {}
    try:
        with open(INDEX_PATH, "r", encoding="utf-8") as f:
            old = json.load(f)
    except Exception:
        pass
    if old.get("schema") == SCHEMA and old.get("items") == index["items"]:
        print(f"= index.json không đổi ({len(index['items'])} kịch bản).")
        return 0
    index["updated_at"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    tmp = INDEX_PATH + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(index, f, ensure_ascii=False, indent=1, sort_keys=False)
        f.write("\n")
    os.replace(tmp, INDEX_PATH)
    print(f"✅ Đã ghi index.json ({len(index['items'])} kịch bản).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
