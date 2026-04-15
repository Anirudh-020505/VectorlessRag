import io
from pathlib import Path
from fastapi import UploadFile
import pypdf
import docx

async def parse_file(file: UploadFile) -> str:
    suffix = Path(file.filename or "upload.txt").suffix.lower()
    content = await file.read()
    text = ""
    
    try:
        if suffix == ".pdf":
            reader = pypdf.PdfReader(io.BytesIO(content))
            for page in reader.pages:
                extracted = page.extract_text()
                if extracted:
                    text += extracted + "\n\n"
        elif suffix in [".docx", ".doc"]:
            doc = docx.Document(io.BytesIO(content))
            for para in doc.paragraphs:
                text += para.text + "\n\n"
        else:
            # Fallback for plain text
            text = content.decode("utf-8", errors="ignore")
            
        return text.strip()
    except Exception as e:
        raise ValueError(f"Failed to parse document: {str(e)}")
