from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import os

from app.dependencies import get_current_user, get_db
from app.models import Document, User
from app.schemas import QueryRequest, QueryResponse, TreeNode
from app.services.agent import query_tree
from app.services.classifier import classify_query_intent, generate_metadata_answer

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def query_document(
    payload: QueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QueryResponse:
    # 1. Fetch Document from DB
    result = await db.execute(
        select(Document).where(
            Document.id == payload.document_id,
            Document.user_id == current_user.id,
        )
    )
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    # 2. Extract Metadata
    name, ext = os.path.splitext(document.title)
    doc_meta = {
        "name": name,
        "extension": ext.lower().replace(".", ""),
        "uploaded_at": document.created_at.isoformat(),
    }

    # 3. Classify Intent (Metadata vs Content)
    intent = await classify_query_intent(payload.question)
    
    # 4. Route based on Intent
    if intent == "METADATA":
        answer = await generate_metadata_answer(payload.question, doc_meta)
        return QueryResponse(
            answer=answer,
            reasoning_path=["Metadata Router"],
            thoughts=["Question identified as metadata-related. Bypassing ReAct loop for speed/accuracy."]
        )

    # Content -> Proceed with normal Vectorless RAG pipeline (ReAct)
    tree = TreeNode.model_validate(document.knowledge_tree)
    result_payload = await query_tree(
        tree=tree, 
        question=payload.question,
        doc_metadata=doc_meta
    )
    return QueryResponse(**result_payload)
