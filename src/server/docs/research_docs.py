from typing import Any, Dict

# Research API 문서
RESEARCH_DOCS: Dict[str, Any] = {
    "summary": "리서치 API",
    "description": """
    작품 창작을 위한 리서치 정보를 제공합니다.
    
    요청 파라미터:
    - user_setting: 작품 설정 및 컨텍스트 정보
    - query: 리서치가 필요한 주제/질문
    - session_id: (선택) 대화 기록을 유지하기 위한 세션 식별자
    """,
    "responses": {
        200: {
            "description": "성공적인 응답",
            "content": {
                "application/json": {
                    "example": {"status": "success", "result": "리서치 결과..."}
                }
            },
        },
        500: {
            "description": "서버 내부 오류",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to process research query"}
                }
            },
        },
    },
}

RESEARCH_STREAM_DOCS: Dict[str, Any] = {
    "summary": "리서치 스트리밍 API",
    "description": """
    작품 창작을 위한 리서치 정보를 스트리밍 방식으로 제공합니다.
    
    요청 파라미터:
    - user_setting: 작품 설정 및 컨텍스트 정보
    - query: 리서치가 필요한 주제/질문
    - session_id: (선택) 대화 기록을 유지하기 위한 세션 식별자
    """,
    "responses": {
        200: {
            "description": "성공적인 스트리밍 응답",
            "content": {"text/event-stream": {"example": "리서치 결과...\n\n"}},
        },
        500: {
            "description": "서버 내부 오류",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to process research query"}
                }
            },
        },
    },
}
