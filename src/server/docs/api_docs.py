from typing import Any, Dict

# Auto Modify API 문서
AUTO_MODIFY_DOCS: Dict[str, Any] = {
    "summary": "자동 수정 API",
    "description": """
    입력된 텍스트에 대한 자동 수정 제안을 제공합니다.
    
    요청 파라미터:
    - tenant_id: 테넌트(작품)별 식별자
    - user_setting: 작품 설정 및 컨택스트 정보
    - query: 수정이 필요한 대상 텍스트
    """,
    "responses": {
        200: {
            "description": "성공적인 응답",
            "content": {
                "application/json": {
                    "example": {"status": "success", "result": "수정된 텍스트..."}
                }
            },
        },
        500: {
            "description": "서버 내부 오류",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to process auto modification"}
                }
            },
        },
    },
}

AUTO_MODIFY_STREAM_DOCS: Dict[str, Any] = {
    "summary": "자동 수정 스트리밍 API",
    "description": """
    입력된 텍스트에 대한 자동 수정 제안을 스트리밍 방식으로 제공합니다.
    
    요청 파라미터:
    - tenant_id: 테넌트(작품)별 식별자
    - user_setting: 작품 설정 및 컨택스트 정보
    - query: 수정이 필요한 대상 텍스트
    """,
    "responses": {
        200: {
            "description": "성공적인 스트리밍 응답",
            "content": {"text/event-stream": {"example": "수정된 텍스트...\n\n"}},
        },
        500: {
            "description": "서버 내부 오류",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to process auto modification"}
                }
            },
        },
    },
}

# Feedback API 문서
FEEDBACK_DOCS: Dict[str, Any] = {
    "summary": "구간 피드백 API",
    "description": """
    입력된 텍스트에 대한 구간 피드백을 제공합니다.
    
    요청 파라미터:
    - tenant_id: 테넌트(작품)별 식별자
    - user_setting: 작품 설정 및 컨택스트 정보
    - query: 피드백이 필요한 대상 텍스트
    """,
    "responses": {
        200: {
            "description": "성공적인 응답",
            "content": {
                "application/json": {
                    "example": {"status": "success", "result": "피드백 내용..."}
                }
            },
        },
        500: {
            "description": "서버 내부 오류",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to process feedback"}
                }
            },
        },
    },
}

FEEDBACK_STREAM_DOCS: Dict[str, Any] = {
    "summary": "구간 피드백 스트리밍 API",
    "description": """
    입력된 텍스트에 대한 구간 피드백을 스트리밍 방식으로 제공합니다.
    
    요청 파라미터:
    - tenant_id: 테넌트(작품)별 식별자
    - user_setting: 작품 설정 및 컨택스트 정보
    - query: 피드백이 필요한 대상 텍스트
    """,
    "responses": {
        200: {
            "description": "성공적인 스트리밍 응답",
            "content": {"text/event-stream": {"example": "피드백 내용...\n\n"}},
        },
        500: {
            "description": "서버 내부 오류",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to process feedback"}
                }
            },
        },
    },
}
