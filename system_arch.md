# System Architecture

## Overview
This system is an automated web crawler and API server designed to interface with Google's Image Generation Flow. It bypasses Google's strict Bot Detection mechanisms by combining advanced Selenium configurations, CDP (Chrome DevTools Protocol), and ActionChains to simulate human behavior, while managing high-concurrency requests through a sequential queue system.

Kiến trúc bao gồm hai thành phần chính:
1. **API Server (FastAPI)**: Tiếp nhận HTTP requests chứa prompt văn bản (theo đúng cấu trúc JSON của Google Gemini API).
2. **Crawler (Selenium)**: Tự động hóa quá trình mở trình duyệt, chọn logo từ danh sách tải lên, vượt qua Bot Detection để nhập prompt, chờ và tải ảnh kết quả về an toàn.

## Directory Structure
- `main.py`: Entry point for the FastAPI server (chạy trên Uvicorn port 8000). Khởi chạy Hàng đợi (Queue) khi startup.
- `api_request_lock.py`: Trái tim của hệ thống Concurrency. Chứa `APIRequestQueue` đóng vai trò là một hàng đợi (Queue) tuần tự và một `ThreadPoolExecutor` duy nhất. Đảm bảo các Request đến cùng lúc sẽ phải xếp hàng và chờ nhau. Sau mỗi lượt sẽ tự động sleep 5 giây để tránh bị Google block.
- `api/routes.py`: Định nghĩa API endpoints (`POST /generate`). Phân tích JSON chuẩn Gemini, bóc tách dữ liệu và đẩy vào Queue.
- `crawler/browser.py`: Khởi tạo Selenium WebDriver (`undetected-chromedriver`). Load profile lưu sẵn để bypass đăng nhập. Tích hợp cấu hình Proxy tùy chỉnh và vô hiệu hóa WebRTC chống rò rỉ IP.
- `crawler/proxy_extension.py`: Module tạo Chrome Extension động (Unpacked Directory) để tiêm chứng chỉ đăng nhập Proxy (Auth/Geo-Targeting) vào trình duyệt, khắc phục giới hạn của `undetected-chromedriver`.
- `crawler/actions.py`: Chứa các module tương tác DOM chống Bot Detection (Anti-Bot):
  - Nhập Text siêu tốc qua CDP (`Input.insertText`) từng dòng để qua mặt cơ chế theo dõi gõ phím.
  - Sử dụng `ActionChains` mô phỏng quỹ đạo click chuột tự nhiên thay vì click cơ học, tránh bị phát hiện "dịch chuyển tức thời".
  - Bắt gói tin tải ảnh ngầm qua tiêm Javascript (Fetch) để lấy thẳng dữ liệu Base64 không cần bấm nút Download trên UI.
- `login.py`: Script khởi chạy trình duyệt một lần duy nhất để người dùng đăng nhập tay vào Google.
- `proxy_config.txt`: File cấu hình địa chỉ Proxy xoay vòng (hỗ trợ `user:pass@host:port`).
- `chrome_profile/`: Thư mục lưu trữ phiên đăng nhập và cookie, giúp vượt qua bước xác thực tài khoản Google trong các lần chạy sau.
- `downloads/`: Thư mục lưu trữ ảnh được tải về từ Google Flow trước khi trả Base64 về cho API.

## Workflow
1. Client gọi API `/generate` với payload chuẩn Gemini chứa `prompt`.
2. FastAPI tiếp nhận, trích xuất text và ném công việc vào `request_queue`. Request sẽ bị "treo" (await) cho tới khi tới lượt. TRONG LÚC ĐÓ, API mở một luồng HTTP Streaming, trả về ngay HTTP 200 OK và lén gửi 1 khoảng trắng (Space ` `) mỗi 15 giây để "lừa" Cloudflare Tunnel không cắt kết nối vì dính luật Timeout 100s.
3. Queue Worker nhận lệnh, kích hoạt luồng Selenium (chạy đồng bộ trong ThreadPool). Trình duyệt chạy ở chế độ `headless=False` bung trực tiếp ra màn hình vật lý (XFCE Desktop) để dùng GPU thật, lách qua con mắt soi Xvfb của Google.
4. Crawler tự động mở Google Flow. Nếu đang ở sẵn trang Project, bỏ qua bước F5 tải lại trang để tránh hành vi tải trang liên tục của Bot.
5. Dùng ActionChains click nút `+` -> Chọn `Uploads` -> Click `Add to prompt` ở ảnh logo đã có sẵn.
6. Sử dụng CDP để nạp siêu tốc Text prompt vào khung chat. ActionChains di chuột bấm nút Send.
7. Đợi ảnh mới xuất hiện bằng cách quét liên tục thay đổi DOM của các thẻ `<img>`.
8. Tiêm JS để Fetch trực tiếp ảnh mới nhất, decode sang Base64 và ghi vào thư mục `downloads/`.
9. Trả cục dữ liệu JSON chuẩn Gemini về cho Client qua luồng Streaming đang mở. (Các bộ parse JSON phía client sẽ tự động xóa các khoảng trắng rác ở đầu).
10. Queue Worker tự động Sleep ngẫu nhiên 30-45 giây để đánh lừa thuật toán tần suất của Google trước khi nhận request tiếp theo.
11. Quản lý Zombie & Proxy: Sau mỗi 30 request (hoặc khi Google rate-limit), hệ thống tự động tắt trình duyệt, gọi hàm `force_kill_chrome()` diệt sạch các tiến trình `chrome`, `chromium`, `chromedriver` bị treo, xóa file `SingletonLock` rồi xoay Session Proxy mới.
