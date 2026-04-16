from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models import Document, User
from app.schemas import QueryRequest, QueryResponse, TreeNode
from app.services.agent import query_tree

router = APIRouter(tags=["query"])


@router.post("/query", response_model=QueryResponse)
async def query_document(
    payload: QueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> QueryResponse:
    result = await db.execute(
        select(Document).where(
            Document.id == payload.document_id,
            Document.user_id == current_user.id,
        )
    )
    document = result.scalar_one_or_none()
    if document is None:
        raise HTTPException(status_code=404, detail="Document not found.")

    import os
    name, ext = os.path.splitext(document.title)
    
    tree = TreeNode.model_validate(document.knowledge_tree)
    result_payload = await query_tree(
        tree=tree, 
        question=payload.question,
        doc_metadata={
            "name": name,
            "extension": ext.lower().replace(".", "")
        }
    )
    return QueryResponse(**result_payload)
