from typing import Any, Dict

# Auto Modify API 문서
AUTO_MODIFY_DOCS: Dict[str, Any] = {
    "summary": "자동 수정 API",
    "description": """
    입력된 텍스트에 대한 자동 수정 제안을 제공합니다.
    
    요청 파라미터:
    - tenant_id: 테넌트(작품)별 식별자
    - user_setting: 작품 설정 및 컨텍스트 정보 (중첩 딕셔너리)
        - synopsis: {
            genre: 장르,
            length: 길이,
            purpose: 목적,
            logline: 로그라인,
            example: 예시
        }
        - worldview: {
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
            custom_field: 커스텀필드
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
                relationship: 관계
            },
            ...
        ]
        - plot: {
            exposition: 발단,
            complication: 전개,
            climax: 위기,
            resolution: 결말
        }
        - ideanote: {
            idea_title: 아이디어 제목,
            idea_content: 아이디어 내용
        }
        - custom_field: [
            {
                section_code: 섹션 코드,
                custom_field_name: 필드명,
                custom_field_content: 필드 내용
            },
            ...
        ]
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
    - user_setting: 작품 설정 및 컨텍스트 정보 (중첩 딕셔너리)
        - synopsis: {
            genre: 장르,
            length: 길이,
            purpose: 목적,
            logline: 로그라인,
            example: 예시
        }
        - worldview: {
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
            custom_field: 커스텀필드
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
                relationship: 관계
            },
            ...
        ]
        - plot: {
            exposition: 발단,
            complication: 전개,
            climax: 위기,
            resolution: 결말
        }
        - ideanote: {
            idea_title: 아이디어 제목,
            idea_content: 아이디어 내용
        }
        - custom_field: [
            {
                section_code: 섹션 코드,
                custom_field_name: 필드명,
                custom_field_content: 필드 내용
            },
            ...
        ]
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
