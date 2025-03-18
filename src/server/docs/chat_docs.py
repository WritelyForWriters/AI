from typing import Any, Dict

# 채팅 API
CHAT_DOCS: Dict[str, Any] = {
    "summary": "일반 채팅 API",
    "description": """
    사용자의 질문에 대답하는 일반 채팅 API입니다.
    
    요청 파라미터:
    - user_setting: 사용자 설정 정보를 포함하는 객체
    - query: 선택된 구간 정보 (작품의 일부분)
    - user_input: 사용자의 질문 또는 요청 텍스트
    - session_id (optional): 대화를 연속적으로 유지하기 위한 세션 식별자
    """,
    "responses": {
        200: {
            "description": "성공적인 응답",
            "content": {
                "application/json": {
                    "example": {
                        "status": "success",
                        "result": "안녕하세요! 무엇을 도와드릴까요?",
                    }
                }
            },
        },
        500: {
            "description": "서버 오류",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to process chat query"}
                }
            },
        },
    },
}

# 채팅 스트리밍 API
CHAT_STREAM_DOCS: Dict[str, Any] = {
    "summary": "일반 채팅 스트리밍 API",
    "description": """
    사용자의 질문에 대한 응답을 스트리밍으로 제공하는 일반 채팅 API입니다.
    
    요청 파라미터:
    - user_setting: 사용자 설정 정보를 포함하는 객체
    - query: 선택된 구간 정보 (작품의 일부분)
    - user_input: 사용자의 질문 또는 요청 텍스트
    - session_id (optional): 대화를 연속적으로 유지하기 위한 세션 식별자

    """,
    "responses": {
        200: {
            "description": "성공적인 스트리밍 응답",
            "content": {"text/event-stream": {}},
        },
        500: {
            "description": "서버 오류",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to process streaming chat query"}
                }
            },
        },
    },
}
