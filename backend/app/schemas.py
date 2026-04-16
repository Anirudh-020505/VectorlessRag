from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TreeNode(BaseModel):
    id: str
    title: str
    summary: str
    content: str | None = None
    children: list["TreeNode"] = Field(default_factory=list)
    # KEYWORD_PRESERVATION: Exact keywords extracted before LLM summarization
    keywords: list[str] = Field(default_factory=list)


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    email: str
    display_name: str
    avatar_url: str | None = None


class DocumentListItem(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    created_at: datetime


class IndexDocumentResponse(BaseModel):
    document_id: str
    title: str
    message: str


class QueryRequest(BaseModel):
    document_id: str
    question: str


class QueryResponse(BaseModel):
    answer: str
    reasoning_path: list[str]
    thoughts: list[str] = Field(default_factory=list)


class JsonIndexBody(BaseModel):
    filename: str | None = None
    title: str | None = None
    content: str
