import io
import logging
from pathlib import Path
from fastapi import UploadFile
import pypdf
import docx

logger = logging.getLogger(__name__)

async def parse_file(file: UploadFile) -> str:
    suffix = Path(file.filename or "upload.txt").suffix.lower()
    content = await file.read()
    text = ""
    logger.info("Parsing file: %s (suffix=%s, size=%d bytes)", file.filename, suffix, len(content))

    try:
        if suffix == ".pdf":
            import pdfplumber
            with pdfplumber.open(io.BytesIO(content)) as pdf:
                logger.info("PDF pages: %d", len(pdf.pages))
                for i, page in enumerate(pdf.pages):
                    extracted = page.extract_text(layout=True)
                    logger.info("Page %d extracted %d chars", i, len(extracted) if extracted else 0)
                    if extracted:
                        text += extracted + "\n\n"
            if not text.strip():
                logger.warning("pdfplumber extracted no text — PDF may be image-based or protected")
                text = f"[PDF file '{file.filename}' contains {len(pdf.pages)} pages but no extractable text.]"
        elif suffix in [".docx", ".doc"]:
            doc = docx.Document(io.BytesIO(content))
            for para in doc.paragraphs:
                text += para.text + "\n\n"
        else:
            # Fallback for plain text / md / json
            text = content.decode("utf-8", errors="ignore")

        logger.info("Final extracted text length: %d chars", len(text.strip()))
        return text.strip()
    except Exception as e:
        logger.exception("Failed to parse document: %s", e)
        raise ValueError(f"Failed to parse document: {str(e)}")
