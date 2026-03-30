import os
import tempfile
from pathlib import Path

from fastapi import UploadFile
from unstructured.partition.auto import partition


async def parse_file(file: UploadFile) -> str:
    suffix = Path(file.filename or "upload.txt").suffix or ".txt"
    temp_path: str | None = None
    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix, dir="/tmp") as tmp:
            temp_path = tmp.name
            content = await file.read()
            tmp.write(content)

        elements = partition(filename=temp_path)
        return "\n".join(
            getattr(element, "text", "").strip()
            for element in elements
            if getattr(element, "text", "").strip()
        )
    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)
