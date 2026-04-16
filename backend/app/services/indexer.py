import asyncio
import json
import logging
import re

from openai import AsyncOpenAI
from fastapi import HTTPException

from app.config import get_settings
from app.schemas import TreeNode

logger = logging.getLogger(__name__)
settings = get_settings()

client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
MODEL_NAME = "gpt-5.3-chat-latest"


def _clean_gemini_json(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


def _chunk_text(text: str, max_words: int = 1500) -> list[str]:
    words = text.split()
    chunks = []
    current_chunk = []
    current_count = 0
    
    for word in words:
        current_chunk.append(word)
        current_count += 1
        if current_count >= max_words:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_count = 0
    
    if current_chunk:
        chunks.append(" ".join(current_chunk))
    return chunks


def _build_chunk_prompt(raw_text: str, chunk_index: int, total_chunks: int) -> str:
    return (
        "You are an information architect specialized in granular indexing.\n"
        f"You are processing chunk {chunk_index + 1} of {total_chunks} of a larger document.\n"
        "Return ONLY valid JSON matching this schema:\n"
        '{ "id": str, "title": str, "summary": str, "content": str|null, "children": [TreeNode] }\n'
        "Rules:\n"
        "1) Create a detailed hierarchical structure for ONLY this chunk.\n"
        "2) Preserve specific figures, metrics, and key terms in the summaries.\n"
        "3) Use unique, slug-like IDs.\n\n"
        "Chunk Content:\n"
        f"{raw_text}"
    )


async def build_knowledge_tree(raw_text: str) -> TreeNode:
    chunks = _chunk_text(raw_text)
    sub_trees = []
    
    # Stage 1: Index each chunk independently
    for i, chunk in enumerate(chunks):
        prompt = _build_chunk_prompt(chunk, i, len(chunks))
        try:
            response = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
            if content:
                cleaned = _clean_gemini_json(content)
                parsed = json.loads(cleaned)
                sub_trees.append(TreeNode.model_validate(parsed))
        except Exception as exc:
            logger.error(f"Failed to index chunk {i}: {exc}")
            continue

    if not sub_trees:
        raise HTTPException(status_code=502, detail="Failed to index any document chunks.")

    # Stage 2: Merge into a master tree
    root = TreeNode(
        id="root",
        title="Document Overview",
        summary="A comprehensive knowledge tree built from multiple document segments.",
        content=None,
        children=sub_trees
    )
    return root
