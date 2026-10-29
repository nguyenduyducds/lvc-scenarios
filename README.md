# LVC Studio — Kho kịch bản miễn phí

Kho kịch bản dựng sẵn cho **LVC Studio**. App tự tải mục lục `index.json` ở đây (qua `raw.githubusercontent.com`)
nên thêm / sửa kịch bản **không cần phát hành bản app mới**.

## Cấu trúc

```
index.json          # mục lục do tools/build_index.py sinh ra — ĐỪNG sửa tay
scenarios/*.json    # mỗi file = 1 kịch bản (tên file = mã kịch bản, chữ thường không dấu)
tools/build_index.py
```

## Thêm / sửa kịch bản

**Cách 1 — từ repo app (khuyên dùng):** trong thư mục `ToolEdit` chạy

```
python dev_scripts/publish_scenarios.py            # đồng bộ assets/scenarios → repo này, dựng mục lục, commit + push
python dev_scripts/publish_scenarios.py --dry-run  # chỉ xem sẽ đổi gì
```

**Cách 2 — thủ công:** chép/sửa file trong `scenarios/`, chạy `python tools/build_index.py`, rồi `git add -A && git commit && git push`.
(Upload thẳng trên web GitHub thì phải chạy lại `python tools/build_index.py` và commit `index.json`; nên dùng Cách 1 cho đỡ quên.)

## Quy tắc cho mỗi kịch bản

- JSON dạng phẳng `{khoá_cấu_hình: giá_trị, ..., "_meta": {"name": "...", "desc": "...", "tag": "..."}}`.
- Tối đa 400 KB. **Không** nhúng ảnh xem trước (`_meta.avatar`) — ảnh cắt từ phim có thể vi phạm bản quyền.
- **Không** chứa đường dẫn ổ đĩa (`D:\...`), email, khoá bí mật. `build_index.py` sẽ báo lỗi và dừng.

## App đọc thế nào

1. Tải `index.json` (có ETag nên chỉ tải lại khi đổi), so `sha256` từng file với mục lục.
2. Lưu bản tải về vào thư mục dữ liệu của app; mất mạng thì dùng bản đã lưu, chưa từng tải thì dùng bản đi kèm app.
3. Kịch bản tải về chỉ là **dữ liệu cấu hình**, app chỉ nhận các khoá thiết lập đã biết.
