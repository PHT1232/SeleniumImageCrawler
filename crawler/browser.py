import undetected_chromedriver as uc
import os

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
            # Bỏ dấu @ nếu sếp lỡ copy cả user:pass, ép dùng IP:PORT
            if '@' in proxy:
                proxy = proxy.split('@')[-1]
            if proxy:
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
