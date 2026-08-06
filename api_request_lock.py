import asyncio
from concurrent.futures import ThreadPoolExecutor

class APIRequestQueue:
    def __init__(self):
        # Hàng đợi chứa các request
        self.queue = asyncio.Queue()
        self.worker_task = None
        # ThreadPoolExecutor để chạy các hàm Selenium (vốn là đồng bộ) mà không làm treo server FastAPI
        self.executor = ThreadPoolExecutor(max_workers=1)

    def start(self):
        """Khởi động worker ngầm để xử lý queue"""
        if self.worker_task is None:
            self.worker_task = asyncio.create_task(self._worker())

    async def _worker(self):
        """Worker lấy từng request ra khỏi queue và xử lý tuần tự"""
        while True:
            # Lấy request tiếp theo từ queue
            task_func, args, future = await self.queue.get()
            try:
                # Chạy task đồng bộ (Selenium) trong ThreadPool
                loop = asyncio.get_running_loop()
                result = await loop.run_in_executor(self.executor, task_func, *args)
                # Trả kết quả về cho request API
                future.set_result(result)
            except Exception as e:
                # Trả lỗi về cho request API
                future.set_exception(e)
            finally:
                self.queue.task_done()
                # Đợi ngẫu nhiên 15-45 giây giữa các request để tránh bị Google phát hiện là Bot
                import random
                wait_time = random.randint(15, 45)
                print(f">> [QUEUE] Đã xử lý xong 1 request. Đang nghỉ ngẫu nhiên {wait_time}s trước khi nhận request tiếp theo...")
                await asyncio.sleep(wait_time)
                print(">> [QUEUE] Đã sẵn sàng cho request tiếp theo!")

    async def enqueue(self, task_func, *args):
        """Hàm dùng để đẩy request vào queue và đợi kết quả"""
        loop = asyncio.get_running_loop()
        future = loop.create_future()
        await self.queue.put((task_func, args, future))
        
        print(f">> [QUEUE] Đã đưa 1 request vào hàng đợi. Tổng số request đang chờ: {self.queue.qsize()}")
        
        # Đợi cho đến khi worker xử lý xong và trả về kết quả
        return await future

# Khởi tạo một instance toàn cục để dùng chung cho toàn bộ app
request_queue = APIRequestQueue()
