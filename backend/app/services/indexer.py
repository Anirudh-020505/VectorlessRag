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


def _build_prompt(raw_text: str) -> str:
    return (
        "You are an information architect.\n"
        "Return ONLY valid JSON. No markdown. No explanation.\n"
        "Output must match exact schema:\n"
        '{ "id": str, "title": str, "summary": str, "content": str|null, "children": [TreeNode] }\n'
        "Rules:\n"
        "1) Recursively break document into logical sections.\n"
        "2) Leaf nodes must contain content. Branch nodes must set content to null.\n"
        "3) Every node id must be unique and slug-like.\n"
        "4) Keep summaries concise and useful for retrieval.\n\n"
        "Document:\n"
        f"{raw_text}"
    )


async def build_knowledge_tree(raw_text: str) -> TreeNode:
    prompt = _build_prompt(raw_text)
    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}]
        )
        content = response.choices[0].message.content
        if not content:
            raise HTTPException(status_code=502, detail="OpenAI returned empty response.")
        cleaned = _clean_gemini_json(content)
        parsed = json.loads(cleaned)
        return TreeNode.model_validate(parsed)
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Failed to build knowledge tree: %s", exc)
        raise HTTPException(
            status_code=502,
            detail="Failed to build knowledge tree from OpenAI response.",
        ) from exc
