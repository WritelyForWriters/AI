from typing import Any, Dict

# Research API 문서
RESEARCH_DOCS: Dict[str, Any] = {
    "summary": "리서치 API",
    "description": """
    작품 창작을 위한 리서치 정보를 제공합니다.
    
    요청 파라미터:
    - session_id: (선택) 대화 기록을 유지하기 위한 세션 식별자
    - user_setting: 작품 설정 및 컨텍스트 정보 (중첩 딕셔너리)
        - synopsis: {
            genre: 장르,
            length: 길이,
            purpose: 목적,
            logline: 로그라인,
            example: 예시
        }
        - world_view: {
            geography: 지리,
            history: 역사,
            politics: 정치,
            society: 사회,
            religion: 종교,
            economy: 경제,
            technology: 기술,
            lifestyle: 생활,
            language: 언어,
            culture: 문화,
            species: 종족,
            occupation: 직업,
            conflict: 갈등,
            custom_fields: [
                {
                    custom_field_name: 필드명,
                    custom_field_content: 필드 내용
                },
                ...
            ]
        }
        - character: [
            {
                intro: 소개,
                character_name: 이름,
                age: 나이,
                gender: 성별,
                character_occupation: 직업,
                appearance: 외모,
                personality: 성격,
                characteristic: 특징,
                relationship: 관계,
                custom_fields: [
                    {
                        custom_field_name: 필드명,
                        custom_field_content: 필드 내용
                    },
                    ...
                ]
            },
            ...
        ]
        - plot: {
            content: 줄거리 내용
        }
        - idea_note: {
            idea_title: 아이디어 제목,
            idea_content: 아이디어 내용
        }
    - query: 선택된 구간 정보 (작품의 일부분)
    - user_input: 리서치가 필요한 주제/질문
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
    - query: 선택된 구간 정보 (작품의 일부분)
    - user_input: 리서치가 필요한 주제/질문
    - session_id: (선택) 대화 기록을 유지하기 위한 세션 식별자
    - user_setting: 작품 설정 및 컨텍스트 정보 (중첩 딕셔너리)
        - synopsis: {
            genre: 장르,
            length: 길이,
            purpose: 목적,
            logline: 로그라인,
            example: 예시
        }
        - world_view: {
            geography: 지리,
            history: 역사,
            politics: 정치,
            society: 사회,
            religion: 종교,
            economy: 경제,
            technology: 기술,
            lifestyle: 생활,
            language: 언어,
            culture: 문화,
            species: 종족,
            occupation: 직업,
            conflict: 갈등,
            custom_fields: [
                {
                    custom_field_name: 필드명,
                    custom_field_content: 필드 내용
                },
                ...
            ]
        }
        - character: [
            {
                intro: 소개,
                character_name: 이름,
                age: 나이,
                gender: 성별,
                character_occupation: 직업,
                appearance: 외모,
                personality: 성격,
                characteristic: 특징,
                relationship: 관계,
                custom_fields: [
                    {
                        custom_field_name: 필드명,
                        custom_field_content: 필드 내용
                    },
                    ...
                ]
            },
            ...
        ]
        - plot: {
            content: 줄거리 내용
        }
        - idea_note: {
            idea_title: 아이디어 제목,
            idea_content: 아이디어 내용
        }
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
