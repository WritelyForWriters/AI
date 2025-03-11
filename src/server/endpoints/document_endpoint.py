from typing import Any, Dict, List

from fastapi import HTTPException, status
from pydantic.main import BaseModel

from src.vectorstores.differential_vectorstore import differential_vectorstore


class DocumentInput(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}


class DocumentUploadRequest(BaseModel):
    tenant_id: str
    content: str
    metadata: Dict[str, Any] = {}


class DocumentsUploadRequest(BaseModel):
    tenant_id: str
    documents: List[DocumentInput]


async def upload_document(request: DocumentUploadRequest) -> Dict[str, Any]:
    """
    소설과 같은 긴 문서를 효율적으로 처리하는 엔드포인트
    변경된 청크만 임베딩하여 저장

    Args:
        request: 테넌트 ID, 문서 내용 및 메타데이터를 포함한 요청

    Returns:
        Dict: 처리 결과 (변경된 청크 수 등)
    """
    try:
        result = differential_vectorstore.process_document(
            request.tenant_id,
            request.content,
            request.metadata,
        )

        return {
            "status": "success",
            "tenant_id": request.tenant_id,
            "processed": {
                "added_chunks": result["added"],
                "modified_chunks": result["modified"],
                "deleted_chunks": result["deleted"],
                "total_affected": result["added"]
                + result["modified"]
                + result["deleted"],
            },
        }
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"문서 처리 중 오류가 발생했습니다: {str(err)}",
        ) from err


async def upload_documents(request: DocumentsUploadRequest) -> Dict[str, Any]:
    """
    여러 문서를 벡터 스토어에 업로드하는 엔드포인트 로직
    (기존 기능 유지)

    Args:
        request: 테넌트 ID와 업로드할 문서들을 포함한 요청

    Returns:
        Dict: 업로드 결과 메시지
    """
    try:
        total_added = 0
        total_modified = 0
        total_deleted = 0

        for doc in request.documents:
            result = differential_vectorstore.process_document(
                request.tenant_id,
                doc.content,
                doc.metadata,
            )

            total_added += result["added"]
            total_modified += result["modified"]
            total_deleted += result["deleted"]

        return {
            "status": "success",
            "tenant_id": request.tenant_id,
            "processed": {
                "documents": len(request.documents),
                "added_chunks": total_added,
                "modified_chunks": total_modified,
                "deleted_chunks": total_deleted,
                "total_affected": total_added + total_modified + total_deleted,
            },
        }
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"문서 처리 중 오류가 발생했습니다: {str(err)}",
        ) from err
