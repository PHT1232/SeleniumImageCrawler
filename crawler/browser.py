import undetected_chromedriver as uc
import os
import re
import uuid

# Global session ID cho Proxy-Cheap để quản lý Sticky IP programmatically
current_session_id = str(uuid.uuid4())[:8]

def rotate_proxy_session():
    global current_session_id
    current_session_id = str(uuid.uuid4())[:8]
    print(f"[*] Đã xoay Proxy Session ID mới: {current_session_id}")

def force_kill_chrome():
    """Ép diệt toàn bộ tiến trình Chrome và ChromeDriver bị treo để giải phóng RAM và Lock file."""
    try:
        import time
        os.system("pkill -9 -f chrome")
        os.system("pkill -9 -f chromedriver")
        
        # Xóa các file lock của Chrome profile để tránh lỗi SessionNotCreatedException
        profile_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'chrome_profile'))
        default_dir = os.path.join(profile_dir, "Default")
        
        for base_dir in [profile_dir, default_dir]:
            for lock_file in ["SingletonLock", "SingletonCookie", "SingletonSocket"]:
                lf = os.path.join(base_dir, lock_file)
                if os.path.exists(lf):
                    try:
                        if os.path.islink(lf):
                            os.unlink(lf)
                        else:
                            os.remove(lf)
                    except:
                        pass
        print("[*] Đã dọn dẹp các tiến trình Chrome cũ và xóa file Lock.")
        # Ngủ 2 giây để hệ điều hành có thời gian nhả Port và dọn rác hoàn toàn
        time.sleep(2)
    except Exception as e:
        print(f"Lỗi khi dọn dẹp Chrome: {e}")

def get_driver(headless: bool = False):
    """
    Khởi tạo và cấu hình Trình duyệt ẩn danh (Undetected Chrome WebDriver).
    """
    options = uc.ChromeOptions()
    if headless:
        options.add_argument("--headless")
    
    # Một số option cấu hình UI
    options.add_argument("--start-maximized")
    options.add_argument("--disable-notifications")
    
    # Rất quan trọng khi chạy trên Server Linux dưới quyền Root
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    
    # Đọc cấu hình Proxy từ file proxy_config.txt (nếu có)
    proxy_file = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'proxy_config.txt'))
    if os.path.exists(proxy_file):
        with open(proxy_file, 'r') as f:
            proxy = f.read().strip()
            if proxy:
                # Tự động ghi đè Session ID cho Proxy-Cheap để xoay IP chủ động
                if "proxy-cheap.com" in proxy:
                    try:
                        credentials, host_port = proxy.split('@')
                        if ':' in credentials:
                            user, pwd = credentials.split(':', 1)
                        else:
                            user, pwd = "", credentials
                            
                        # Thay thế session cũ (nếu có) bằng session động
                        if "_session-" in user or "_session-" in pwd:
                            user = re.sub(r'_session-[a-zA-Z0-9_-]+', f'_session-{current_session_id}', user)
                            pwd = re.sub(r'_session-[a-zA-Z0-9_-]+', f'_session-{current_session_id}', pwd)
                        else:
                            if pwd and not user:
                                pwd += f"_session-{current_session_id}"
                            else:
                                user += f"_session-{current_session_id}"
                                
                        if user:
                            proxy = f"{user}:{pwd}@{host_port}"
                        else:
                            proxy = f"{pwd}@{host_port}"
                    except Exception as e:
                        print(f"Lỗi inject proxy session: {e}")
                        
                if '@' in proxy:
                    from crawler.proxy_extension import create_proxy_auth_extension
                    ext_dir = create_proxy_auth_extension(proxy, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'proxy_auth_plugin')))
                    if ext_dir:
                        print(f"[*] Đang khởi tạo Trình duyệt với Proxy (Unpacked Extension): {proxy}")
                        options.add_argument(f"--load-extension={ext_dir}")
                else:
                    print(f"[*] Đang khởi tạo Trình duyệt với Proxy: {proxy}")
                    options.add_argument(f"--proxy-server=http://{proxy}")
    
    # Cấu hình user profile để lưu session login google
    profile_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'chrome_profile'))
    
    # Cấu hình thư mục tải về mặc định và CHỐNG RÒ RỈ IP (WebRTC)
    download_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'downloads'))
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        # Chặn WebRTC rò rỉ IP thật ra ngoài (Bắt buộc khi dùng Proxy)
        "webrtc.ip_handling_policy": "disable_non_proxied_udp",
        "webrtc.multiple_routes_enabled": False,
        "webrtc.nonproxied_udp_enabled": False
    }
    options.add_experimental_option("prefs", prefs)
    
    # Tạo driver sử dụng undetected_chromedriver
    driver = uc.Chrome(
        options=options, 
        use_subprocess=True, 
        user_data_dir=profile_dir, 
        browser_executable_path="/usr/bin/google-chrome"
    )
    
    return driver
