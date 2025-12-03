from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
from PIL import Image
from pdf2image import convert_from_bytes
import io

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Função auxiliar para não repetir código
def process_image_page(image):
    custom_config = r'--oem 3 --psm 6 -l por'
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, config=custom_config)
    
    page_words = []
    n_boxes = len(data['text'])
    
    for i in range(n_boxes):
        if int(data['conf'][i]) > 0 and data['text'][i].strip() != "":
            page_words.append({
                "text": data['text'][i],
                "conf": data['conf'][i],
                "box": {
                    "left": data['left'][i],
                    "top": data['top'][i],
                    "width": data['width'][i],
                    "height": data['height'][i]
                }
            })
    return page_words

@app.post("/ocr")
async def read_file(file: UploadFile = File(...)):
    # Lê o arquivo da memória
    file_content = await file.read()
    
    results = []

    # VERIFICAÇÃO: É PDF?
    if file.content_type == "application/pdf":
        try:
            # Converte PDF para lista de imagens (uma por página)
            # dpi=200 é um bom equilíbrio entre qualidade e velocidade
            images = convert_from_bytes(file_content, dpi=200)
            
            for index, img in enumerate(images):
                words = process_image_page(img)
                results.append({
                    "page": index + 1,
                    "words": words
                })
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao processar PDF: {str(e)}")

    # VERIFICAÇÃO: É Imagem? (JPG, PNG)
    elif file.content_type in ["image/jpeg", "image/png", "image/jpg"]:
        try:
            image = Image.open(io.BytesIO(file_content))
            words = process_image_page(image)
            results.append({
                "page": 1,
                "words": words
            })
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {str(e)}")
            
    else:
        raise HTTPException(status_code=400, detail="Arquivo não suportado. Envie PDF, JPG ou PNG.")

    return {"result": results}