Alcohol Label Verification App

A FastAPI-based OCR web application that verifies key alcohol label information against a simplified TTB-style submission form.
This project extracts text from an uploaded image using Tesseract OCR, compares it to user-entered data, and returns a clear PASS/FAIL result with per-field explanations.

🔗 Live App: https://alcohol-label-verifier.onrender.com/
    This instance is deployed on Render, using a custom Dockerfile that installs Tesseract OCR in a Linux environment.

🚀 Features
    ✔ Upload an alcohol label image
        Accepts JPG/PNG files via a simple HTML form.
    ✔ Enter product information
        Brand Name
        Product Class / Type
        Alcohol Content (ABV %)
        Net Contents (Optional)
    ✔ OCR extraction with Tesseract
        Extracts text from the uploaded label using pytesseract.
    ✔ Field-by-field verification
        Checks label text against user inputs:
            Brand Name
            Product Type
            Alcohol Content
            Net Contents
            Government Warning phrase (“GOVERNMENT WARNING”)
    ✔ Clear PASS/FAIL results
        Displays:
            Overall result
            Detailed field-by-field MATCH / MISMATCH
            Raw OCR output (for debugging)

🧠 Approach & Design Decisions
    1. Simplification aligned with assignment requirements
        The real TTB form is extremely detailed, but the prompt requests a simplified version.
        I implemented only the required fields while keeping the workflow realistic.

    2. FastAPI for speed + clarity
    
        FastAPI allows:
            Quick backend development
            Clean routing
            Native support for file uploads
            Easy local testing
            Compatibility with Docker + Render
        It was the best fit for this assignment.

    3. Tesseract OCR integration
        To support cross-platform usage:
            On Windows, I explicitly point to the Tesseract executable.
            On Linux (Render), Tesseract is installed via apt-get and auto-detected.
        This makes the app portable.

    4. Matching strategy:
        Lowercasing and normalization
        Regex-based detection for ABV and numeric content
        Unit normalization (mL, ml, l, L)
        Substring matching for type and brand
        Government Warning check via string presence

🔍 How the Matching Logic Works
    Brand Name
        Case-insensitive substring search
        Ignores punctuation & extra whitespace
    
    Product Type
        Case-insensitive exact keyword match
        Designed to detect common types like “Wine”, “Beer”, “Spirits”
    
    Alcohol Content (ABV)
        Extract numeric value from form → e.g., "13.5%" → 13.5
        Regex search for patterns in OCR output:
            13.5%
            13.5 %
            ALC 13.5%
    
    Net Contents
        Normalize units:
            750 ml, 750 mL, 750 ML → 750ml
            1.5 L → 1.5l
        Compare normalized strings
    
    Government Warning
        Minimum requirement: OCR text must contain "government warning"
        Full paragraph validation is optional (future enhancement)

💻 Running the App Locally
    1️⃣ Install Python 3.10+

    2️⃣ Install Tesseract OCR
        Windows installer:
        https://github.com/UB-Mannheim/tesseract/wiki
        Default path:C:\Program Files\Tesseract-OCR\tesseract.exe
        The app auto-detects Tesseract on Windows.

    3️⃣ Clone the Repository
        git clone https://github.com/pfaisal/alcohol-label-verifier.git
        cd alcohol-label-verifier

    4️⃣ Create a Virtual Environment
        python -m venv venv
        venv\Scripts\activate

    5️⃣ Install Dependencies
        pip install -r requirements.txt

    6️⃣ Run the App
        uvicorn main:app --reload
        Then open:    http://127.0.0.1:8000

🌐 Deployment (Render)
    
    Deployment is powered by a custom Dockerfile, which:
        Installs Python
        Installs Tesseract OCR (apt-get install tesseract-ocr)
        Installs Python dependencies
        Runs the server with:
        uvicorn main:app --host 0.0.0.0 --port $PORT
        This ensures the same behavior across local and production environments.

🧪 Manual Test Cases
The following test cases ensure robust behavior:
    1. Perfect Match
        All fields match the label → PASS.
    2. Wrong Brand
        Brand name mismatch → FAIL.
    3. Wrong Product Type
        Form says “Wine”, label says “Beer” → FAIL.
    4. Incorrect Alcohol Content
        Form says 13.5%, label shows 12% → FAIL.
    5. Missing Government Warning
        Warning phrase not detected → FAIL.
    6. Partial Warning
        Label includes partial text only → FAIL.
    7. Blurry / Low-Quality OCR
        OCR cannot extract text → FAIL with graceful error.

📌 Assumptions
    Uploaded labels are in English
    OCR quality depends on image quality
    Government warning only validated via keyword presence
    Percentage symbol must appear in the OCR text for ABV
    Users provide reasonable text inputs

⚠ Known Limitations
    No fuzzy text matching (Levenshtein)
    No bounding boxes or image highlighting
    Sensitive to poor-quality images
    Not optimized for mobile UI
    Only a subset of TTB fields implemented

🔮 Future Enhancements
    Add fuzzy string matching for noisy OCR
    Validate full TTB-required government warning paragraph
    Add bounding box visualization for detected text
    Support more label fields (e.g., appellation, bottling location)
    Add frontend styling or rebuild in React
    Multi-language OCR detection