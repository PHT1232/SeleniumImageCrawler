import time
import os
import json
import undetected_chromedriver as uc

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def main():
    if not os.path.exists(CONFIG_PATH):
        print(f"Không tìm thấy {CONFIG_PATH}. Vui lòng tạo file trước.")
        return
        
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
        
    accounts = data.get("accounts", [])
    if not accounts:
        print("Không có tài khoản nào trong config.json")
        return
        
    print("=== CHỌN TÀI KHOẢN ĐỂ ĐĂNG NHẬP ===")
    for i, acc in enumerate(accounts):
        print(f"{i + 1}. {acc['id']} (Profile: {acc['profile_dir']})")
        
    try:
        choice = int(input("\nNhập số thứ tự tài khoản: "))
        if choice < 1 or choice > len(accounts):
            print("Lựa chọn không hợp lệ!")
            return
    except ValueError:
        print("Vui lòng nhập số!")
        return
        
    selected_acc = accounts[choice - 1]
    profile_dir = selected_acc["profile_dir"]
    user_data_dir = os.path.abspath(profile_dir)
    os.makedirs(user_data_dir, exist_ok=True)
    
    print(f"\n[*] Đang khởi động trình duyệt cho tài khoản {selected_acc['id']}...")
    print(f"[*] Profile Directory: {user_data_dir}")
    print("[!] Hãy đăng nhập vào Google. Sau khi đăng nhập xong, hãy đóng trình duyệt.")

    options = uc.ChromeOptions()
    options.add_argument(f"--user-data-dir={user_data_dir}")
    # Fix X11 permission when running as root
    options.add_argument("--no-sandbox")

    driver = uc.Chrome(options=options, version_main=127) # Change version_main if your chrome is different

    driver.get("https://accounts.google.com")

    # Giữ script chạy cho đến khi người dùng tự đóng trình duyệt
    while True:
        try:
            # Kiểm tra xem trình duyệt còn mở không
            driver.title
            time.sleep(1)
        except:
            break

    print("\n[*] Đã đóng trình duyệt. Session đã được lưu thành công vào:")
    print(user_data_dir)

if __name__ == "__main__":
    main()
