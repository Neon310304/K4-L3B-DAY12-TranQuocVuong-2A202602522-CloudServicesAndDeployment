# CP0 — Setup và baseline

- Học viên: Trần Quốc Vương — 2A202602522.
- Repository: `K4-L3B-DAY12-TranQuocVuong-2A202602522-CloudServicesAndDeployment`.
- Đã đọc: README.md, LAB_GUIDE.md, CHECKPOINTS.md, RUBRIC.md, RULES.md và SUBMISSION.md.
- Môi trường: Windows PowerShell, Python 3.12.6, Git 2.54.0.windows.1.
- Đã tạo `.venv`, nâng cấp pip và cài `requirements.txt`.
- `python -m pip check`: `No broken requirements found.`
- `.env` được tạo từ `.env.example`, có API key cá nhân; không ghi giá trị secret vào tài liệu.
- `.env` và `.venv` được Git bỏ qua; `.env` không được Git theo dõi.
- Chưa có Docker trong môi trường hiện tại; tạm dùng `REDIS_URL=fake://`. Kiểm tra `fakeredis.FakeRedis().ping()` thành công.

## Baseline

Chạy từ gốc repository bằng Python của môi trường ảo:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/ -v -m "not docker"
```

Kết quả thực tế:

```text
66 failed, 7 passed, 5 skipped, 2 deselected, 1 warning, 16 errors
```

Pytest kết thúc với exit code 1 vì các checkpoint chưa được triển khai.
Không có `ModuleNotFoundError` hoặc `ImportError` trong log.
Các test thất bại do TODO/NotImplementedError, cấu hình starter chưa hoàn thiện;
16 lỗi fixture do chưa có workflow bonus và chưa có Public URL cho CP5.
Có một cảnh báo Starlette về việc TestClient dùng httpx; baseline vẫn chạy hoàn tất.

Log đầy đủ lưu cục bộ tại `cp0-test.log` (được Git bỏ qua).
CP0 đạt điều kiện setup; kết quả này không xác nhận đạt CP1–CP5.
Docker/Redis thật cần được chuẩn bị cho phần container và deployment.
