import time
import base64
import os
import glob
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains

def login_google(driver, email=None, password=None):
    pass

def navigate_to_flow(driver, url="https://labs.google/fx/tools/flow/project/93a244b7-7817-4bbb-a97c-1fd971f7da66"):
    current_url = driver.current_url
    if current_url and current_url.startswith(url):
        print("Đang ở sẵn trang Project, tiến hành F5 tải lại trang để dọn dẹp sạch sẽ bộ nhớ tạm (Chống lỗi State Corruption)...")
        driver.refresh()
        time.sleep(5)
    else:
        print(f"Đang truy cập: {url}")
        driver.get(url)
        time.sleep(5)
    
    # Xử lý trường hợp bị chặn ở màn hình Welcome (Click Create with Google Flow)
    try:
        create_btn = driver.find_elements(By.XPATH, "//*[contains(text(), 'Create with Google Flow')]")
        if create_btn:
            print("Phát hiện màn hình Welcome, đang click 'Create with Google Flow'...")
            from selenium.webdriver.common.action_chains import ActionChains
            ActionChains(driver).move_to_element(create_btn[0]).click().perform()
            time.sleep(5)
            # Sau khi click, trình duyệt có thể điều hướng đi chỗ khác, ta ép nó về lại đúng Project ID
            print("Đang truy cập lại vào Project của chúng ta...")
            driver.get(url)
            time.sleep(5)
    except Exception as e:
        pass 

def select_logo_from_uploads(driver):
    wait = WebDriverWait(driver, 10)
    print("Đang tìm nút '+'...")
    time.sleep(random.uniform(0.5, 1.5))
    
    try:
        # Khôi phục nút add_2: Đây mới là nút + ở dưới khung chat, nút add thường nằm ở Header
        add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//i[text()='add_2']]")))
        ActionChains(driver).move_to_element(add_btn).pause(random.uniform(0.1, 0.3)).click().perform()
    except Exception as e:
        driver.save_screenshot("debug.png")
        print("Lỗi click nút +, thử fallback:", e)
        # Fallback lấy nút add cuối cùng nếu add_2 không tồn tại
        add_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "(//button[.//i[text()='add']])[last()]")))
        ActionChains(driver).move_to_element(add_btn).pause(random.uniform(0.1, 0.3)).click().perform()
        
    time.sleep(random.uniform(1.0, 2.0))
    
    print("Đang chọn menu 'Uploads'...")
    try:
        # Khôi phục cơ chế duyệt ngược từ cuối (do Uploads popup nằm sau trong DOM)
        uploads_elements = driver.find_elements(By.XPATH, "//*[text()='Uploads' or text()='Tải lên']")
        clicked = False
        for el in reversed(uploads_elements):
            if el.is_displayed() and el.location['x'] > 200: # Bỏ qua Uploads menu trái
                ActionChains(driver).move_to_element(el).pause(random.uniform(0.1, 0.3)).click().perform()
                clicked = True
                break
        if not clicked and uploads_elements:
            ActionChains(driver).move_to_element(uploads_elements[-1]).pause(random.uniform(0.1, 0.3)).click().perform()
    except Exception as e:
        print(f"Lỗi chọn menu Uploads: {e}")
        
    time.sleep(random.uniform(2.0, 3.0)) # Đợi popup và list ảnh tải xong
    
    print("Đang tìm nút 'Add to prompt'...")
    try:
        # Thử hover vào ảnh đầu tiên để nút Add to prompt hiện lên (Google đổi UI)
        first_image_container = driver.find_elements(By.XPATH, "(//div[contains(@class, 'container') and .//img])[1]")
        if first_image_container:
            ActionChains(driver).move_to_element(first_image_container[0]).perform()
            time.sleep(random.uniform(0.5, 1.0))
            
        # Khôi phục multi XPath mạnh mẽ cho nút Add
        add_to_prompt_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Add to prompt') or contains(text(), 'Add to Prompt') or contains(text(), 'Thêm vào lời nhắc')] | //*[contains(text(), 'Add to prompt')] | (//button[.//span[contains(text(), 'Add to prompt')]])[1]")))
        ActionChains(driver).move_to_element(add_to_prompt_btn).pause(random.uniform(0.1, 0.3)).click().perform()
    except Exception as e:
        print(f"Lỗi click Add to prompt: {e}")
        
    print("Đợi 3 giây để ảnh Logo được Google load thành công vào khung chat...")
    time.sleep(3)

def paste_prompt_text(driver, prompt_text: str):
    print("Đang dán prompt...")
    try:
        import re
        import sys
        
        wait = WebDriverWait(driver, 10)
        # CHÚ Ý QUAN TRỌNG: Lấy đúng phần tử Slate editor
        slate_editor = wait.until(EC.element_to_be_clickable((By.XPATH, "//div[@role='textbox' and @data-slate-editor='true']")))
        
        # 1. Bảo hiểm kép: Focus bằng JS và Click CDP vào TÂM KHUNG CHAT
        driver.execute_script("window.focus();")
        driver.execute_script("arguments[0].focus();", slate_editor)
        time.sleep(0.5)
        
        # Click vào editor để focus bằng Natural Mouse Move
        print("Đang click vào khung chat bằng Natural Mouse Move...")
        ActionChains(driver).move_to_element(slate_editor).pause(random.uniform(0.1, 0.3)).click().perform()
        time.sleep(0.5)
        
        # 2. Bắn Text siêu tốc bằng CDP (Từng dòng)
        print("\n>> ĐANG NẠP CHỮ VÀO KHUNG CHAT BẰNG CDP (INSERT TEXT)...")
        lines = prompt_text.split('\n')
        for i, line in enumerate(lines):
            # Lọc bỏ các dòng trống dư thừa
            if line.strip() or i < len(lines) - 1:
                if line:
                    driver.execute_cdp_cmd('Input.insertText', {'text': line})
                
                # Nối dòng bằng Shift+Enter (Giả lập phần cứng qua CDP)
                if i < len(lines) - 1:
                    time.sleep(0.05)
                    # Giữ phím Shift
                    driver.execute_cdp_cmd('Input.dispatchKeyEvent', {'type': 'rawKeyDown', 'windowsVirtualKeyCode': 16, 'modifiers': 8})
                    # Nhấn nhả phím Enter
                    driver.execute_cdp_cmd('Input.dispatchKeyEvent', {'type': 'keyDown', 'windowsVirtualKeyCode': 13, 'modifiers': 8})
                    driver.execute_cdp_cmd('Input.dispatchKeyEvent', {'type': 'keyUp', 'windowsVirtualKeyCode': 13, 'modifiers': 8})
                    # Nhả phím Shift
                    driver.execute_cdp_cmd('Input.dispatchKeyEvent', {'type': 'keyUp', 'windowsVirtualKeyCode': 16, 'modifiers': 0})
            time.sleep(0.05)
                
        time.sleep(2)
        
        # TRƯỚC KHI BẤM GỬI: Ghi nhớ đường link của TẤT CẢ các bức ảnh đang có trên màn hình
        # Bỏ qua các ảnh có chứa chữ THUMBNAIL (chính là cái logo đính kèm)
        result_imgs = driver.find_elements(By.XPATH, "//img[contains(@src, 'media.getMediaUrlRedirect') and not(contains(@src, 'THUMBNAIL'))]")
        old_srcs = [img.get_attribute("src") for img in result_imgs if img.get_attribute("src")]
        
        # Ghi nhớ số lượng thông báo lỗi cũ đang có trong lịch sử chat
        old_errors_count = len(driver.find_elements(By.XPATH, "//*[contains(text(), 'Something went wrong')]"))
        
        # 3. Tìm nút Gửi (Mũi tên)
        print("Đang bấm nút gửi bằng Natural Mouse Move...")
        try:
            send_btn = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[.//i[text()='arrow_forward']]")))
            if send_btn.get_attribute("aria-disabled") == "true":
                time.sleep(1)
                
            # Click bằng ActionChains để mô phỏng di chuột thực tế
            ActionChains(driver).move_to_element(send_btn).pause(random.uniform(0.1, 0.3)).click().perform()
            
        except Exception as e:
            print(f"Lỗi khi ấn nút Send: {e}")
        
        return {"old_srcs": old_srcs, "old_errors_count": old_errors_count}
            
    except Exception as e:
        print(f"Lỗi nhập prompt: {e}")
        return None

def wait_for_image_load_and_download(driver, prompt_context):
    """Đợi quá trình sinh ảnh kết thúc, click và download"""
    old_srcs = prompt_context["old_srcs"]
    old_errors_count = prompt_context["old_errors_count"]
    
    print("Đang đợi ảnh mới xuất hiện (Quét liên tục mỗi 5s)...")
    wait_long = WebDriverWait(driver, 240, poll_frequency=5)
    
    try:
        try_again_count = [0]
        
        def check_new_image(d):
            try:
                # 1. Quét tìm nút "Try again" (Nhanh và chính xác nhất)
                try_again_btns = d.find_elements(By.XPATH, "//button[.//span[contains(text(), 'Try again')] or contains(text(), 'Try again')]")
                if try_again_btns and any(btn.is_displayed() for btn in try_again_btns):
                    if try_again_count[0] < 3:
                        print(f"[Anti-Bot] Phát hiện lỗi, tự động bấm 'Try again' lần {try_again_count[0] + 1}/3...")
                        d.execute_script("arguments[0].click();", try_again_btns[-1])
                        try_again_count[0] += 1
                        time.sleep(5) # Nghỉ 5s cho UI kịp update
                        return False # Quay lại vòng lặp chờ
                    else:
                        raise RuntimeError("Đã tự động bấm Try again 3 lần nhưng vẫn thất bại (Google đã block IP này).")
                
                # Cảnh báo lỗi chung nếu không có nút Try again
                error_msg = d.find_elements(By.XPATH, "//*[contains(text(), 'Something went wrong')]")
                if error_msg and any(el.is_displayed() for el in error_msg):
                    # Đảm bảo đây không phải là lỗi cũ (Bằng cách check xem số lượng lỗi có tăng không)
                    if len(error_msg) > old_errors_count:
                        raise RuntimeError("Google Flow báo lỗi: Something went wrong nhưng không có nút Try again.")
                
                
                # 2. Quét tìm ảnh mới
                imgs = d.find_elements(By.XPATH, "//img[contains(@src, 'media.getMediaUrlRedirect') and not(contains(@src, 'THUMBNAIL'))]")
                for img in imgs:
                    src = img.get_attribute("src")
                    if src and src not in old_srcs:
                        # Kiểm tra xem ảnh đã load 100% data từ network chưa
                        is_loaded = d.execute_script("return arguments[0].complete && typeof arguments[0].naturalWidth != 'undefined' && arguments[0].naturalWidth > 0;", img)
                        if is_loaded:
                            return img
                return False
            except Exception:
                # Nếu phần tử bị DOM làm mới (StaleElementReferenceException), bỏ qua và thử lại
                return False
            
        result_img_from_wait = wait_long.until(check_new_image)
        print("Đã phát hiện ảnh mới! Đang tiến hành tải ngầm (Bypass UI)...")
        
        # Lấy URL của ảnh mới nhất (bỏ qua Thumbnail)
        fresh_img = driver.find_elements(By.XPATH, "//img[contains(@src, 'media.getMediaUrlRedirect') and not(contains(@src, 'THUMBNAIL'))]")[-1]
        image_url = fresh_img.get_attribute("src")
        print(f"URL ảnh: {image_url}")
        
        # Tiêm Javascript fetch ảnh và chuyển thành Base64
        base64_string = driver.execute_async_script("""
            var url = arguments[0];
            var callback = arguments[1];
            
            fetch(url)
                .then(response => response.blob())
                .then(blob => {
                    var reader = new FileReader();
                    reader.onloadend = function() {
                        callback(reader.result);
                    }
                    reader.readAsDataURL(blob);
                })
                .catch(error => {
                    callback("ERROR: " + error.message);
                });
        """, image_url)
        
        if base64_string.startswith("ERROR"):
            print("Lỗi tải ngầm ảnh:", base64_string)
            return False
            
        print("Đã lấy được dữ liệu Base64! Đang lưu thành file...")
        base64_data = base64_string.split(',')[1]
        
        filename = f"downloads/cyberpunk_fashion_{int(time.time())}.png"
        os.makedirs("downloads", exist_ok=True)
        with open(filename, "wb") as fh:
            fh.write(base64.b64decode(base64_data))
            
        print(f"=====================================")
        print(f"TẢI ẢNH THÀNH CÔNG! File: {filename}")
        print(f"=====================================")
        
        return {
            "candidates": [
                {
                    "content": {
                        "parts": [
                            {
                                "inlineData": {
                                    "mimeType": "image/png",
                                    "data": base64_data
                                }
                            }
                        ]
                    }
                }
            ]
        }
        
    except Exception as e:
        print(f"Lỗi khi đợi ảnh mới: {type(e).__name__} - {e}")
        try:
            driver.save_screenshot("error_wait_image.png")
            print("Đã lưu screenshot lỗi tại error_wait_image.png để kiểm tra (có thể do timeout 90s chưa thấy ảnh mới hoặc sai XPath).")
            with open("error_page_source.html", "w", encoding="utf-8") as f:
                f.write(driver.page_source)
        except Exception as ex:
            print(f"Không thể lưu screenshot lỗi: {ex}")
        return False
