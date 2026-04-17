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


def _extract_keywords_from_text(text: str) -> list[str]:
    """
    KEYWORD_PRESERVATION: Pre-pass extraction of exact keywords before LLM summarization.
    
    Extracts:
    - All heading text (lines followed by special chars or ALL CAPS)
    - Rhetorical questions (Why/How/What questions)
    - Quoted phrases
    - Capitalized proper nouns (single & multi-word)
    - Numbers and metrics
    """
    keywords = set()
    
    # 1. RHETORICAL QUESTIONS: Extract "Why...", "How...", "What..." questions
    # These are critical for finding answers in FAQ-style documents
    # Updated: Handle leading whitespace with ^\s* instead of just ^
    question_pattern = r'^\s*((?:Why|How|What|When|Where|Which)[^?\n]*\?)'
    for match in re.finditer(question_pattern, text, re.MULTILINE | re.IGNORECASE):
        question = match.group(1).strip()
        if len(question) > 5:  # Must be at least 5 chars
            keywords.add(question)
    
    # 2. Extract lines that look like headings (followed by === or ---, or all caps)
    heading_pattern = r'^([A-Z][A-Za-z\s\?\!]+?)(?:[\n=\-]+|$)'
    for match in re.finditer(heading_pattern, text, re.MULTILINE):
        heading = match.group(1).strip()
        if heading and len(heading) > 2:
            keywords.add(heading)
    
    # 3. Extract quoted phrases
    for match in re.finditer(r'"([^"]+)"', text):
        keywords.add(match.group(1).strip())
    
    # 4. Extract capitalized phrases (2-4 words) - catches "Amazon Web Services", "Alexa", etc.
    # But avoid common words
    common_words = {'The', 'And', 'For', 'With', 'This', 'That', 'Have', 'From', 'Which', 'These', 'There'}
    for match in re.finditer(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', text):
        phrase = match.group(1).strip()
        if phrase not in common_words and len(phrase) > 2:
            keywords.add(phrase)
    
    # 5. Extract acronyms and abbreviations (2-5 capital letters)
    for match in re.finditer(r'\b([A-Z]{2,5})\b', text):
        acronym = match.group(1)
        if acronym not in {'I', 'A', 'B', 'C', 'D', 'E'}:  # Skip single letter things
            keywords.add(acronym)
    
    # 6. Extract numbers with context (dollar amounts, percentages, etc.)
    for match in re.finditer(r'(\$?[\d,]+(?:\.\d+)?%?)', text):
        keywords.add(match.group(1))
    
    logger.debug(f"Extracted {len(keywords)} keywords from chunk (including {sum(1 for kw in keywords if '?' in kw)} questions)")
    return sorted(list(keywords))


def _build_chunk_prompt(raw_text: str, chunk_index: int, total_chunks: int, extracted_keywords: list[str] = None) -> str:
    keywords_context = ""
    if extracted_keywords:
        keywords_context = f"\nREFERENCE KEYWORDS FOUND IN THIS SECTION (preserve these exactly):\n{', '.join(extracted_keywords[:50])}\n"
    
    return (
        "You are an expert Information Architect.\n"
        f"You are indexing part {chunk_index + 1} of {total_chunks} of a massive document.\n"
        "Your task is to build a high-fidelity, hierarchical Knowledge Tree for this section.\n\n"
        "CRITICAL RULES FOR KEYWORD PRESERVATION:\n"
        "1) EXACT TITLES: Use the EXACT heading text from the document as node titles. Do NOT summarize, paraphrase, or abstract titles.\n"
        "2) KEYWORD EXTRACTION: Extract all searchable keywords (company names, product names, metrics, concepts) and include them verbatim in the 'summary' field.\n"
        "3) PRESERVE RHETORICAL ELEMENTS: If a heading contains a rhetorical question (e.g., 'Why is AI Capital Expensive?'), preserve the EXACT question in the title.\n"
        "4) NUMBERS & METRICS: Ensure every financial figure, metric, percentage, and date is included verbatim in the summary.\n"
        "5) FULL CONTENT: For leaf nodes (no children), populate the 'content' field with the complete, unabridged text from that section.\n"
        "6) NO DATA LOSS: Do not aggregate sections too aggressively. If a section contains a table or list, create a specific node preserving exact labels.\n"
        "7) SEARCH OPTIMIZATION: Include in the summary field ANY text that a user might search for (proper nouns, product names, phrases).\n"
        f"{keywords_context}\n"
        "OUTPUT FORMAT: Return ONLY valid JSON matching this schema:\n"
        '{ "id": str, "title": str, "summary": str, "content": str|null, "children": [TreeNode], "keywords": [str] }\n\n'
        "Content to Index:\n"
        f"{raw_text}"
    )


async def build_knowledge_tree(raw_text: str) -> TreeNode:
    # Use structural splitting
    chunks = _chunk_text_structurally(raw_text)
    sub_trees = []
    
    # Stage 1: Index each chunk independently with keyword extraction
    for i, chunk in enumerate(chunks):
        # KEYWORD_PRESERVATION: Pre-pass extraction before LLM sees the text
        extracted_keywords = _extract_keywords_from_text(chunk)
        logger.info(f"Chunk {i}: extracted {len(extracted_keywords)} keywords")
        
        prompt = _build_chunk_prompt(chunk, i, len(chunks), extracted_keywords)
        try:
            response = await client.chat.completions.create(
                model=MODEL_NAME,
                messages=[{"role": "user", "content": prompt}]
            )
            content = response.choices[0].message.content
            if content:
                cleaned = _clean_gemini_json(content)
                parsed = json.loads(cleaned)
                
                # If LLM didn't extract keywords, use our pre-extracted ones as fallback
                if 'keywords' not in parsed or not parsed['keywords']:
                    parsed['keywords'] = extracted_keywords
                    logger.info(f"Chunk {i}: using pre-extracted keywords as fallback")
                
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
