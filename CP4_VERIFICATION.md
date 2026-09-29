# CP4 — Scaling và Reliability

## Đã triển khai

- Redis List theo user, message JSON, giữ 20 message mới nhất, TTL 7 ngày.
- History theo thứ tự cũ đến mới, chia sẻ giữa các instance.
- `ping()` bắt mọi Exception, trả False khi Redis không sẵn sàng.
- Redis client có timeout kết nối và socket 2 giây cho mỗi lần thử.
- `/health` độc lập Redis; `/ready` kiểm tra Redis và trạng thái shutdown.
- SIGTERM/SIGINT bật cờ shutdown và chuyển tiếp handler cũ.
- Đăng ký signal nhiều lần không tự lưu handler của chính nó gây đệ quy.

## Kết quả thực tế

- `python -m pytest tests/test_cp4.py -v`: **19 passed**.
- Toàn bộ test CP1–CP4 cùng `test_security_edges.py` và
  `test_reliability_edges.py`: **77 passed**, không skip test Docker.
- Một cảnh báo deprecation Starlette/httpx; không có test thất bại.
- Ba agent container cùng Redis đều healthy và `/ready` trả 200.
- Gọi luân phiên cùng user qua ba container:
  `history_length = [0, 2, 4, 6, 8, 10]`.
- `docker stop --time 10` gửi SIGTERM tới một instance: thoát mã **0** sau
  khoảng **0,84 giây**, log có `service_stopped` và
  `Application shutdown complete`; không bị SIGKILL.
- Khởi động lại instance đó: lần hỏi tiếp theo thấy **12 message** trước đó.
- Dừng Redis: cả ba instance trả `/health=200`, `/ready=503` với `redis=false`.
- Bật lại Redis: cả ba instance trở về `/ready=200`.
- Đã xóa riêng dữ liệu user kiểm thử sau khi hoàn tất.
- Kiểm tra SIGTERM trên instance không có request dài đang chạy; chưa phải
  bằng chứng đo độ trễ hoặc drain request dài dưới tải production.

## Tái hiện scale

Compose mặc định giữ `8000:8000` cho CP2. Ba replica không thể cùng bind
một cổng host, nên dùng file bổ sung để mỗi replica nhận cổng loopback riêng:

```powershell
docker compose -f docker-compose.yml -f compose.scale.yml up -d --build --scale agent=3 --wait
docker compose -f docker-compose.yml -f compose.scale.yml ps
docker compose -f docker-compose.yml -f compose.scale.yml port --index 1 agent 8000
docker compose -f docker-compose.yml -f compose.scale.yml port --index 2 agent 8000
docker compose -f docker-compose.yml -f compose.scale.yml port --index 3 agent 8000
```

Dùng các cổng được in ra để gọi lần lượt `/ask` với cùng `X-User-Id`.
API key lấy từ `.env` cục bộ; không in header chứa key vào log hoặc ảnh.

File scale dùng `!override` để thay hẳn cấu hình ports, yêu cầu Compose
2.24.4 trở lên theo [Docker Docs](https://docs.docker.com/reference/compose-file/merge/#replace-value).
Máy hiện tại dùng Compose v5.5.1. Không dùng Nginx trong bài kiểm tra này;
request được gửi trực tiếp tới từng replica.

Quay về một instance tại localhost:8000:

```powershell
docker compose up -d --scale agent=1 --wait
```

Đây là trạng thái được khôi phục sau khi hoàn tất kiểm tra CP4.
