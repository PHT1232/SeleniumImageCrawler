import requests

url = "http://127.0.0.1:8000/generate"

# Bọc prompt trong 3 dấu nháy kép để cho phép xuống dòng
prompt_text = """
Concept: Create a vibrant 1:1 campaign key visual for VNI Culinary, presenting high-end gastronomy as an intricate art form. Show a dynamic, intense moment where a master chef is meticulously plating a modern Vietnamese fusion dish using tweezers in a luxury, dimly-lit professional kitchen.Composition & layout: Use a full-bleed editorial photograph across the entire square. Place the active culinary scene predominantly on the right and centre, while the left third carries typography directly over the image with a carefully controlled translucent dark-charcoal-to-transparent gradient fade, never a solid panel. Allow the kitchen details to continue behind the copy so the design feels immersive and intentionally art-directed.Focal point & hierarchy (what pops first): A sharply lit close-up of a silver culinary tweezer placing a delicate micro-herb onto a piece of seared Wagyu beef atop a beautifully glazed ceramic plate is the first visual hit, positioned near the lower-centre foreground. Keep this signature moment crisp and tactile, with the surrounding chef, sous-chefs and flaming stovetops softly less defined.Scene & framing (how the frame is filled): Rich modern professional kitchen, edge-to-edge, with stainless steel counters, copper pans, vibrant fresh ingredients, and subtle steam rising into the environment. A stylish Vietnamese executive chef in a crisp black uniform demonstrates extreme focus while kitchen staff work in the background.Subject/imagery: Action-led, candid gestures; intense, passionate expressions; exquisite food styling. Dramatic overhead spot lighting, realistic food textures, premium Michelin-star restaurant photography.Typography & headline: Clean bold sans-serif, stacked large headline: “Ẩm thực” on one line, “Đỉnh cao” beneath it. Highlight “Đỉnh cao” in #F59E0B (Rich Gold). Add subheadline exactly: “Nghệ thuật trình bày và chế biến món ăn chuẩn 5 sao”.Brand, colour & emphasis: Use the provided VNI Education logo exactly, unclipped and unaltered, placed in a clean upper-left area. Anchor the image with deep charcoal #1F2937 tonal shadows; use gold only for the highlighted headline and CTA, with restrained fiery orange accents.Feature highlights: Add three small, organised glyph callouts: “Nguyên liệu thượng hạng”, “Kỹ thuật điêu luyện”, “Trải nghiệm đẳng cấp”.CTA & contact (button + exact hotline/website): Include a compact gold rounded button reading exactly “Đặt bàn ngay”. Integrate a legible lower-edge contact line: “Hotline: 0823 86 5858  |  https://vni.edu.vn/”.Finishing details (shapes, depth, lighting): Subtle steam and dramatic lens flares from the stovetop flames; soft depth of field, warm highlights, refined shadows, no clutter.Quality constraints: Ultra-realistic 4K premium food photography, sharp Vietnamese diacritics, mobile-readable text, no watermark, no gibberish, no altered logo, no distorted hands or faces.BRAND LOCK (must follow):- Use the provided reference logo image exactly as-is — do not redraw, recolor, crop or distort it. Place it in the top-left corner at a readable size.- Brand colors: #1F2937, #F59E0B, #DC2626. Use them for accents, shapes and the CTA.- Vietnamese text must be spelled exactly as given, with correct diacritics. No watermark, no lorem ipsum.
"""

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

print("Đang gửi Request tới API...")
response = requests.post(url, json=payload)

print("Status Code:", response.status_code)
if response.status_code == 200:
    print("Response JSON:")
    print(response.json())
else:
    print("Error:", response.text)
