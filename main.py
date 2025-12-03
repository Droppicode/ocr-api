from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import pytesseract
from PIL import Image
import io

app = FastAPI()

# Configuração de CORS (permite que seu Front na Vercel acesse esta API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Em produção, troque "*" pela URL do seu site
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def home():
    return {"status": "OCR Service Online"}

@app.post("/ocr")
async def read_image(file: UploadFile = File(...)):
    # 1. Lê a imagem enviada
    image_data = await file.read()
    image = Image.open(io.BytesIO(image_data))

    # 2. Configura para ler em Português
    custom_config = r'--oem 3 --psm 6 -l por'
    
    # 3. Extrai dados (texto + coordenadas)
    # image_to_data retorna um dicionário com listas de coordenadas
    data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT, config=custom_config)

    words = []
    n_boxes = len(data['text'])
    
    # 4. Formata a resposta para JSON limpo
    for i in range(n_boxes):
        # Filtra textos vazios ou confiança muito baixa (-1)
        if int(data['conf'][i]) > 0 and data['text'][i].strip() != "":
            words.append({
                "text": data['text'][i],
                "conf": data['conf'][i], # Confiança do OCR (0-100)
                "box": {
                    "left": data['left'][i],   # Posição X
                    "top": data['top'][i],     # Posição Y (importante para alinhar colunas)
                    "width": data['width'][i], # Largura
                    "height": data['height'][i]# Altura
                }
            })

    return {"result": words}