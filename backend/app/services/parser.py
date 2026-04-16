import io
import logging
import re
from pathlib import Path
from fastapi import UploadFile
import pypdf
import docx

logger = logging.getLogger(__name__)


def _normalize_encoding(text: str) -> str:
    """
    ENCODING FIX: Efficiently handle custom font encodings from stylized corporate PDFs.
    """
    # 1. Remove null bytes and other non-printable chars
    text = text.replace("\0", "")
    
    # 2. Fix spaced-out characters: "A l e x a" -> "Alexa"
    # Logic: Look for sequences of [single char + single space] repeated at least 3 times
    def fix_spaced_out(match):
        return match.group(0).replace(" ", "")
    
    # Matches patterns like "A l e x a " or " F r e e   C a s h "
    text = re.sub(r'(\b[A-Za-z]\s){3,}[A-Za-z]\b', fix_spaced_out, text)
    
    # 3. Normalize multiple spaces within lines but preserve structural line breaks
    normalized_lines = []
    for line in text.split('\n'):
        # Condense large gaps but keep meaningful spacing
        clean_line = re.sub(r' {2,}', '  ', line.strip())
        if clean_line:
            normalized_lines.append(clean_line)
    
    return '\n'.join(normalized_lines)


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
            else:
                # ENCODING FIX: Normalize extracted text
                raw_len = len(text)
                text = _normalize_encoding(text)
                if raw_len != len(text):
                    logger.info("Encoding normalization: %d chars -> %d chars", raw_len, len(text))
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
