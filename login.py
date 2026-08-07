import time
import os
import json
import undetected_chromedriver as uc

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "config.json")

def load_config():
    if not os.path.exists(CONFIG_PATH):
        # Tự động tạo file config trống nếu chưa có
        return {"accounts": []}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except:
            return {"accounts": []}

def save_config(data):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)

def main():
    data = load_config()
    accounts = data.get("accounts", [])
        
    print("=== QUẢN LÝ TÀI KHOẢN GOOGLE ===")
    for i, acc in enumerate(accounts):
        print(f"{i + 1}. Đăng nhập lại: {acc['id']} (Profile: {acc['profile_dir']})")
    print("N. Thêm tài khoản Google MỚI")
    
    choice_str = input("\nNhập số thứ tự hoặc 'N' để thêm mới: ").strip().upper()
    
    if choice_str == 'N':
        new_id = input("Nhập ID (Tên) cho tài khoản mới (Ví dụ: gmail_2): ").strip()
        if not new_id:
            print("Tên không được để trống!")
            return
        if any(a['id'] == new_id for a in accounts):
            print("Lỗi: ID này đã tồn tại trong config.json!")
            return
            
        new_project = input("Nhập URL của Google Flow Project cho tài khoản này: ").strip()
        if not new_project:
            print("URL không được để trống!")
            return
            
        new_profile_dir = f"chrome_profile_{new_id}"
        new_acc = {
            "id": new_id,
            "profile_dir": new_profile_dir,
            "projects": [new_project]
        }
        accounts.append(new_acc)
        data["accounts"] = accounts
        save_config(data)
        print(f"[*] Đã lưu cấu hình tài khoản '{new_id}' vào config.json!")
        selected_acc = new_acc
    else:
        try:
            choice = int(choice_str)
            if choice < 1 or choice > len(accounts):
                print("Lựa chọn không hợp lệ!")
                return
            selected_acc = accounts[choice - 1]
        except ValueError:
            print("Vui lòng nhập số hợp lệ hoặc 'N'!")
            return
        
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
