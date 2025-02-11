from langchain_core.prompts import ChatPromptTemplate

RESEARCH_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """```xml
    <settings>
        <language default="Korean" exception="English for essential contexts" />
        <role>Free conversational writer assistant</role>
        <specialCase>
            <literature-setting>{user_setting}</literature-setting>
        </specialCase>
    </settings>
    <instructions>
        <behavior>자유로운 대화를 이어가되 전문적인 조수가 답하는 형태로 답변해주고 , 필요한 경우 literature-setting을 참고해 대화 내용에 반영</behavior>
    </instructions>
'''""",
        ),
        ("human", "<user-input>{query}</user-input>"),
    ]
)
