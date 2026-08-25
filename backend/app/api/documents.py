import os
import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.api.auth import get_current_user
from app.models.user import User
from app.models.document import Document, DocumentChunk
from app.schemas.document import DocumentResponse, DocumentChunkResponse
from app.ai.rag.parser import extract_text_from_file
from app.ai.rag.chunker import chunk_extracted_pages
from app.ai.embeddings.client import embedding_client

router = APIRouter()

UPLOAD_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../data/raw"))
os.makedirs(UPLOAD_DIR, exist_ok=True)


@router.post("/documents/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED, tags=["Document Ingestion"])
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Ingestion Pipeline Endpoint:
    1. Saves uploaded PDF/DOCX/TXT file to local disk (data/raw/).
    2. Extracts page text and metadata.
    3. Slices text into overlapping chunks.
    4. Computes 384-dimensional FastEmbed vector embeddings locally ($0 Cost!).
    5. Stores document and chunk records in PostgreSQL.
    """
    original_filename = file.filename or "uploaded_file.txt"
    ext = os.path.splitext(original_filename)[1].lower()

    if ext not in [".pdf", ".docx", ".txt", ".csv"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file type '{ext}'. Supported formats: .pdf, .docx, .txt, .csv"
        )

    # Unique file storage path
    unique_filename = f"{uuid.uuid4().hex}_{original_filename}"
    file_path = os.path.join(UPLOAD_DIR, unique_filename)

    # Read and save file content
    contents = await file.read()
    file_size = len(contents)

    with open(file_path, "wb") as f:
        f.write(contents)

    try:
        # Step 1: Text extraction
        pages = extract_text_from_file(file_path, original_filename)
        if not pages:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from document. File may be empty or unreadable."
            )

        # Step 2: Text Chunking
        chunks_data = chunk_extracted_pages(pages, chunk_size=500, chunk_overlap=50)

        # Step 3: Local Vector Embedding Generation
        chunk_texts = [c["text"] for c in chunks_data]
        embeddings = embedding_client.generate_embeddings(chunk_texts)

        # Step 4: Create Document Database Record
        doc_record = Document(
            filename=unique_filename,
            original_name=original_filename,
            file_type=ext,
            file_size=file_size,
            storage_path=file_path,
            owner_id=current_user.id
        )
        db.add(doc_record)
        await db.commit()
        await db.refresh(doc_record)

        # Step 5: Save Document Chunks & Vector Embeddings
        chunk_objects = []
        for idx, chunk_info in enumerate(chunks_data):
            vec = embeddings[idx] if idx < len(embeddings) else []
            chunk_obj = DocumentChunk(
                document_id=doc_record.id,
                chunk_index=chunk_info["chunk_index"],
                page_number=chunk_info["page_number"],
                content=chunk_info["text"],
                metadata_json={"source": original_filename, "page": chunk_info["page_number"]},
                embedding=vec
            )
            chunk_objects.append(chunk_obj)

        db.add_all(chunk_objects)
        await db.commit()

        return DocumentResponse(
            id=doc_record.id,
            filename=doc_record.filename,
            original_name=doc_record.original_name,
            file_type=doc_record.file_type,
            file_size=doc_record.file_size,
            owner_id=doc_record.owner_id,
            uploaded_at=doc_record.uploaded_at,
            total_chunks=len(chunk_objects)
        )

    except Exception as e:
        # Cleanup uploaded file if parsing fails
        if os.path.exists(file_path):
            os.remove(file_path)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Document Ingestion Failed: {str(e)}"
        )


@router.get("/documents", response_model=List[DocumentResponse], tags=["Document Ingestion"])
async def list_documents(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all uploaded documents belonging to the authenticated user.
    """
    result = await db.execute(
        select(Document).where(Document.owner_id == current_user.id).order_by(Document.uploaded_at.desc())
    )
    documents = result.scalars().all()

    response = []
    for doc in documents:
        # Count chunks per document
        count_res = await db.execute(
            select(func.count(DocumentChunk.id)).where(DocumentChunk.document_id == doc.id)
        )
        total_chunks = count_res.scalar() or 0

        response.append(DocumentResponse(
            id=doc.id,
            filename=doc.filename,
            original_name=doc.original_name,
            file_type=doc.file_type,
            file_size=doc.file_size,
            owner_id=doc.owner_id,
            uploaded_at=doc.uploaded_at,
            total_chunks=total_chunks
        ))

    return response
