import requests

url = "http://127.0.0.1:8000/generate"

prompt_text = "A futuristic cyberpunk city at night with neon lights and flying cars, high resolution, photorealistic."

payload = {
  "contents": [
    {
      "parts": [
        {
          "inline_data": {
            "mime_type": "image/png",
            "data": ""
          }
        },
        {
          "text": prompt_text
        }
      ]
    }
  ],
  "generationConfig": {
    "responseModalities": [
      "IMAGE"
    ],
    "temperature": 1.0
  }
}

print(f"--- TEST 1 ĐANG CHẠY ---")
print(f"Prompt: {prompt_text}")
print("Đang chờ phản hồi từ API (Nếu luồng này gọi thứ hai, nó sẽ tự động đợi trong Queue)...")

response = requests.post(url, json=payload)

if response.status_code == 200:
    print("\n[+] TEST 1 THÀNH CÔNG! Đã nhận được ảnh.")
    # Bạn có thể print(response.json()) nếu muốn xem chuỗi Base64
else:
    print(f"\n[-] TEST 1 LỖI: {response.text}")
