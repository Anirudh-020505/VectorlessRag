import logging
import json
from openai import AsyncOpenAI
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()
client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY, base_url=settings.OPENAI_BASE_URL)
MODEL_NAME = "gpt-5.3-chat-latest"

async def classify_query_intent(question: str) -> str:
    """
    Classifies a user's question into 'METADATA' or 'CONTENT'.
    """
    prompt = f"""Classify the following question into 'METADATA' or 'CONTENT'.
Respond with only the word 'METADATA' or 'CONTENT'.

Examples:
- "What is the extension of this file?" -> METADATA
- "Tell me the file name" -> METADATA
- "Summarize the introduction" -> CONTENT
- "What are the main points?" -> CONTENT
- "Who wrote this doc?" -> METADATA

Question: {question}
Classification:"""

    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=5,
            temperature=0
        )
        classification = response.choices[0].message.content.strip().upper()
        if "METADATA" in classification:
            return "METADATA"
        return "CONTENT"
    except Exception as e:
        logger.error(f"Intent classification failed: {e}")
        return "CONTENT"

async def generate_metadata_answer(question: str, doc_metadata: dict) -> str:
    """
    Synthesizes a natural language answer based on provided document metadata.
    """
    prompt = f"""You are a helpful assistant. Answer the user's question about the document using the following metadata:
{json.dumps(doc_metadata, indent=2)}

Question: {question}
Answer:"""

    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=100,
            temperature=0
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"Metadata answer generation failed: {e}")
        return f"The document is named '{doc_metadata.get('name')}' with extension '{doc_metadata.get('extension')}'."
