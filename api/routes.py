from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional, List
from crawler.browser import get_driver
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

def get_shared_driver():
    global _driver
    if _driver is None:
        # User yêu cầu hiện giao diện debug trước nên headless=False
        _driver = get_driver(headless=False)
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
    global image_count, _driver
    
    # Tự động xoay Proxy sau mỗi 30 request
    if image_count > 0 and image_count % 30 == 0:
        if _driver is not None:
            print(f"[*] Đã đạt mốc {image_count} ảnh. Đang tiến hành tắt trình duyệt để đổi sang IP Proxy mới...")
            try:
                _driver.quit()
            except:
                pass
            _driver = None
            
    driver = get_shared_driver()
    
    # 1. Mở trang Google Flow
    navigate_to_flow(driver)
    
    # 2. Bấm dấu +, chọn Uploads, và Add logo vào prompt
    select_logo_from_uploads(driver)
    
    # 3. Paste Text prompt (Sẽ bao gồm cả enter/click send)
    old_srcs = paste_prompt_text(driver, prompt)
    
    # 4. Đợi ảnh sinh ra (Dynamic Wait) và Download file trả về
    result = wait_for_image_load_and_download(driver, old_srcs)
    
    image_count += 1
    return result

@router.post("/generate")
async def generate_image_api(request: GenerateRequest):
    try:
        # Trích xuất dữ liệu từ format mới (Giống Gemini API)
        prompt = ""
        if request.contents and len(request.contents) > 0:
            for part in request.contents[0].parts:
                if part.text:
                    prompt = part.text
        
        if not prompt:
            raise HTTPException(status_code=400, detail="Missing text prompt in request")

        # Đẩy request vào hàng đợi và đợi (await) kết quả trả về
        result = await request_queue.enqueue(run_selenium_generation, prompt)
        return result
        
    except Exception as e:
        import traceback
        print("\n=== LỖI NGHIÊM TRỌNG TRONG QUÁ TRÌNH XỬ LÝ ===")
        traceback.print_exc()
        print("===============================================\n")
        raise HTTPException(status_code=500, detail=f"Lỗi hệ thống: {str(e)}")
