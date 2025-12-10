Alcohol Label Verification App

A lightweight web application that uses FastAPI + Tesseract OCR to analyze alcohol label images and verify whether the visible text matches user-provided product information.

🚀 Features
Upload an image of an alcohol label
Extract visible text using Tesseract OCR
Validate extracted text against user inputs:
    Brand Name
    Product Type
    Alcohol Content (%)
    Net Contents
    "Government Warning" phrase
Display results as MATCH / MISMATCH
Show raw OCR output for debugging

🛠️ Tech Stack
Component	    Technology
Backend	        FastAPI (Python)
OCR Engine	    Tesseract (pytesseract wrapper)
Frontend	    Simple HTML served by FastAPI
Environment	    Python 3

📦 Installation & Setup

1️⃣ Install Tesseract OCR
Download for Windows:
https://github.com/UB-Mannheim/tesseract/wiki

Default path:
C:\Program Files\Tesseract-OCR\tesseract.exe
The application references this path directly.

2️⃣ Create virtual environment
python -m venv venv
venv\Scripts\activate

3️⃣ Install dependencies
pip install -r requirements.txt

4️⃣ Run the application
uvicorn main:app --reload


Then open in your browser:  http://127.0.0.1:8000

🧪 Usage Instructions
Enter product details (brand, type, ABV, etc.)
Upload a label image
Submit the form
Review: Per-field MATCH / MISMATCH
        Raw OCR text
        Verification summary

⚠️ Assumptions & Limitations
    OCR accuracy depends on image quality
    Matching is exact text search (not fuzzy)
    Government warning check only verifies presence of the phrase
    Alcohol % must appear in standard format (e.g., 13.5%)

📁 Project Structure    
label-verifier/
│
├── main.py              # Main FastAPI application
├── requirements.txt     # Python dependencies
├── README.md            # Project documentation
└── venv/                # Virtual environment (not needed for submission)

🔮 Future Enhancements
    Add fuzzy text matching for better tolerance
    Improve UI styling
    Add validation rules for full government warning text
    Dockerfile for easy deployment