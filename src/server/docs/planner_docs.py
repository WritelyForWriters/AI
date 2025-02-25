from typing import Any, Dict

PLANNER_DOCS: Dict[str, Any] = {
    "summary": "소설 기획 생성 API",
    "description": """
    장르와 로그라인을 기반으로 소설의 세부 기획 내용을 생성합니다.
    
    요청 파라미터:
    - genre: 소설의 장르
    - logline: 소설의 핵심 줄거리
    - prompt: 생성에 대한 추가 지시사항
    - section: 생성할 섹션 (예시문장/세계관/줄거리 등)
    - tenant_id: 작품 식별자
    
    생성 가능한 섹션:
    - example: 예시문장
    - geography, history, politics, society, religion:세계관(지리/역사/정치/사회/종교)
    - economy, technology, lifestyle, language, culture:세계관(경제/기술/생활/언어/문화)
    - species, occupation, conflict, custom_field:세계관(종족/직업/갈등/커스텀필드)
    - introduction, development, crisis, conclusion:줄거리(발단/전개/위기/결말)
    """,
    "responses": {
        200: {
            "description": "성공적인 응답",
            "content": {
                "application/json": {
                    "example": {"status": "success", "result": "생성된 내용..."}
                }
            },
        },
        500: {
            "description": "서버 내부 오류",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to generate planner content"}
                }
            },
        },
    },
}

PLANNER_STREAM_DOCS: Dict[str, Any] = {
    "summary": "소설 기획 생성 스트리밍 API",
    "description": """
    장르와 로그라인을 기반으로 소설의 세부 기획 내용을 스트리밍 방식으로 생성합니다.
    
    요청 파라미터:
    - genre: 소설의 장르
    - logline: 소설의 핵심 줄거리
    - prompt: 생성에 대한 추가 지시사항
    - section: 생성할 섹션 (예시문장/세계관/줄거리 등)
    - tenant_id: 작품 식별자
    """,
    "responses": {
        200: {
            "description": "성공적인 스트리밍 응답",
            "content": {"text/event-stream": {"example": "생성된 내용...\n\n"}},
        },
        500: {
            "description": "서버 내부 오류",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to generate planner content"}
                }
            },
        },
    },
}
