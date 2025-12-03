FROM python:3.9-slim

# ADICIONADO: poppler-utils (obrigatório para converter PDF em imagem)
RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-por poppler-utils && \
    apt-get clean

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]