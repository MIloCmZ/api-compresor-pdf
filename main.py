from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pypdf import PdfReader, PdfWriter
import io

app = FastAPI(
    title="Mi API de Compresión PDF Ilimitada",
    description="API gratuita para optimizar y comprimir archivos PDF sin límites."
)

@app.post("/compress")
async def compress_pdf(file: UploadFile = File(...)):
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
    return {"status": "API en funcionamiento", "docs_url": "/docs"}
