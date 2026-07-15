from fastapi import FastAPI, UploadFile, File, HTTPException, Security, Depends
from fastapi.security.api_key import APIKeyHeader
from fastapi.responses import StreamingResponse
from pypdf import PdfReader, PdfWriter
import io
import os

# Configuración de la seguridad
API_KEY_NAME = "X-API-KEY"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=False)

# Definimos una API Key por defecto por si olvidas configurarla en Render
DEFAULT_API_KEY = "mi_clave_secreta_provisional_123"

async def get_api_key(api_key: str = Depends(api_key_header)):
    # Busca la clave en las variables de entorno de Render; si no existe, usa la por defecto
    expected_key = os.getenv("COMPRESSOR_API_KEY", DEFAULT_API_KEY)
    if not api_key or api_key != expected_key:
        raise HTTPException(status_code=403, detail="Acceso denegado: API Key inválida o ausente.")
    return api_key

app = FastAPI(
    title="Mi API de Compresión PDF Protegida",
    description="API propia para optimizar archivos PDF de forma segura."
)

@app.post("/compress")
async def compress_pdf(
    file: UploadFile = File(...), 
    api_key: str = Depends(get_api_key) # Protege esta ruta
):
    if not file.filename.endswith('.pdf'):
        raise HTTPException(status_code=400, detail="El archivo debe ser un formato PDF válido.")
    
    try:
        pdf_content = await file.read()
        reader = PdfReader(io.BytesIO(pdf_content))
        writer = PdfWriter()
        
        for page in reader.pages:
            page.compress_content_streams()
            writer.add_page(page)
            
        for page in writer.pages:
            for img in page.images:
                img.replace(img.image, quality=60)

        output_buffer = io.BytesIO()
        writer.write(output_buffer)
        output_buffer.seek(0)
        
        return StreamingResponse(
            output_buffer,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=comprimido_{file.filename}"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error al procesar el PDF: {str(e)}")

@app.get("/")
def read_root():
    return {"status": "API Segura en funcionamiento", "docs_url": "/docs"}
