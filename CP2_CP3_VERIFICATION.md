# CP2 và CP3 — Kết quả kiểm chứng

## CP2

- Docker Desktop 4.93.0 được cài qua winget từ bộ cài chính thức của Docker.
- Docker Engine/CLI 29.8.1, Docker Compose v5.5.1; backend WSL 2 hoạt động.
- `docker build -t day12-agent:prod .`: thành công.
- `docker images day12-agent:prod --format '{{.Size}}'`: `271MB`, dưới 500 MB.
- `docker compose up -d --wait`: agent và redis đều healthy.
- `GET http://localhost:8000/health`: HTTP 200, trả về
  `{"status":"ok","service":"day12-agent","version":"1.0.0"}`.
- `docker compose exec -T agent id`: UID/GID 10001 (appuser).
- Kiểm tra trong image: không có `/app/.env` hoặc `/app/.git`.
- Chạy container riêng với `PORT=8123`: image healthcheck chuyển sang healthy.
- `python -m pytest tests/test_cp2.py -v`: **16 passed**, không skip Docker.

## CP3

- `python -m pytest tests/test_cp1.py tests/test_cp3.py -v`: **35 passed**
  (CP1: 13, CP3: 22).
- `python -m pytest tests/test_security_edges.py -v`: **5 passed** trong lượt
  kiểm tra bổ sung cùng các test store liên quan.
- Sáu test store liên quan đến đọc/ghi history, cắt lịch sử, TTL và fake URL đạt.
- HTTP thực tế với agent container và Redis thật: thiếu/sai key → 401;
  key hợp lệ → 200; lượt hỏi thứ hai nhận history_length=2.
- Gọi quá quota → 429, có Retry-After; đặt chi phí vượt ngân sách cho user
  kiểm thử riêng → 402, không tạo history.
- Kiểm tra Redis thật với 30 request đồng thời/quota 5: đúng 5 được chấp nhận,
  25 bị chặn. WATCH/MULTI/EXEC bảo vệ thao tác kiểm tra và ghi quota.
- Các dữ liệu user kiểm thử được xóa sau khi kiểm tra.
- Có một cảnh báo deprecation từ Starlette TestClient/httpx; test vẫn hoàn tất.

## Trạng thái và giới hạn

- Agent đang phục vụ ở http://localhost:8000; Redis chỉ publish trên loopback.
- `.env` local đã chuyển từ fake Redis sang `redis://localhost:6379/0`;
  secret giữ cục bộ, không được ghi vào tài liệu hoặc commit.
- Đã làm phần append/get_history của CP4 để `/ask` chạy được end-to-end.
  Readiness và ping của store vẫn thuộc bước CP4 tiếp theo.
- Cost guard theo hợp đồng của lab: `/ask` kiểm tra tổng đã tiêu trước khi gọi
  mock LLM rồi ghi chi phí thực tế sau đó. Đây chưa phải cơ chế đặt trước
  ngân sách nguyên tử; chưa đảm bảo trần chi phí tuyệt đối khi có nhiều
  request đang chạy đồng thời hoặc chi phí lượt kế tiếp vượt số dư.
- User ID do client cung cấp theo yêu cầu lab; triển khai thương mại cần gắn
  danh tính với credential để hạn mức không bị né bằng cách đổi user ID.
