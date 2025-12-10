from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import pytesseract
import io
import re
import unicodedata

# Tell pytesseract exactly where Tesseract is installed on your machine
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

app = FastAPI()

# Allow everything for simplicity
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- Helper functions ----------

def normalize_text(s: str) -> str:
    if not s:
        return ""
    s = unicodedata.normalize("NFKD", s)
    s = s.lower()
    # keep letters, numbers, %, dot, and spaces
    s = re.sub(r"[^a-z0-9%.\s]", " ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

def extract_number(s: str):
    if not s:
        return None
    m = re.search(r"(\d+(\.\d+)?)", s)
    return m.group(1) if m else None

def check_contains(field_label: str, form_value: str, ocr_text: str):
    form_norm = normalize_text(form_value)
    if not form_norm:
        return {
            "status": "not_provided",
            "details": f"{field_label} was not provided in the form."
        }
    if form_norm in ocr_text:
        return {
            "status": "match",
            "details": f"{field_label} '{form_value}' was found on the label."
        }
    return {
        "status": "mismatch",
            "details": f"{field_label} '{form_value}' was NOT found on the label."
    }

def check_abv(form_abv: str, ocr_text: str):
    form_num = extract_number(form_abv)
    if not form_num:
        return {
            "status": "not_provided",
            "details": "Alcohol content was not provided or not in a numeric form."
        }

    # look for patterns like "45%" or "45 %"
    pattern = rf"{form_num}\s*%"
    if re.search(pattern, ocr_text):
        return {
            "status": "match",
            "details": f"Alcohol content {form_num}% was found on the label."
        }
    return {
        "status": "mismatch",
        "details": f"Alcohol content {form_num}% was NOT found on the label."
    }

def normalize_units(s: str) -> str:
    s = normalize_text(s)
    # basic unit normalization
    s = s.replace("milliliters", "ml")
    s = s.replace("milliliter", "ml")
    s = s.replace("fl oz", "oz")
    return s

def check_net_contents(form_net: str, ocr_text: str):
    if not form_net:
        return {
            "status": "not_provided",
            "details": "Net contents not provided."
        }
    form_norm = normalize_units(form_net)
    ocr_norm = normalize_units(ocr_text)
    if form_norm and form_norm in ocr_norm:
        return {
            "status": "match",
            "details": f"Net contents '{form_net}' were found on the label."
        }
    return {
        "status": "mismatch",
        "details": f"Net contents '{form_net}' were NOT found on the label."
    }

def check_government_warning(ocr_text_raw: str):
    text = ocr_text_raw.lower()
    if "government warning" in text:
        return {
            "status": "match",
            "details": "'GOVERNMENT WARNING' phrase was found on the label."
        }
    return {
        "status": "mismatch",
        "details": "'GOVERNMENT WARNING' phrase was NOT found on the label."
    }

# ---------- Routes ----------

@app.get("/", response_class=HTMLResponse)
async def form_page():
    # This returns the HTML page with the form
    return """
    <html>
      <head>
        <title>Alcohol Label Verification</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 40px auto;
          }
          h1 {
            text-align: center;
          }
          form {
            border: 1px solid #ccc;
            padding: 20px;
            border-radius: 8px;
          }
          label {
            display: block;
            margin-top: 10px;
            font-weight: bold;
          }
          input[type="text"], input[type="file"] {
            width: 100%;
            padding: 8px;
            margin-top: 4px;
            box-sizing: border-box;
          }
          button {
            margin-top: 20px;
            padding: 10px 20px;
          }
          .result {
            margin-top: 20px;
            padding: 15px;
            border-radius: 8px;
          }
          .match {
            color: green;
          }
          .mismatch {
            color: red;
          }
          .info {
            color: #555;
          }
        </style>
      </head>
      <body>
        <h1>Alcohol Label Verification</h1>
        <p>Enter the product details and upload a label image. The app will check if the label matches.</p>
        <form action="/verify" method="post" enctype="multipart/form-data">
          <label>Brand Name</label>
          <input type="text" name="brand_name" required />

          <label>Product Class / Type</label>
          <input type="text" name="product_type" required />

          <label>Alcohol Content (e.g., 13.5%)</label>
          <input type="text" name="alcohol_content" required />

          <label>Net Contents (optional, e.g., 750 mL)</label>
          <input type="text" name="net_contents" />

          <label>Label Image</label>
          <input type="file" name="file" accept="image/*" required />

          <button type="submit">Verify Label</button>
        </form>
      </body>
    </html>
    """

@app.post("/verify", response_class=HTMLResponse)
async def verify_label(
    brand_name: str = Form(...),
    product_type: str = Form(...),
    alcohol_content: str = Form(...),
    net_contents: str = Form(""),
    file: UploadFile = File(...)
):
    # Read image
    image_bytes = await file.read()
    img = Image.open(io.BytesIO(image_bytes))

    # OCR
    ocr_raw = pytesseract.image_to_string(img)
    ocr_norm = normalize_text(ocr_raw)

    # Run checks
    checks = {}
    checks["Brand Name"] = check_contains("Brand Name", brand_name, ocr_norm)
    checks["Product Type"] = check_contains("Product Type", product_type, ocr_norm)
    checks["Alcohol Content"] = check_abv(alcohol_content, ocr_norm)
    checks["Net Contents"] = check_net_contents(net_contents, ocr_raw)
    checks["Government Warning"] = check_government_warning(ocr_raw)

    # Overall result = any mismatch = fail
    overall_match = True
    for label, result in checks.items():
        if result["status"] == "mismatch":
            overall_match = False

    # Build HTML for results
    overall_html = (
        '<div class="result match"><h2>✅ Label matches the provided data (based on detected text).</h2></div>'
        if overall_match
        else '<div class="result mismatch"><h2>❌ Label does NOT fully match the provided data.</h2></div>'
    )

    checks_html = ""
    for label, result in checks.items():
        status = result["status"]
        css_class = "info"
        if status == "match":
            css_class = "match"
        elif status == "mismatch":
            css_class = "mismatch"

        checks_html += f"""
        <p class="{css_class}">
          <strong>{label}:</strong> {status.upper()} – {result['details']}
        </p>
        """

    page = f"""
    <html>
      <head>
        <title>Verification Result</title>
        <style>
          body {{
            font-family: Arial, sans-serif;
            max-width: 800px;
            margin: 40px auto;
          }}
          .match {{ color: green; }}
          .mismatch {{ color: red; }}
          .info {{ color: #555; }}
          .result {{
            margin-bottom: 20px;
            padding: 15px;
            border-radius: 8px;
          }}
          .back-link {{
            margin-top: 20px;
            display: inline-block;
          }}
          textarea {{
            width: 100%;
            height: 150px;
            margin-top: 10px;
          }}
        </style>
      </head>
      <body>
        {overall_html}
        <h2>Detailed Checks</h2>
        {checks_html}
        <h3>OCR Text (for debugging)</h3>
        <textarea readonly>{ocr_raw}</textarea>
        <br/>
        <a href="/" class="back-link">🔙 Go back</a>
      </body>
    </html>
    """
    return HTMLResponse(content=page)
