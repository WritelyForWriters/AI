from langchain_core.prompts import ChatPromptTemplate

USER_MODIFY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """```xml
            <instruction>
                <instructions>
                    1. 주어진 user-input 텍스트를 주의 깊게 읽고, user_prompt에 맞게 user-input 문장을 수정합니다.
                    2. contexts를 참고하여 스타일과 분위기가 일관되도록 유지합니다.
                    3. 문맥에 맞게 수정하고, 수정된 문장은 간결하고 자연스러워야 합니다.
                    4. 출력 결과에는 XML 태그가 포함되지 않도록 합니다.
                    5. 출력 결과에는 오직 user-input을 수정한 결과물만 포함되어야 합니다.
                </instructions>
                    <contexts>
                <context>
                  <literature-setting>
                    {user_setting}
                  </literature-setting>
                </context>
                <context>
                  <part-of-the-work>
                    {context}
                  </part-of-the-work>
                </context>
                </contexts>
            </instruction>
            ```""",
        ),
        ("human", "<user-input>{text}</user-input>"),
        ("user", "<user_prompt>{prompt}</user_prompt>"),
    ]
)
