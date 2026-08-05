import undetected_chromedriver as uc
import time
import os
import json

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
        with open("cookies.json", "r") as f:
            cookies = json.load(f)
            for cookie in cookies:
                # Xóa các trường không tương thích
                if 'sameSite' in cookie and cookie['sameSite'] not in ["Strict", "Lax", "None"]:
                    del cookie['sameSite']
                if 'storeId' in cookie:
                    del cookie['storeId']
                try:
                    driver.add_cookie(cookie)
                except Exception as e:
                    pass
        print("Nhồi Cookie thành công!")
    except Exception as e:
        print("Lỗi đọc file cookies.json:", e)
        
    print("Đang truy cập lại Google Flow để kiểm tra...")
    driver.get("https://labs.google/fx/tools/flow")
    time.sleep(5)
    
    driver.save_screenshot("verify_login.png")
    print("Đã chụp ảnh verify_login.png. Bạn có thể kiểm tra xem đã login thành công chưa!")
    driver.quit()

if __name__ == "__main__":
    run()
