from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import base64

print("Đang kết nối vào trình duyệt Chrome hiện tại...")
chrome_options = Options()
chrome_options.add_experimental_option("debuggerAddress", "127.0.0.1:9222")
driver = webdriver.Chrome(options=chrome_options)

# URL ảnh cà phê mà bạn vừa gửi lúc nãy
image_url = "/fx/api/trpc/media.getMediaUrlRedirect?name=32a20f79-dabb-4599-9b78-bfa4b74fce94"
print(f"Đang tải thử ảnh ngầm từ URL: {image_url}...")

script = """
var url = arguments[0];
var callback = arguments[1];

fetch(url)
    .then(response => {
        if (!response.ok) {
            throw new Error('HTTP error ' + response.status);
        }
        return response.blob();
    })
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
"""

# Tăng thời gian chờ async script lên 15s
driver.set_script_timeout(15)

try:
    base64_string = driver.execute_async_script(script, image_url)
    
    if base64_string.startswith("ERROR"):
        print("LỖI: Không thể tải ảnh ->", base64_string)
    else:
        print("TẢI ẢNH THÀNH CÔNG! Đang ghi ra file...")
        base64_data = base64_string.split(',')[1]
        
        filename = "test_coffee_fetch.png"
        with open(filename, "wb") as fh:
            fh.write(base64.b64decode(base64_data))
        print(f"Đã lưu thành công: {filename}")
        
except Exception as e:
    print(f"Lỗi hệ thống: {e}")
