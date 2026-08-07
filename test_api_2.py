import requests

url = "https://instructions-specifically-unlikely-shuttle.trycloudflare.com/generate"

prompt_text = "A peaceful Zen garden with a small pond, koi fish, and blooming cherry blossoms in spring, highly detailed."

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

print(f"--- TEST 2 ĐANG CHẠY ---")
print(f"Prompt: {prompt_text}")
print("Đang chờ phản hồi từ API (Nếu luồng này gọi thứ hai, nó sẽ tự động đợi trong Queue)...")

response = requests.post(url, json=payload)

if response.status_code == 200:
    print("\n[+] TEST 2 THÀNH CÔNG! Đã nhận được ảnh.")
    import json
    res_json = response.json()
    # Cắt bớt chuỗi Base64 dài để tránh làm trôi Terminal
    try:
        b64 = res_json["candidates"][0]["content"]["parts"][0]["inlineData"]["data"]
        res_json["candidates"][0]["content"]["parts"][0]["inlineData"]["data"] = b64[:50] + "... [BASE64 ĐÃ BỊ CẮT BỚT KHI IN RA]"
    except:
        pass
    print(json.dumps(res_json, indent=2, ensure_ascii=False))
else:
    print(f"\n[-] TEST 2 LỖI: {response.text}")
