from langchain_core.prompts import ChatPromptTemplate

FEEDBACK_PROMPT = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """```xml
<instruction>
    <instructions>
        1.  **맥락 일관성 최우선 분석:** 주어진 `user-input` 텍스트를 주의 깊게 읽습니다. 당신의 **가장 중요한 첫 번째 임무**는 입력된 텍스트가 제공된 `contexts`(`user_setting`에 포함된 세계관, 캐릭터 상세 정보, 사용자 정의 필드, 인물 관계, 시간적 배경 등 및 이전 `context` 내용)와 일관되는지 평가하는 것입니다. 논리적 모순, 시대착오적 오류, 또는 설정된 세계관 규칙 위반(예: 캐릭터가 설정된 성격과 다르게 행동함, 존재하지 않아야 할 기술을 사용함, 세계관 내에서 알 수 없는 것을 언급함)이 있는지 찾아내십시오.
        2.  **맥락 오류 우선 수정:** 만약 설정과의 불일치가 발견되면, 문법이나 문체 수정에 앞서 **이러한 근본적인 맥락 오류를 먼저 해결**해야 합니다. `user-input` 텍스트를 주어진 설정과 논리적으로 일관되도록 수정하십시오. 핵심적인 맥락적 결함이 있는데 단순히 문법만 고쳐서는 안 됩니다.
        3. 주어진 user-input 텍스트를 주의 깊게 읽고, 어색한 표현, 문법 오류, 또는 부적절한 문장 끝맺음을 찾아냅니다.
        4. contexts를 참고하여 수정 사항이 원문의 톤, 분위기 및 맥락에 잘 맞도록 조정합니다.
        5. contexts를 참고하여 수정된 내용을 원래의 스타일과 분위기를 유지하면서 일관되게 작성합니다.
        6. 폭력/선정성을 순화하지말아야 합니다.
        7. 출력 결과에는 XML 태그를 포함하지 않도록 합니다.
        8. 최종적으로 수정된 텍스트와 수정한 이유를 한국어로 작성합니다.
        9. 출력 결과에는 오직 user-input을 수정한 텍스트와 수정한 이유만 포함되어야 합니다
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
            <example>
    <input>그는 매우 빠르게 달렸다, 그래서 그는 경주에서 이겼다.</input>
    <output>
        <result>그는 매우 빠르게 달려서 경주에서 이겼다.</result>
        <reasons>
            <reason>문장 연결에 자연스러움을 더하기 위해 쉼표 대신 접속사를 사용했습니다.</reason>
            <reason>중복된 주어를 제거해 문장을 간결하게 만들었습니다.</reason>
        </reasons>
    </output>
</example>
<example>
    <input>나는 그 영화를 보았고, 그것은 정말 재미있었다.</input>
    <output>
        <result>나는 그 영화를 보았고, 정말 재미있었다.</result>
        <reasons>
            <reason>불필요한 지시 대명사 '그것은'을 제거해 문장의 흐름을 매끄럽게 했습니다.</reason>
            <reason>문장을 간결하게 만들어 가독성을 높였습니다.</reason>
        </reasons>
    </output>
</example>
<example>
    <input>그녀는 나에게 말했다, "내일 만나요".</input>
    <output>
        <result>그녀는 나에게 "내일 만나요"라고 말했다.</result>
        <reasons>
            <reason>인용 표현의 위치를 자연스럽게 조정하고 표기법에 맞게 고쳤습니다.</reason>
            <reason>쉼표를 제거해 더 매끄러운 문장 구조를 만들었습니다.</reason>
        </reasons>
    </output>
</example>
<example>
<input>
    “애기씨, 지가 두 눈으로 똑똑히 봤당께요!” 춘삼이 소리쳤다. “끝순이 저 년이 지난 밤 애기씨 침소에 여우 새끼마냥 숨어들어가서 치마폭에 뭘 싸들고 나왔당께요!”
    춘삼의 폭로에 마당에 모인 몸종들이 웅성거렸다. 끝순은 얼굴이 시뻘게져 아무 반박도 하지 못하고 춘삼을 노려보았다.
</input>
<output>
    <result>
        “애기씨, 지가 두 눈으로 똑똑히 봤어유!” 춘삼이 의기양양한 표정으로 소리쳤다. “끝순이 저 년이 지난 밤 애기씨 침소에 여우 새끼마냥 숨어들어가서 치마폭에 뭘 싸들고 나왔당께요!”
        ‘뭐여, 끝순이가?’ ‘잘못 본 거 아니여?’
        춘삼의 폭로에 마당에 모인 몸종들이 술렁였다. 끝순은 얼굴이 순식간에 시뻘게져, 아무 반박도 하지 못하고 그녀를 노려보았다.
    </result>
    <reasons>
        <reason>‘봤당께요’를 ‘봤어유’로 변경하여 방언의 자연스러움을 높였습니다.</reason>
        <reason>몸종들의 반응 대사(‘뭐여, 끝순이가?’ ‘잘못 본 거 아니여?’)를 추가하여 상황의 긴장감과 생동감을 강화했습니다.</reason>
        <reason>‘웅성거렸다’를 ‘술렁였다’로 바꿔 감정의 밀도와 긴장감을 더 구체적으로 표현했습니다.</reason>
        <reason>‘순식간에’라는 표현을 삽입해 끝순의 감정 변화가 더 급작스럽고 강렬하게 느껴지도록 했습니다.</reason>
        <reason>불필요한 반복을 줄이고 문장을 다듬어 전체적인 가독성과 몰입도를 높였습니다.</reason>
    </reasons>
</output>

</example>
    </examples>
</instruction>
```""",
        ),
        ("human", "<user-input>{query}</user-input>"),
    ]
)
