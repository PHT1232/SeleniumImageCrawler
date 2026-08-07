from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from crawler.browser import get_driver, rotate_proxy_session, force_kill_chrome
from crawler.actions import (
    navigate_to_flow,
    select_logo_from_uploads,
    paste_prompt_text,
    wait_for_image_load_and_download
)
from api_request_lock import request_queue

router = APIRouter()

# Biến toàn cục để giữ WebDriver luôn mở
_driver = None
image_count = 0
proxy_mode = False  # Ban đầu dùng IP thật, chỉ bật proxy khi bị block

def get_shared_driver():
    global _driver
    if _driver is None:
        if proxy_mode:
            print("[*] Chế độ PROXY: Đang dùng Proxy làm backup do IP thật bị block...")
        else:
            print("[*] Chế độ IP THẬT: Đang dùng IP server trực tiếp (không qua Proxy)...")
        # Vì máy đã có giao diện Desktop (XFCE) và màn hình thật, ta tắt headless để qua mặt Anti-bot
        _driver = get_driver(headless=False, use_proxy=proxy_mode)
    return _driver

class InlineData(BaseModel):
    mime_type: Optional[str] = None
    data: Optional[str] = None

class Part(BaseModel):
    inline_data: Optional[InlineData] = None
    text: Optional[str] = None

class Content(BaseModel):
    parts: List[Part]

class GenerationConfig(BaseModel):
    responseModalities: Optional[List[str]] = None
    temperature: Optional[float] = None

class GenerateRequest(BaseModel):
    contents: List[Content]
    generationConfig: Optional[GenerationConfig] = None

def run_selenium_generation(prompt: str):
    """Hàm đồng bộ chạy các lệnh Selenium, sẽ được đưa vào ThreadPool"""
    global image_count, _driver, proxy_mode
    import time
    
    attempt = 0
    consecutive_fails = 0  # Đếm số lần fail LIÊN TIẾP với cùng 1 IP
    
    while True:
        attempt += 1
        
        # Tự động xoay Proxy sau mỗi 30 request
        if image_count > 0 and image_count % 30 == 0:
            if _driver is not None:
                print(f"[*] Đã đạt mốc {image_count} ảnh. Đang tiến hành tắt trình duyệt để đổi sang IP Proxy mới...")
                try:
                    _driver.quit()
                except:
                    pass
                force_kill_chrome()
                _driver = None
                consecutive_fails = 0
                
        driver = get_shared_driver()
        
        try:
            # 1. Mở trang Google Flow
            navigate_to_flow(driver)
            
            # 2. Bấm dấu +, chọn Uploads, và Add logo vào prompt
            select_logo_from_uploads(driver)
            
            # 3. Paste Text prompt (Sẽ bao gồm cả enter/click send)
            prompt_context = paste_prompt_text(driver, prompt)
            
            # 4. Đợi ảnh sinh ra (Dynamic Wait) và Download file trả về
            result = wait_for_image_load_and_download(driver, prompt_context)
            
            image_count += 1
            consecutive_fails = 0
            return result
        except Exception as e:
            error_str = str(e)
            if "Account Quota Limit" in error_str or "quota limit" in error_str.lower():
                print(f"[-] LỖI CHÍ MẠNG: Tài khoản Google này đã bị hết lượt sử dụng trong ngày (Quota Limit).")
                print(f"[-] Xoay IP không có tác dụng. Vui lòng dừng script, chạy python3 login.py để đăng nhập tài khoản Google khác!")
                try:
                    _driver.quit()
                except:
                    pass
                force_kill_chrome()
                _driver = None
                raise e # Ném thẳng lỗi ra API để Client biết đường dừng gửi request
                
            if "Google đã block IP này" in error_str or "Google Flow báo lỗi" in error_str:
                print(f"[*] Google Flow đã chặn IP này (Soft/Hard block). Chờ 60s (1 phút) rồi xoay IP/Khởi động lại Trình duyệt ngay lập tức...")
                time.sleep(60)
                # Bật Proxy mode và xoay IP cứng
                proxy_mode = True
                rotate_proxy_session()
                try:
                    _driver.quit()
                except:
                    pass
                force_kill_chrome()
                _driver = None
                consecutive_fails = 0
                continue
            
            # Lỗi không phải do IP block (lỗi code, lỗi logic...) → mới báo ra ngoài
            raise e

@router.post("/generate")
async def generate_image_api(request: GenerateRequest):
    # Trích xuất dữ liệu từ format mới (Giống Gemini API)
    prompt = ""
    if request.contents and len(request.contents) > 0:
        for part in request.contents[0].parts:
            if part.text:
                prompt = part.text
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Missing text prompt in request")

    import asyncio
    import json
    from fastapi.responses import StreamingResponse

    async def generate_with_keepalive():
        # Khởi tạo Task chạy ngầm
        task = asyncio.create_task(request_queue.enqueue(run_selenium_generation, prompt))
        
        # Trong lúc Task đang chạy (xếp hàng + vẽ ảnh), mỗi 15 giây nhả ra 1 khoảng trắng
        while not task.done():
            yield b" "
            await asyncio.sleep(15)
            
        # Khi Task hoàn thành, lấy kết quả
        try:
            result = task.result()
            # Nhả nốt cục JSON xịn ra
            yield json.dumps(result).encode('utf-8')
        except Exception as e:
            import traceback
            print("\n=== LỖI NGHIÊM TRỌNG TRONG QUÁ TRÌNH XỬ LÝ ===")
            traceback.print_exc()
            print("===============================================\n")
            error_json = {"detail": f"Lỗi hệ thống: {str(e)}"}
            yield json.dumps(error_json).encode('utf-8')

    # Trả về StreamingResponse, lừa Cloudflare rằng dữ liệu vẫn đang chảy
    return StreamingResponse(generate_with_keepalive(), media_type="application/json")
