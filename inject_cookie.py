import undetected_chromedriver as uc
import time
import os

def run():
    print("Đang khởi động Chrome...")
    profile_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), 'chrome_profile'))
    options = uc.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    
    driver = uc.Chrome(options=options, use_subprocess=True, user_data_dir=profile_dir, browser_executable_path="/usr/bin/google-chrome")
    
    print("Mở trang Google...")
    driver.get("https://google.com")
    time.sleep(2)
    
    print("Đang nhồi Cookie vào trình duyệt...")
    try:
        with open("cookie_string.txt", "r") as f:
            raw_cookie = f.read().strip()
            
        cookie_items = raw_cookie.split(';')
        for item in cookie_items:
            if '=' in item:
                name, value = item.strip().split('=', 1)
                cookie_dict = {
                    'name': name,
                    'value': value,
                    'domain': '.google.com',
                    'secure': True,
                    'httpOnly': True
                }
                try:
                    driver.add_cookie(cookie_dict)
                except Exception as e:
                    pass
        print("Nhồi Cookie thành công!")
    except Exception as e:
        print("Lỗi đọc file cookie_string.txt:", e)
        
    print("Đang truy cập tài khoản Google để kích hoạt...")
    driver.get("https://accounts.google.com")
    time.sleep(5)
    
    driver.save_screenshot("verify_login.png")
    print("Đã chụp ảnh verify_login.png. Bạn có thể kiểm tra xem đã login thành công chưa!")
    driver.quit()

if __name__ == "__main__":
    run()
