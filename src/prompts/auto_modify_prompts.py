from langchain_core.prompts import ChatPromptTemplate

AUTO_MODIFY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """```xml
<instruction>
    <instructions>
        1. 주어진 user-input 텍스트를 주의 깊게 읽고, 어색한 표현, 문법 오류, 또는 문장의 마무리를 수정합니다.
        2. contexts를 참고하여  수정된 내용이 장면이나 작품의 톤, 분위기, 맥락에 잘 맞도록 조정합니다.
        3. contexts를 참고하여 스타일과 분위기가 일관되도록 유지하며, 필요한 경우 단어 선택이나 문장 구조를 변경합니다.
        4. 수정된 결과물은 간결하고 정확해야 하며, 요청된 변경 사항을 완전히 반영해야 합니다.
        5. 폭력/선정성을 순화하지말아야 합니다.
        6. 출력 결과에는 XML 태그가 포함되지 않도록 합니다.
        7. 출력 결과에는 오직 user-input을 수정한 결과물만 포함되어야 합니다.
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
    <examples>
        <example>
            <input>그녀는 매우 아름다웠고, 모든 사람들은 그녀를 바라보았다. 그녀는 웃었다.</input>
            <output>그녀는 매우 아름다웠고, 모든 이들이 그녀를 바라보았다. 그녀는 미소 지었다.</output>
        </example>
        <example>
            <input>그는 집에 돌아갔고, 피곤했다. 그래서 그는 바로 잠에 들었다.</input>
            <output>그는 집에 돌아와 피곤함을 느꼈다. 그래서 곧바로 잠에 들었다.</output>
        </example>
        <example>
            <input>비가 내리고 있었다. 그래서 우리는 우산을 가져갔다.</input>
            <output>비가 내리고 있었다. 그래서 우리는 우산을 챙겼다.</output>
            <input>“애기씨, 지가 두 눈으로 똑똑히 봤당께요!” 춘삼이 소리쳤다. “끝순이 저 년이 지난 밤 애기씨 침소에 여우 새끼마냥 숨어들어가서 치마폭에 뭘 싸들고 나왔당께요!”
춘삼의 폭로에 마당에 모인 몸종들이 웅성거렸다. 끝순은 얼굴이 시뻘게져 아무 반박도 하지 못하고 춘삼을 노려보았다.</input>
             <output>“애기씨, 지가 두 눈으로 똑똑히 봤어유!” 춘삼이 의기양양한 표정으로 소리쳤다. “끝순이 저 년이 지난 밤 애기씨 침소에 여우 새끼마냥 숨어들어가서 치마폭에 뭘 싸들고 나왔당께요!”
‘뭐여, 끝순이가?’ ‘잘못 본 거 아니여?’
춘삼의 폭로에 마당에 모인 몸종들이 술렁였다. 끝순은 얼굴이 순식간에 시뻘게져, 아무 반박도 하지 못하고 그녀를 노려보았다.</output>
        </example>
    </examples>
</instruction>
```""",
        ),
        ("human", "<user-input>{query}</user-input>"),
    ]
)
