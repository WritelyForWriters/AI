from typing import Any, Dict

# Document API 문서
DOCUMENT_DOCS: Dict[str, Any] = {
    "summary": "문서 업로드",
    "description": """
    문서를 벡터 스토어에 업로드합니다. 효율적 처리를 위해 변경된 부분만 재임베딩합니다.
    
    요청 파라미터:
    - tenant_id: 테넌트 ID
    - content: 문서 내용
    - metadata: 문서 메타데이터 (선택 사항)
    """,
    "responses": {
        200: {
            "description": "성공적으로 처리됨",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "tenant_id": "tenant123",
                        "processed": {
                            "added_chunks": 5,
                            "modified_chunks": 2,
                            "deleted_chunks": 1,
                            "total_affected": 8,
                        },
                    }
                }
            },
        },
        500: {
            "description": "내부 서버 오류",
            "content": {
                "application/json": {
                    "example": {"detail": "문서 처리 중 오류가 발생했습니다"}
                }
            },
        },
    },
}

# Document Batch API 문서
DOCUMENT_BATCH_DOCS: Dict[str, Any] = {
    "summary": "여러 문서 배치 업로드",
    "description": """
    여러 문서를 한 번에 벡터 스토어에 업로드합니다.
    
    요청 파라미터:
    - tenant_id: 테넌트 ID
    - documents: 문서 목록
      - content: 문서 내용
      - metadata: 문서 메타데이터 (선택 사항)

    """,
    "responses": {
        200: {
            "description": "성공적으로 처리됨",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "tenant_id": "tenant123",
                        "processed": {
                            "documents": 3,
                            "added_chunks": 12,
                            "modified_chunks": 5,
                            "deleted_chunks": 2,
                            "total_affected": 19,
                        },
                    }
                }
            },
        },
        500: {
            "description": "내부 서버 오류",
            "content": {
                "application/json": {
                    "example": {"detail": "문서 처리 중 오류가 발생했습니다"}
                }
            },
        },
    },
}
