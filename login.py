import time
from crawler.browser import get_driver

print("Đang khởi động Chrome...")
# Lấy driver (headless=False để hiện giao diện)
driver = get_driver(headless=False)

print("Mở trang Google Flow...")
driver.get("https://labs.google/fx/tools/flow/project/93a244b7-7817-4bbb-a97c-1fd971f7da66")

print("=========================================================")
print("VUI LÒNG ĐĂNG NHẬP VÀO TÀI KHOẢN GOOGLE CỦA BẠN!")
print("Sau khi đăng nhập thành công và thấy giao diện như ảnh 1,")
print("hãy quay lại Terminal này và bấm Ctrl+C để đóng trình duyệt.")
print("=========================================================")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Đang lưu phiên đăng nhập và đóng trình duyệt...")
    driver.quit()
    print("Xong! Bây giờ bạn có thể dùng API.")
