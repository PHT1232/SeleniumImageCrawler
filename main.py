from fastapi import FastAPI
import uvicorn
from api.routes import router
from api_request_lock import request_queue

app = FastAPI(
    title="Selenium Crawler API",
    description="API for Google Imagen Flow automation using Selenium",
    version="1.0.0"
)

app.include_router(router)

@app.on_event("startup")
async def startup_event():
    request_queue.start()
    print(">> Đã khởi động Hệ thống Xếp hàng API (Queue Worker)")

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Selenium Crawler API is running"}

if __name__ == "__main__":
    # Chạy server với uvicorn, port 8989
    uvicorn.run("main:app", host="127.0.0.1", port=8989, reload=True)
