from fastapi import APIRouter, Depends, HTTPException, Request, UploadFile
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_current_user, get_db
from app.models import Document, User
from app.schemas import DocumentListItem, IndexDocumentResponse, JsonIndexBody
from app.services.indexer import build_knowledge_tree
from app.services.parser import parse_file

router = APIRouter(tags=["documents"])


@router.post("/index-document", response_model=IndexDocumentResponse)
async def index_document(
    request: Request,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> IndexDocumentResponse:
    raw_text: str | None = None
    file: UploadFile | None = None
    final_title: str | None = None
    content_type = request.headers.get("content-type", "")

    if "application/json" in content_type:
        parsed = JsonIndexBody.model_validate(await request.json())
        raw_text = parsed.content
        final_title = parsed.title or parsed.filename or "Untitled Document"
    else:
        form = await request.form()
        maybe_file = form.get("file")
        title = form.get("title")
        if isinstance(title, str):
            final_title = title
        if isinstance(maybe_file, UploadFile):
            file = maybe_file
            raw_text = await parse_file(file)
            final_title = final_title or file.filename or "Untitled Document"

    if isinstance(raw_text, str):
        raw_text = raw_text.strip()

    if not raw_text:
        raise HTTPException(
            status_code=400,
            detail="Document content is empty. Send JSON body or multipart file.",
        )

    final_title = final_title or "Untitled Document"

    tree = await build_knowledge_tree(raw_text)
    document = Document(
        title=final_title or "Untitled Document",
        raw_text=raw_text,
        knowledge_tree=tree.model_dump(mode="json"),
        user_id=current_user.id,
    )
    db.add(document)
    await db.commit()
    await db.refresh(document)

    return IndexDocumentResponse(
        document_id=document.id,
        title=document.title,
        message="Document indexed successfully",
    )


@router.get("/documents", response_model=list[DocumentListItem])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DocumentListItem]:
    result = await db.execute(
        select(Document)
        .where(Document.user_id == current_user.id)
        .order_by(Document.created_at.desc())
    )
    documents = result.scalars().all()
    return [DocumentListItem.model_validate(document) for document in documents]


@router.delete("/documents/{document_id}")
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    stmt = delete(Document).where(
        Document.id == document_id,
        Document.user_id == current_user.id,
    )
    result = await db.execute(stmt)
    await db.commit()
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Document not found.")
    return {"message": "Document deleted successfully"}
