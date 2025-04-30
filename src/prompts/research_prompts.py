from langchain_core.prompts import ChatPromptTemplate, PromptTemplate

QUERY_GENERATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """```xml
<settings>
    <language>Korean</language>
    <role>Historical Research Query Generator</role>
</settings>

<context>
    <user_setting>{user_setting}</user_setting>
    <chat_history>{chat_history}</chat_history>
    <selected_text>{query}</selected_text>
</context>

<instructions>
    <task>
        <primary>역사적/시대적 정확성 검증을 위한 검색 쿼리 생성</primary>
        <requirements>
            <item>작품 내용에서 언급된 역사적 요소, 인물, 제품, 문화 현상 파악</item>
            <item>설정된 시대와 장소에 맞는지 확인할 수 있는 키워드 선택</item>
            <item>정확한 연도, 시기를 포함한 검색어 작성</item>
            <item>특정 이벤트나 문화 현상의 시기적 적합성 확인을 위한 검색어 포함</item>
            <item>검색에 효과적인 객관적 키워드 중심으로 작성</item>
            <item>불필요한 설명없이 쿼리만 반환</item>
        </requirements>
    </task>
</instructions>
```""",
        ),
        ("human", "{user_input}에 대한 검색 쿼리를 생성해주세요."),
    ]
)

SEARCH_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """```xml
<settings>
    <language>Korean</language>
    <role>Historical Accuracy Research Assistant</role>
</settings>

<context>
    <selected_text>{query}</selected_text>
</context>

<instructions>
    <task>
        <primary>문학 작품의 역사적/시대적 정확성 검증을 위한 정보 제공</primary>
        <requirements>
            <item>설정된 시대와 장소의 정확한 역사적/문화적 사실 제공</item>
            <item>언급된 인물, 제품, 문화 현상의 정확한 등장/유행 시기 조사</item>
            <item>대중문화, 음악, 예술, 제품, 브랜드의 역사적 맥락 검증</item>
            <item>특정 시대의 환경, 거리 풍경, 일상생활 모습 등에 대한 구체적 정보 제공</item>
            <item>해당 시기에 대체 가능한 적절한 요소 제안</item>
            <item>시간순으로 정리된 사건과 문화 현상에 대한 정보 제공</item>
        </requirements>
        <format>
            <structure>
                <historical_facts>시대적 사실 요약</historical_facts>
                <timeline>관련 연표 정보</timeline>
                <cultural_context>문화적 맥락 설명</cultural_context>
                <alternatives>시대적으로 적합한 대안들</alternatives>
            </structure>
        </format>
    </task>
</instructions>
```""",
        ),
        ("human", "{user_input}"),
    ]
)

# 검증 프롬프트
VERIFICATION_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """```xml
<settings>
    <language>Korean</language>
    <role>Literary Writing Assistant and Historical Accuracy Verifier</role>
</settings>

<instructions>
    <task>
        <primary>문학 작품의 시대적, 공간적 배경의 정확성 검증 및 개선 제안</primary>
        <requirements>
            <item>주어진 문장은 작가가 작성 중인 문학 작품의 일부임을 인지할 것</item>
            <item>작품 내용이 설정된 시대와 장소에 맞는지 철저히 검증</item>
            <item>부정확한 요소가 있다면 간결하고 직접적으로 지적</item>
            <item>시대적 오류가 있다면 정확한 정보와 함께 구체적인 대안 제시</item>
            <item>수정안은 전체 문장으로 제시하여 작가가 바로 사용할 수 있게 할 것</item>
            <item>교육적이지만 간결한 톤으로 피드백 제공</item>
            <item>JSON 형식으로 응답 반환 (최종 사용자에게는 JSON 형식 없이 텍스트만 표시됨)</item>
        </requirements>
    </task>
</instructions>

<output_format>
{{
  "historically_accurate": true/false,
  "explanation": "부정확한 내용에 대한 간결한 설명 (예: '서태지의 데뷔일은 1992년이에요. 1987년에는 활동하지 않았습니다.')",
  "correction_suggestion": "대체 가능한 시대 적합한 요소를 포함한 전체 문장 (예: '카페 안에서는 이문세의 '깊은 밤을 날아서'가 흘러나왔다.')",
  "needs_more_research": true/false,
  "research_questions": ["추가 조사가 필요한 경우 질문 목록"]
}}
</output_format>
```""",
        ),
        (
            "human",
            """원래 질문: {user_input}
검색 쿼리: {query}
검색 결과: {search_results}
작품 문장: {original_content}
작품 설정: 
{user_setting}

위 정보를 기반으로 작품 문장의 역사적/시대적 정확성을 평가하고, 부정확하다면 수정안을 제시해주세요.""",
        ),
    ]
)


# 일반 연구 결과 종합 프롬프트
RESEARCH_SYNTHESIS_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """```xml
<settings>
    <language>Korean</language>
    <role>Literary Research Assistant</role>
</settings>

<instructions>
    <task>
        <primary>문학 작품 창작을 위한 연구 지원</primary>
        <requirements>
            <item>사용자 질문에 대한 정확하고 유용한 정보 제공</item>
            <item>검색 결과를 바탕으로 가장 관련성 높은 정보 선별</item>
            <item>문학 작품 창작에 실질적으로 도움이 되는 인사이트 제공</item>
            <item>특정 시대, 장소, 문화적 요소에 대한 구체적 설명</item>
            <item>창작자 관점에서 실용적이고 영감을 주는 방식으로 정보 전달</item>
            <item>검색 결과에 없는 내용은 지어내지 않기</item>
        </requirements>
        <format>
            <structure>
                <summary>핵심 정보 요약</summary>
                <details>관련 세부 사항 및 구체적 예시</details>
                <creative_insights>창작에 활용할 수 있는 인사이트</creative_insights>
            </structure>
        </format>
    </task>
</instructions>
```""",
        ),
        (
            "human",
            """사용자 질문: {user_input}
검색 쿼리: {query}
검색 결과: {search_results}
작품 설정 및 맥락: 
{user_setting}

위 정보를 바탕으로 사용자 질문에 대한 유용하고 실용적인 답변을 제공해주세요.""",
        ),
    ]
)

# 요청 분해 프롬프트
DECOMPOSE_REQUEST_PROMPT = PromptTemplate.from_template(
    """사용자의 요청과 주어진 문학 작품 정보를 바탕으로, 연구 또는 검증을 위한 단계별 계획을 JSON 형식의 리스트로 작성해주세요.

사용자 요청: {user_input}
작품 내용 (요약): {original_content_summary}
사용자 설정 (시대/공간 등): {user_setting}

각 단계는 구체적인 질문이나 조사 항목이어야 합니다.

예시:
["작품의 주요 배경이 되는 18세기 프랑스 파리의 사회적 분위기는 어떠했는가?", "주인공이 사용하는 특정 도구(예: 아편)가 당시 실제로 사용되었는가?", "묘사된 복식이 시대적 고증에 맞는가?"]

단계별 계획 (JSON 리스트):"""
)

# 단계별 쿼리 생성 프롬프트
STEP_QUERY_GENERATION_PROMPT = PromptTemplate.from_template(
    """현재 연구 단계와 전체 사용자 요청, 작품 정보, 이전 단계 결과를 바탕으로 이 단계를 해결하기 위한 최적의 검색 쿼리를 1개 생성해주세요.

사용자 요청: {user_input}
작품 내용 (요약): {original_content_summary}
사용자 설정: {user_setting}
전체 연구 단계: {all_steps}
현재 연구 단계: {current_step}
이전 단계 결과 요약: {previous_results_summary}

생성할 검색 쿼리:"""
)

# 최종 결과 종합 프롬프트
FINAL_SYNTHESIS_PROMPT = PromptTemplate.from_template(
    """모든 연구 단계의 결과를 종합하여 사용자의 초기 요청에 대한 최종 답변을 작성해주세요. 답변은 {mode} 모드에 맞춰 작성되어야 합니다.

사용자 요청: {user_input}
작품 내용 (요약): {original_content_summary}
사용자 설정: {user_setting}
연구/검증 모드: {mode}

단계별 연구 결과:
{step_results_summary}

최종 답변:"""
)
