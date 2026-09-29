# Phiếu Phản Ánh — K4 Level 3B, Ngày 12

> **Bài làm cá nhân.** Trả lời bằng lời của chính bạn, dựa trên những gì bạn
> quan sát được khi chạy code — không sao chép đáp án của người khác.
>
> Các câu trả lời bên dưới dựa trên log và phép thử đã thực hiện.
> `grade.py` đếm số câu đã trả lời (15 điểm cho 10 câu).
>
> Họ và tên: Trần Quốc Vương  Mã học viên: 2A202602522

---

### Câu 1 — Fail fast (CP1)

Trong `Settings`, `agent_api_key` không có giá trị mặc định nên app chết ngay
khi khởi động nếu thiếu biến môi trường. Hãy mô tả một tình huống cụ thể mà
việc "chết sớm" này cứu bạn, so với việc để mặc định `"changeme"`.

Nếu triển khai lên Render mà quên `AGENT_API_KEY`, tôi muốn startup báo lỗi ngay. Tôi đã chạy Uvicorn trong môi trường không có khóa: quá trình khởi động thất bại với `ValidationError` ở `agent_api_key`. Nếu dùng `changeme`, web service vẫn lên xanh nhưng bất kỳ ai biết khóa mẫu có thể gọi `/ask`.

---

### Câu 2 — Log cho máy đọc (CP1)

Chạy service và gọi `/ask` vài lần. Dán một dòng log JSON bạn thu được, rồi
nêu **hai** việc bạn làm được với dòng log đó mà `print("đã trả lời xong")`
không làm được.

Dòng JSON tôi lấy từ `docker compose logs agent` sau một lần gọi `/ask` (đã xóa dữ liệu user thử khỏi Redis):

```json
{"user_id": "exercise-0abf6437ad25", "tokens_in": 6, "tokens_out": 45, "cost_usd": 2.79e-05, "event": "ask_completed", "level": "info", "timestamp": "2026-09-29T08:07:32.007974+00:00"}
```

Tôi có thể lọc event theo `user_id` để xem ai dùng service, và cộng `cost_usd` theo ngày để cảnh báo khi chi phí tăng. Dòng `print("đã trả lời xong")` không có user, thời gian hay chi phí để làm hai việc đó.

---

### Câu 3 — Kích thước image (CP2)

Build cả hai phiên bản và ghi lại số đo thật:

```bash
docker build -f <Dockerfile-1-stage> -t agent:single .
docker build -t agent:multi .
docker images | grep agent
```

| Bản | Dung lượng |
|-----|-----------|
| 1 stage (bản đầu) | 1.73 GB |
| Multi-stage | 271 MB |

Giải thích: phần dung lượng chênh lệch đó là những gì?

Tôi build Dockerfile một stage từ commit gốc `1239120` và Dockerfile hiện tại với cùng build context đã lọc secret. `docker images` báo 1.73 GB so với 271 MB. Bản một stage dùng `python:3.11` đầy đủ; bản mới dùng `python:3.11-slim` và chỉ mang thư viện đã cài sang runtime. Chênh lệch chủ yếu đến từ base image đầy đủ và các thành phần không cần thiết cho runtime.

---

### Câu 4 — Thứ tự lệnh trong Dockerfile (CP2)

Sửa một ký tự trong `app/main.py` rồi build lại. Với Dockerfile của bạn, những
layer nào được dùng lại từ cache, layer nào phải chạy lại? Nếu bạn đặt
`COPY . .` lên trước `RUN pip install` thì kết quả khác thế nào?

`COPY requirements.txt` và `RUN pip install` đứng trước `COPY app/`, `COPY utils/`. Khi chỉ sửa `app/main.py`, Docker có thể dùng lại base image và layer cài dependency; layer copy source và các bước sau nó phải tạo lại. Nếu để `COPY . .` trước `pip install`, thay một ký tự trong source sẽ làm mất cache của layer cài thư viện. Tôi đã thử build với thay đổi source tạm rồi hoàn nguyên; Docker dừng ở bước lấy metadata từ `registry-1.docker.io` (một lần lỗi DNS, một lần timeout). Vì vậy đây là kết luận từ thứ tự layer, chưa phải quan sát `CACHED` trong lần thử đó.

---

### Câu 5 — Vì sao không chạy bằng root (CP2)

Container mặc định chạy bằng root. Mô tả chuỗi sự kiện dẫn từ "một lỗ hổng
trong code Python của bạn" tới "kẻ tấn công có quyền cao trên máy host", và
lệnh `USER` cắt đứt chuỗi đó ở chỗ nào.

Nếu một lỗi Python cho phép chạy lệnh trong container, tiến trình root có thể đọc/sửa mọi tệp mà container được phép chạm tới. Khi container được cấp mount hoặc quyền Docker daemon rộng, kẻ tấn công có thể tác động lên host. `USER appuser` hạ quyền tiến trình từ đầu; tôi đã kiểm tra `docker compose exec agent id` cho kết quả UID/GID 10001. Điều này giảm quyền sau khi bị khai thác, dù vẫn cần giới hạn mount và quyền Docker.

---

### Câu 6 — Cửa sổ trượt (CP3)

Rate limit của bạn dùng sliding window 60 giây. Nếu thay bằng cách đếm theo
phút đồng hồ (reset lúc giây 00), một người dùng có thể gửi tối đa bao nhiêu
request trong 2 giây liên tiếp khi hạn mức là 10/phút? Giải thích cách đạt được
con số đó.

Với giới hạn 10 request/phút, đếm theo phút lịch cho phép 20 request trong khoảng 2 giây: gửi 10 request sát 10:00:59 và 10 request ngay 10:01:00. Cửa sổ trượt vẫn nhìn lại 60 giây trước request mới nên đợt thứ hai bị chặn. Trong Redis tôi xóa timestamp cũ, đếm ZSET, rồi mới thêm member timestamp+UUID.

---

### Câu 7 — Rate limit và cost guard (CP3)

Hai cơ chế này khác nhau ở điểm nào? Cho một tình huống mà rate limit cho qua
nhưng cost guard phải chặn, và một tình huống ngược lại.

Rate limit kiểm số lượt gọi trong 60 giây; cost guard kiểm tổng USD của tháng UTC. Một user gọi ít lần nhưng đã tiêu gần hết 10 USD thì rate limit vẫn cho qua, còn cost guard trả 402. Ngược lại, user gửi 11 câu hỏi rất rẻ trong một phút vẫn còn ngân sách nhưng lượt thứ 11 bị trả 429. Tôi đã thấy cả 429 kèm `Retry-After` và 402 khi thử trên container thật.

---

### Câu 8 — /health khác /ready (CP4)

Nếu gộp hai endpoint làm một và cho nó kiểm tra Redis, chuyện gì xảy ra với cụm
3 container khi Redis mất kết nối 30 giây? Trả lời theo đúng thứ tự sự kiện.

Nếu Redis rớt 30 giây mà `/health` cũng ping Redis, cả ba agent sẽ báo 503. Orchestrator có thể restart cả ba cùng lúc; lúc Redis trở lại vẫn phải chờ container khởi động lại, khiến khoảng gián đoạn dài hơn. Tôi đã dừng Redis khi ba replica chạy: cả ba `/health` vẫn 200, `/ready` đều 503; sau khi bật Redis, `/ready` trở về 200. Nhờ vậy load balancer có thể ngừng gửi request vào instance chưa sẵn sàng mà không coi process là đã chết.

---

### Câu 9 — Stateless (CP4)

Chạy `docker compose up --scale agent=3` rồi gọi `/ask` nhiều lần với cùng một
`X-User-Id`. Quan sát `history_length` trong response. Nếu lịch sử được lưu
trong một dict Python thay vì Redis, bạn sẽ thấy con số đó thay đổi thế nào?

Tôi gọi luân phiên trực tiếp vào ba cổng của ba container cùng một `X-User-Id`. `history_length` lần lượt là `0, 2, 4, 6, 8, 10`. Sau khi stop/start một replica, lần kế tiếp vẫn thấy 12 message đã có. Nếu dùng dict Python, mỗi container giữ lịch sử riêng nên số đếm phụ thuộc container vừa nhận request, có thể giảm hoặc lặp lại khi đổi container; restart thì mất dữ liệu trong RAM của instance đó.

---

### Câu 10 — Deploy thật (CP5)

Ghi lại **một** lỗi bạn gặp khi deploy lên cloud (build fail, health check
timeout, sai REDIS_URL, app không đọc `$PORT`...): thông báo lỗi là gì, bạn
tìm ra nguyên nhân bằng cách nào, và sửa ra sao?

Hiện chưa có lần deploy cloud hoàn tất để tôi ghi một lỗi build/runtime trên Render. Lỗi thực tế ở bước chuẩn bị cloud là `Unauthorized. Please login with railway login` khi kiểm tra Railway CLI; nguyên nhân là máy chưa đăng nhập Railway. Tôi chuyển sang Render theo lựa chọn của mình, đã tạo tài khoản và đang chờ tạo Blueprint từ repo cá nhân. Khi Render trả build/deploy log thực tế, tôi sẽ cập nhật thông báo, nguyên nhân và cách sửa; tôi không coi lỗi đăng nhập Railway là bằng chứng service đã deploy.
