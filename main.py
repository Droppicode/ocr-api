from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import io
import fitz  # PyMuPDF

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Função OCR (Lenta, usada como Fallback) ---
def process_image_with_ocr(image):
    custom_config = r'--oem 3 --psm 6 -l por'
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, config=custom_config)
    words = []
    for i in range(len(data['text'])):
        if int(data['conf'][i]) > 0 and data['text'][i].strip() != "":
            words.append({
                "text": data['text'][i],
                "conf": data['conf'][i],
                "box": {
                    "left": data['left'][i],
                    "top": data['top'][i],
                    "width": data['width'][i],
                    "height": data['height'][i]
                },
                "method": "ocr" # Para você saber que foi OCR
            })
    return words

# --- Função Nativa (Rápida, usada como Principal) ---
def process_pdf_native(page):
    words = []
    # get_text("words") retorna lista de tuplas: (x0, y0, x1, y1, "palavra", block_no, line_no, word_no)
    text_blocks = page.get_text("words")
    
    for block in text_blocks:
        x0, y0, x1, y1, text, block_no, line_no, word_no = block
        words.append({
            "text": text,
            "conf": 100, # Confiança total pois é nativo
            "box": {
                "left": x0,
                "top": y0,
                "width": x1 - x0,
                "height": y1 - y0
            },
            "method": "native" # Para você saber que foi extração direta
        })
    return words

@app.post("/process")
async def read_file(file: UploadFile = File(...)):
    file_content = await file.read()
    results = []

    if file.content_type == "application/pdf":
        try:
            # Abre o PDF com PyMuPDF
            doc = fitz.open(stream=file_content, filetype="pdf")
            
            for i, page in enumerate(doc):
                # 1. Tenta extração Nativa (Rápida)
                page_words = process_pdf_native(page)
                
                # 2. Se a lista vier vazia, provavelmente é um PDF Escaneado (Imagem)
                # Aí sim usamos o OCR (Lento)
                if not page_words:
                    print(f"Página {i+1} parece ser imagem. Usando OCR...")
                    # Converte SÓ essa página para imagem
                    images = convert_from_bytes(file_content, first_page=i+1, last_page=i+1, dpi=200)
                    if images:
                        page_words = process_image_with_ocr(images[0])
                
                results.append({
                    "page": i + 1,
                    "words": page_words
                })
                
        except Exception as e:
             raise HTTPException(status_code=500, detail=f"Erro PDF: {str(e)}")

    elif file.content_type in ["image/jpeg", "image/png", "image/jpg"]:
        # Imagens diretas sempre precisam de OCR
        image = Image.open(io.BytesIO(file_content))
        words = process_image_with_ocr(image)
        results.append({"page": 1, "words": words})
            
    else:
        raise HTTPException(status_code=400, detail="Formato inválido")

    return {"result": results}