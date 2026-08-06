from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from contextlib import asynccontextmanager
import uvicorn
from api.routes import router
from api_request_lock import request_queue

from crawler.browser import force_kill_chrome

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Dọn dẹp Zombie Chrome từ các lần chạy trước (do bị crash hoặc Ctrl+C)
    force_kill_chrome()
    
    request_queue.start()
    print(">> Đã khởi động Hệ thống Xếp hàng API (Queue Worker)")
    yield

app = FastAPI(
    title="Selenium Crawler API",
    description="API for Google Imagen Flow automation using Selenium",
    version="1.0.0",
    lifespan=lifespan
)

app.include_router(router)

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Selenium Crawler API is running"}

@app.websocket("/notifications/hub")
async def dummy_websocket(websocket: WebSocket):
    # Chấp nhận kết nối websocket để phần mềm tự động không bị lỗi 403/404
    await websocket.accept()
    try:
        while True:
            # Lắng nghe và bỏ qua các tin nhắn đến
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass

@app.post("/identity/connect/token")
async def dummy_token():
    # Trả về một token giả để đánh lừa các phần mềm tự động (giúp tắt log 404 Not Found)
    return {
        "access_token": "fake-token-bypass",
        "token_type": "Bearer",
        "expires_in": 31536000
    }

if __name__ == "__main__":
    # Chạy server với uvicorn, port 8989
    uvicorn.run("main:app", host="127.0.0.1", port=8989, reload=True)
