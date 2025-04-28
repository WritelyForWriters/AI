from langchain_core.prompts import ChatPromptTemplate

AUTO_MODIFY_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """```xml
<instruction>
    <instructions>
        1. 주어진 user-input 텍스트를 주의 깊게 읽고 분석합니다.
        2. **[매우 중요]** `contexts` 안의 `literature-setting` 정보를 **절대적인 기준(source of truth)**으로 삼아야 합니다. `user-input` 내용이 `literature-setting`과 **모순될 경우, 반드시 `literature-setting`에 맞춰 `user-input`을 수정**해야 합니다. (예: 설정상 청각 장애인 캐릭터가 소리를 듣는 묘사 -> 설정을 반영하여 '인기척을 느꼈다' 등으로 수정)
        3. `contexts`의 `literature-setting` 및 `part-of-the-work`(작품 일부 내용)를 참고하여, 수정된 결과물이 장면이나 작품 전체의 톤, 분위기, 맥락에 자연스럽게 어울리도록 조정합니다. 문체와 분위기의 일관성을 유지하며, 필요한 경우 단어 선택이나 문장 구조를 변경합니다.
        4. **[내용 보강]** `user-input`이 `literature-setting`과 직접 충돌하지 않더라도, `literature-setting`에 명시된 **캐릭터의 특징, 세계관 규칙, 고유 용어 등을 `user-input`에 자연스럽게 통합하여 내용을 더 풍부하고 구체적으로 만듭니다.** (예: 설정상 마법 사용 시 머리색이 변함 -> 마법 사용 장면에 '머리카락이 은빛으로 물들었다'는 묘사 추가)
        5. 수정된 결과물은 간결하고 정확해야 하며, 요청된 변경 사항(특히 설정 반영)을 완전히 반영해야 합니다.
        6. 폭력성/선정성 표현을 임의로 순화하지 말고 원작의 톤을 유지해야 합니다.
        7. 출력 결과에는 XML 태그(`<instruction>`, `<example>` 등)가 포함되지 않도록 합니다.
        8. 출력 결과에는 오직 **수정 및 보강이 완료된 최종 텍스트**만 포함되어야 합니다. 그 외의 설명이나 부연 설명은 절대 포함하지 마십시오.
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
        </example>
        <example>
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
