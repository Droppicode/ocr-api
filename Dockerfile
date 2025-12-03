# Usa uma imagem Python leve
FROM python:3.9-slim

# 1. Instala o Tesseract e o pacote de idioma Português no sistema Linux
RUN apt-get update && \
    apt-get install -y tesseract-ocr tesseract-ocr-por && \
    apt-get clean

# 2. Define o diretório de trabalho
WORKDIR /app

# 3. Copia os requerimentos e instala as dependências Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 4. Copia o código da aplicação
COPY . .

# 5. Comando para rodar a API (O Render injeta a variável PORT automaticamente)
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000}"]