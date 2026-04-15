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


def _strip_fences(text: str) -> str:
    cleaned = text.strip()
    cleaned = re.sub(r"^```json\s*", "", cleaned, flags=re.IGNORECASE)
    cleaned = re.sub(r"^```\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)
    return cleaned.strip()


async def _ask_leaf(content: str, question: str) -> str | None:
    prompt = (
        "Question:\n"
        f"{question}\n\n"
        "Content:\n"
        f"{content}\n\n"
        "If content answers question, return answer only.\n"
        "If not answerable, return exactly: NOT_FOUND"
    )
    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )
    answer = (response.choices[0].message.content or "").strip()
    return None if answer == "NOT_FOUND" else answer


async def _select_child_indices(node: TreeNode, question: str) -> list[int]:
    child_summaries = [
        {"index": idx, "title": child.title, "summary": child.summary}
        for idx, child in enumerate(node.children)
    ]
    prompt = (
        "Given question and child summaries, choose most relevant child indices.\n"
        "Return JSON array only, like [0,2]. No explanation.\n\n"
        f"Question:\n{question}\n\n"
        f"Children:\n{json.dumps(child_summaries, ensure_ascii=False)}"
    )
    response = await client.chat.completions.create(
        model=MODEL_NAME,
        messages=[{"role": "user", "content": prompt}]
    )
    cleaned = _strip_fences(response.choices[0].message.content or "[]")
    try:
        parsed = json.loads(cleaned)
        if not isinstance(parsed, list):
            return []
        valid = [int(i) for i in parsed if isinstance(i, int) and 0 <= i < len(node.children)]
        seen: set[int] = set()
        ordered: list[int] = []
        for index in valid:
            if index not in seen:
                seen.add(index)
                ordered.append(index)
        return ordered
    except Exception:
        return []


async def _traverse(node: TreeNode, question: str, reasoning_path: list[str]) -> str | None:
    reasoning_path.append(node.title)
    is_leaf = len(node.children) == 0 and node.content is not None
    if is_leaf:
        return await _ask_leaf(node.content or "", question)

    if not node.children:
        return None

    indices = await _select_child_indices(node, question)
    if not indices:
        indices = list(range(len(node.children)))

    for index in indices:
        answer = await _traverse(node.children[index], question, reasoning_path)
        if answer:
            return answer
    return None


async def query_tree(tree: TreeNode, question: str) -> dict:
    try:
        reasoning_path: list[str] = []
        answer = await _traverse(tree, question, reasoning_path)
        return {
            "answer": answer or "No relevant answer found in this document.",
            "reasoning_path": reasoning_path,
        }
    except Exception as exc:
        logger.exception("Tree query failed: %s", exc)
        raise HTTPException(status_code=502, detail="Failed to query document with OpenAI.") from exc
