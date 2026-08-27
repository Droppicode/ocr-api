# 🧾 OCR API

<p align="center">
  <img src="https://img.shields.io/badge/FastAPI-005571?style=flat&logo=fastapi" alt="FastAPI"/>
  <img src="https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white" alt="Python"/>
  <img src="https://img.shields.io/badge/Docker-2496ED?style=flat&logo=docker&logoColor=white" alt="Docker"/>
</p>

## 🧩 Part of the fin-track Ecosystem
This microservice was built to support the **[Finance Tracker](https://github.com/your-username/fin-track)** project. It is responsible for parsing bank statements (PDFs and Images) and returning structured text data to the main application.

## ✨ Features
- **Smart Extraction:** Attempts blazingly fast native text extraction using `PyMuPDF` first.
- **OCR Fallback:** Automatically falls back to `Tesseract OCR` if the PDF is scanned or if an image is uploaded.
- **Containerized:** Ready for deployment with a built-in `Dockerfile`.

## 🚀 How to Run

```bash
# Clone the repository
git clone https://github.com/your-username/ocr-api.git
cd ocr-api

# Option 1: Using Docker (Recommended)
docker build -t ocr-api .
docker run -p 8000:8000 ocr-api

# Option 2: Using Venv
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload
```
