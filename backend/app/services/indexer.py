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


def _chunk_text_structurally(text: str, max_words: int = 2500) -> list[str]:
    # Split by double newlines to find natural section breaks
    paragraphs = re.split(r'\n\s*\n', text)
    chunks = []
    current_chunk = []
    current_count = 0
    
    for para in paragraphs:
        # Check if adding this paragraph exceeds our soft limit
        para_word_count = len(para.split())
        if current_count + para_word_count > max_words and current_chunk:
            chunks.append("\n\n".join(current_chunk))
            current_chunk = [para]
            current_count = para_word_count
        else:
            current_chunk.append(para)
            current_count += para_word_count
            
    if current_chunk:
        chunks.append("\n\n".join(current_chunk))
    return chunks


def _build_chunk_prompt(raw_text: str, chunk_index: int, total_chunks: int) -> str:
    return (
        "You are an expert Information Architect.\n"
        f"You are indexing part {chunk_index + 1} of {total_chunks} of a massive document.\n"
        "Your task is to build a high-fidelity, hierarchical Knowledge Tree for this section.\n\n"
        "RULES:\n"
        "1) IDENTIFY STRUCTURE: Look for headers and sub-headers to create a multi-level tree.\n"
        "2) PRESERVE NUMBERS: Ensure every financial figure, metric, and percentage is included in the 'summary' of its respective node.\n"
        "3) NO DATA LOSS: Do not aggregate sections too aggressively. If a section contains a table, create a specific node for it.\n"
        "4) OUTPUT FORMAT: Return ONLY valid JSON matching this schema:\n"
        '{ "id": str, "title": str, "summary": str, "content": str|null, "children": [TreeNode] }\n\n'
        "Content to Index:\n"
        f"{raw_text}"
    )


async def build_knowledge_tree(raw_text: str) -> TreeNode:
    # Use structural splitting
    chunks = _chunk_text_structurally(raw_text)
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
