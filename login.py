import time
import undetected_chromedriver as uc
import os

print("Đang khởi động Chrome ở chế độ Remote Debugging...")

options = uc.ChromeOptions()
options.add_argument("--start-maximized")
options.add_argument("--disable-notifications")
options.add_argument("--remote-debugging-port=9222")
options.add_argument("--remote-debugging-address=0.0.0.0")

profile_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'chrome_profile'))
driver = uc.Chrome(
    options=options, 
    use_subprocess=True, 
    user_data_dir=profile_dir, 
    browser_executable_path="/usr/bin/google-chrome"
)

driver.get("https://accounts.google.com")

print("=========================================================")
print("TÍNH NĂNG REMOTE DEBUGGING ĐÃ BẬT TRÊN CỔNG 9222!")
print("Từ máy tính cá nhân của bạn, hãy mở một Terminal mới và gõ:")
print("ssh -L 9222:localhost:9222 root@dia_chi_ip_may_chu_fedora")
print("\nSau đó mở Chrome trên máy cá nhân và truy cập:")
print("http://localhost:9222")
print("=========================================================")

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Đang đóng trình duyệt và lưu phiên...")
    driver.quit()
    print("Xong!")
