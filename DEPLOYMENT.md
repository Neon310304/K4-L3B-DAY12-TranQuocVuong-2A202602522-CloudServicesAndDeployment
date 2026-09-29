# CP5 — Render deployment

## Thông tin học viên

| Mục | Giá trị |
|---|---|
| Họ và tên | Trần Quốc Vương |
| Mã học viên | 2A202602522 |
| Repository | https://github.com/Neon310304/K4-L3B-DAY12-TranQuocVuong-2A202602522-CloudServicesAndDeployment |

## Service

| Mục | Giá trị |
|---|---|
| Platform | Render Blueprint |
| Ngày deploy | 2026-09-29 |
| Public URL | https://day12-agent-xhlo.onrender.com |
| Web service | `day12-agent` |
| State store | Render Key Value `day12-redis` |

`render.yaml` định nghĩa web service và Key Value ở gói `free`. Web service
build từ Dockerfile. `REDIS_URL` được Render lấy từ `connectionString` nội bộ
của Key Value. `AGENT_API_KEY` được nhập qua giao diện Render khi tạo Blueprint
(`sync: false`); giá trị không nằm trong repository hoặc tài liệu này.

## Cấu hình môi trường

| Tên biến | Nguồn |
|---|---|
| `PORT` | Render tự cấp; Dockerfile đọc biến này khi khởi động |
| `AGENT_API_KEY` | Secret nhập trong dashboard Render |
| `REDIS_URL` | Render Key Value, tham chiếu từ `render.yaml` |
| `RATE_LIMIT_PER_MINUTE` | Cấu hình `render.yaml`: 10 |
| `MONTHLY_BUDGET_USD` | Cấu hình `render.yaml`: 10.0 |
| `LOG_LEVEL` | Cấu hình `render.yaml`: INFO |

Chỉ ghi tên biến và nguồn cấp. Không lưu giá trị API key hoặc chuỗi kết nối Redis.

## Kiểm tra URL HTTPS thật

Thử từ máy cục bộ sau khi Blueprint live, ngày 2026-09-29. Các dòng bên dưới là
kết quả HTTP thực tế; phần body đã rút gọn, không chứa secret.

```text
GET  https://day12-agent-xhlo.onrender.com/health
200 {"status":"ok","service":"day12-agent","version":"1.0.0"}

GET  https://day12-agent-xhlo.onrender.com/ready
200 {"status":"ready","redis":true}

POST https://day12-agent-xhlo.onrender.com/ask  (không gửi API key)
401 {"detail":"invalid or missing API key"}

POST https://day12-agent-xhlo.onrender.com/ask  (có API key, user thử riêng)
200; response có answer, cost_usd, history_length, tokens, user_id

15 request có API key của cùng một user thử mới:
200 200 200 200 200 200 200 200 200 200 429 429 429 429 429
```

Kiểm tra lại không cần secret:

```powershell
curl.exe -i https://day12-agent-xhlo.onrender.com/health
curl.exe -i https://day12-agent-xhlo.onrender.com/ready
curl.exe -i -X POST https://day12-agent-xhlo.onrender.com/ask -H 'Content-Type: application/json' -d '{"question":"Hello"}'
```

`DEPLOY_API_KEY` trong `.env` cục bộ dùng cho bài test tùy chọn có xác thực.
File `.env` được Git bỏ qua.

## Ảnh minh chứng

- `screenshots/dashboard.png`: dashboard Render, che phần secret.
- `screenshots/health.png`: trang hoặc kết quả gọi `/health` ở public URL.

Ảnh do học viên chụp trực tiếp từ giao diện Render/trình duyệt để chứng minh
deploy thật. Trạng thái ảnh sẽ được xác nhận khi hai file có trong repository.
