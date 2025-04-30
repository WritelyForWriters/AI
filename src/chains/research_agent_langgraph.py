import re
from enum import Enum
from typing import (
    Annotated,
    Any,
    AsyncGenerator,
    Dict,
    List,
    Optional,
    Tuple,
    TypedDict,
)

from langchain_community.chat_models import ChatPerplexity
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from src.memory.redis_memory import RedisConversationMemory
from src.prompts.research_prompts import (
    DECOMPOSE_REQUEST_PROMPT,
    FINAL_SYNTHESIS_PROMPT,
    SEARCH_PROMPT,
    STEP_QUERY_GENERATION_PROMPT,
)


# 상태 정의 업데이트
class ResearchState(TypedDict):
    """연구 에이전트의 상태를 추적하는 타입"""

    messages: Annotated[list[BaseMessage], add_messages]  # 메시지 기록
    user_setting: str  # 사용자 설정
    original_content: Optional[str]  # 원본 작품 내용
    mode: str  # 'verification' 또는 'research'
    error: Optional[str]  # 에러 정보

    # 단계적 연구를 위한 상태
    research_steps: Optional[List[str]]  # 생성된 연구 단계 목록
    current_step_index: int  # 현재 처리 중인 단계 인덱스
    step_results: List[
        Dict[str, Any]
    ]  # 각 단계별 결과 저장 [{step: str, query: str, search_result: str}]
    final_answer: Optional[str]  # 최종 생성된 답변
    temp_step_result: Optional[Dict[str, Any]]  # 임시 단계 결과 저장


class ResearchMode(str, Enum):
    """연구 모드 정의"""

    VERIFICATION = "verification"
    RESEARCH = "research"


# 언어 모델 준비
def get_models() -> (
    Tuple[ChatGoogleGenerativeAI, ChatPerplexity, ChatGoogleGenerativeAI]
):
    """필요한 언어 모델 초기화"""
    # 단계 분해, 쿼리 생성, 최종 합성에 사용할 모델 (필요에 따라 분리 가능)
    planning_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-preview-04-17",
        temperature=0.2,
        convert_system_message_to_human=True,
    )
    search_llm = ChatPerplexity(
        temperature=0,
        model="llama-3.1-sonar-small-128k-online",
        timeout=10,
    )
    synthesis_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-pro-preview-03-25",  # 최종 종합은 더 강력한 모델 사용 고려
        temperature=0.3,
        convert_system_message_to_human=True,
    )

    return planning_llm, search_llm, synthesis_llm


# --- 노드 1: 모드 감지 (기존과 동일)
def detect_mode(state: ResearchState) -> ResearchState:
    """사용자 입력과 원본 컨텐츠를 분석하여 검증 또는 연구 모드 결정"""
    messages = state["messages"]
    last_user_message = next(
        (m for m in reversed(messages) if isinstance(m, HumanMessage)), None
    )

    if not last_user_message:
        # 초기 호출 시 사용자 메시지가 없을 수 있으므로 기본값 설정 또는 에러 처리
        return {
            **state,
            "error": "사용자 메시지를 찾을 수 없습니다.",
        }  # 또는 기본 모드 설정

    user_input = last_user_message.content
    original_content = state.get("original_content", "")

    verification_keywords = [
        "고증",
        "정확",
        "확인",
        "맞",
        "틀",
        "역사적",
        "시대적",
        "사실",
        "검증",
        "평가",
        "확인",
        "오류",
        "맞는지",
        "올바른지",
    ]

    has_verification_keyword = any(
        keyword in user_input for keyword in verification_keywords
    )
    has_content_to_verify = original_content and len(original_content.strip()) > 0

    mode = (
        ResearchMode.VERIFICATION
        if (has_verification_keyword and has_content_to_verify)
        else ResearchMode.RESEARCH
    )
    mode_message = SystemMessage(content=f"현재 모드: {mode}")

    # 상태 초기화 시 step_results가 None일 수 있으므로 빈 리스트로 초기화
    return {
        **state,
        "mode": mode,
        "messages": state["messages"] + [mode_message],
        "current_step_index": 0,  # 단계 인덱스 초기화
        "step_results": [],  # 단계 결과 리스트 초기화
        "research_steps": None,  # 연구 단계 초기화
        "final_answer": None,  # 최종 답변 초기화
        "error": None,  # 에러 초기화
    }


# 노드 2: 요청 분해 (신규)
def decompose_request(state: ResearchState) -> ResearchState:
    """사용자 요청을 연구 단계로 분해"""
    if state.get("error"):
        return state

    planning_llm, _, _ = get_models()
    parser = JsonOutputParser()

    messages = state["messages"]
    last_user_message = next(
        (m for m in reversed(messages) if isinstance(m, HumanMessage)), None
    )
    user_input = last_user_message.content if last_user_message else ""
    original_content = state.get("original_content", "")
    user_setting = state.get("user_setting", "")

    # 원본 콘텐츠가 길 경우 요약 사용 (간단 예시)
    original_content_summary = (
        (original_content[:500] + "...")
        if original_content and len(original_content) > 500
        else original_content
    )

    prompt = DECOMPOSE_REQUEST_PROMPT.format(
        user_input=user_input,
        original_content_summary=original_content_summary,
        user_setting=user_setting,
    )

    try:
        result = planning_llm.invoke(prompt)
        steps = parser.parse(result.content)  # JSON 파싱

        if not isinstance(steps, list) or not all(isinstance(s, str) for s in steps):
            raise ValueError(
                "LLM이 유효한 단계 목록(문자열 리스트)을 반환하지 않았습니다."
            )

        steps_message = SystemMessage(
            content="생성된 연구 단계:\n" + "\n".join(f"- {s}" for s in steps)
        )
        return {
            **state,
            "messages": state["messages"] + [steps_message],
            "research_steps": steps,
        }
    except Exception as e:
        error_msg = f"요청 분해 오류: {str(e)}"
        error_message = SystemMessage(content=error_msg)
        return {
            **state,
            "messages": state["messages"] + [error_message],
            "error": error_msg,
        }


# 노드 3: 단계별 실행 (신규 - 쿼리 생성 + 검색 통합)
def execute_step(state: ResearchState) -> ResearchState:
    """현재 단계에 대한 쿼리 생성 및 검색 실행"""
    if state.get("error") or not state.get("research_steps"):
        return state

    planning_llm, search_llm, _ = get_models()

    current_index = state["current_step_index"]
    steps = state["research_steps"]

    # steps가 None이 아님을 타입 체커에 알림
    if steps is None:
        return state

    if current_index >= len(steps):
        # 모든 단계를 완료한 경우 (이론상 라우팅에서 걸러지지만 안전 장치)
        return state

    current_step = steps[current_index]
    step_message = SystemMessage(
        content=f"--- {current_index + 1}단계 연구 시작: {current_step} ---"
    )

    messages = state["messages"]
    last_user_message = next(
        (m for m in reversed(messages) if isinstance(m, HumanMessage)), None
    )
    user_input = last_user_message.content if last_user_message else ""
    original_content = state.get("original_content", "")
    original_content_summary = (
        (original_content[:500] + "...")
        if original_content and len(original_content) > 500
        else original_content
    )
    user_setting = state.get("user_setting", "")
    step_results = state.get("step_results", [])
    previous_results_summary = "\n".join(
        [f"- 단계 '{r['step']}': {r['search_result'][:100]}..." for r in step_results]
    )

    # 1. 현재 단계에 대한 쿼리 생성
    query_prompt = STEP_QUERY_GENERATION_PROMPT.format(
        user_input=user_input,
        original_content_summary=original_content_summary,
        user_setting=user_setting,
        all_steps=steps,
        current_step=current_step,
        previous_results_summary=previous_results_summary,
    )

    try:
        query_result = planning_llm.invoke(query_prompt)
        query = query_result.content.strip()
        query_message = SystemMessage(
            content=f"단계 {current_index + 1} 검색 쿼리: {query}"
        )

        # 2. 생성된 쿼리로 검색 수행
        search_prompt_formatted = SEARCH_PROMPT.format(
            query=query, user_input=user_input
        )  # SEARCH_PROMPT 형식에 맞게
        search_response = search_llm.invoke(search_prompt_formatted)
        search_result_content = search_response.content

        # XML 태그 등 불필요한 내용 제거 (필요시)
        search_result_content = re.sub(r"<[^>]*>", "", search_result_content).strip()
        search_message = SystemMessage(
            content=f"단계 {current_index + 1} 검색 결과:\n{search_result_content}"
        )

        # 현재 단계 결과 임시 저장 (accumulate_result 노드에서 최종 저장)
        current_step_result = {
            "step": current_step,
            "query": query,
            "search_result": search_result_content,
        }

        return {
            **state,
            # 메시지에 단계 시작, 쿼리, 검색 결과 추가
            "messages": state["messages"]
            + [step_message, query_message, search_message],
            # 임시 결과를 state에 잠시 저장 -> accumulate_result에서 처리
            "temp_step_result": current_step_result,
        }

    except Exception as e:
        error_msg = f"단계 {current_index + 1} 실행 오류: {str(e)}"
        error_message = SystemMessage(content=error_msg)
        # 오류 발생 시 해당 단계 결과는 저장하지 않고 에러 플래그 설정
        return {
            **state,
            "messages": state["messages"] + [step_message, error_message],
            "error": error_msg,
            # 오류 시 임시 결과 제거
            "temp_step_result": None,
        }


# 노드 4: 결과 누적 (신규)
def accumulate_result(state: ResearchState) -> ResearchState:
    """현재 단계의 결과를 누적하고 다음 단계로 인덱스 이동"""
    if state.get("error"):
        return state

    current_index = state["current_step_index"]
    temp_result = state.get("temp_step_result")
    updated_step_results = state.get("step_results", [])

    if temp_result:  # 오류 없이 단계가 실행되었으면 결과 추가
        # 타입 검사 통과를 위한 Dict 타입 확인
        if isinstance(temp_result, dict):
            updated_step_results.append(temp_result)

    next_index = current_index + 1

    return {
        **state,
        "current_step_index": next_index,
        "step_results": updated_step_results,
        "temp_step_result": None,  # 임시 결과 초기화
    }


# 노드 5: 최종 종합 (신규 - 기존 verify_and_synthesize, generate_final_result 대체)
def synthesize_all_steps(state: ResearchState) -> ResearchState:
    """모든 단계 결과를 종합하여 최종 답변 생성"""
    if state.get("error") and not state.get(
        "step_results"
    ):  # 에러가 있고 결과도 없으면 바로 종료
        error_msg = state.get("error", "알 수 없는 오류")
        final_message = AIMessage(
            content=f"죄송합니다. 연구 중 오류가 발생하였습니다: {error_msg}"
        )
        return {
            **state,
            "messages": state["messages"] + [final_message],
            "final_answer": final_message.content,
        }

    _, _, synthesis_llm = get_models()

    messages = state["messages"]
    last_user_message = next(
        (m for m in reversed(messages) if isinstance(m, HumanMessage)), None
    )
    user_input = last_user_message.content if last_user_message else ""
    original_content = state.get("original_content", "")
    original_content_summary = (
        (original_content[:500] + "...")
        if original_content and len(original_content) > 500
        else original_content
    )
    user_setting = state.get("user_setting", "")
    mode = state.get("mode", ResearchMode.RESEARCH)
    step_results = state.get("step_results", [])

    step_results_summary = "\n\n".join(
        [
            f"**단계 {i+1}: {res['step']}**\n"
            f"  - 검색 쿼리: {res['query']}\n"
            f"  - 검색 결과 요약: {res['search_result'][:300]}..."
            for i, res in enumerate(step_results)
        ]
    )

    # 오류가 있었지만 일부 결과가 있는 경우, 해당 정보 포함
    if state.get("error"):
        step_results_summary += (
            f"\n\n**참고:** 연구 중 오류가 발생했습니다 ({state['error']}). "
            f"일부 결과가 누락되었을 수 있습니다."
        )

    synthesis_prompt = FINAL_SYNTHESIS_PROMPT.format(
        user_input=user_input,
        original_content_summary=original_content_summary,
        user_setting=user_setting,
        mode=mode,
        step_results_summary=step_results_summary,
    )

    try:
        final_result_content = synthesis_llm.invoke(synthesis_prompt).content

        # XML 태그 등 정리
        final_result_content = re.sub(r"<\?xml.*?\?>", "", final_result_content)
        final_result_content = re.sub(r"<[^>]*>", "", final_result_content).strip()

        final_message = AIMessage(content=final_result_content)

        return {
            **state,
            "messages": state["messages"] + [final_message],
            "final_answer": final_result_content,
        }
    except Exception as e:
        error_msg = f"최종 결과 생성 오류: {str(e)}"
        # 종합 실패 시, 단계별 결과라도 보여주는 것을 고려
        fallback_content = (
            f"죄송합니다. 최종 답변 생성 중 오류가 발생했습니다 ({error_msg}).\n\n"
            f"지금까지의 연구 결과 요약:\n{step_results_summary}"
        )
        final_message = AIMessage(content=fallback_content)
        return {
            **state,
            "messages": state["messages"] + [final_message],
            "final_answer": fallback_content,
            "error": error_msg,  # 최종 단계 에러도 기록
        }


# --- 라우팅 조건 수정 ---
def should_continue(state: ResearchState) -> str:
    """다음 단계를 계속 진행할지, 아니면 최종 종합으로 갈지 결정"""
    if state.get("error"):
        # 오류 발생 시, 종합 단계로 가서 현재까지 결과라도 보고하도록 함
        # 또는 여기서 바로 END로 보낼 수도 있음 ('finish' 대신 'end_with_error' 등)
        print("오류 발생, 종합 단계로 이동")
        return "synthesize"

    research_steps = state.get("research_steps")
    current_index = state["current_step_index"]

    if not research_steps or current_index >= len(research_steps):
        # 단계가 없거나 모든 단계를 완료했으면 종합 단계로
        print("모든 단계 완료 또는 단계 없음, 종합 단계로 이동")
        return "synthesize"
    else:
        # 다음 단계 실행
        print(f"다음 단계 ({current_index + 1}/{len(research_steps)}) 실행")
        return "continue_step"


# --- LangGraph StateGraph 구성 업데이트 ---
def build_research_graph() -> StateGraph:
    """단계적 사고를 적용한 연구 그래프 빌드"""
    graph = StateGraph(ResearchState)

    # 노드 추가
    graph.add_node("detect_mode", detect_mode)
    graph.add_node("decompose_request", decompose_request)
    graph.add_node("execute_step", execute_step)
    graph.add_node("accumulate_result", accumulate_result)
    graph.add_node("synthesize_all_steps", synthesize_all_steps)

    # 시작 노드 설정
    graph.add_edge(START, "detect_mode")

    # 엣지 추가
    graph.add_edge("detect_mode", "decompose_request")
    graph.add_edge("decompose_request", "execute_step")  # 첫 단계 실행
    graph.add_edge("execute_step", "accumulate_result")

    # 조건부 엣지: 단계 반복 또는 최종 종합
    graph.add_conditional_edges(
        "accumulate_result",  # 결과 누적 후 판단
        should_continue,
        {
            "continue_step": "execute_step",  # 다음 단계 실행
            "synthesize": "synthesize_all_steps",  # 모든 단계 완료 시 종합
            # "end_with_error": END # 오류 시 즉시 종료 옵션
        },
    )

    # 종료 노드
    graph.add_edge("synthesize_all_steps", END)

    # 컴파일
    return graph.compile()


# LangGraphResearchAgent 클래스는 유지 (내부 로직은 변경된 그래프 사용)
class LangGraphResearchAgent:
    """LangGraph 기반 단계적 연구 에이전트"""

    _instances: Dict[str, "LangGraphResearchAgent"] = {}

    @classmethod
    def get_instance(cls, session_id: Optional[str] = None) -> "LangGraphResearchAgent":
        """싱글톤 인스턴스 반환"""
        if session_id:
            if session_id not in cls._instances:
                cls._instances[session_id] = cls(session_id)
            return cls._instances[session_id]

        # 기본 인스턴스 처리 개선
        default_key = "default_agent"
        if default_key not in cls._instances:
            cls._instances[default_key] = cls()
        return cls._instances[default_key]

    def __init__(self, session_id: Optional[str] = None):
        """초기화 시 그래프 빌드"""
        self.graph = build_research_graph()
        self.memory = RedisConversationMemory(session_id) if session_id else None
        self.session_id = session_id
        print(f"LangGraphResearchAgent 인스턴스 생성 (session_id: {session_id})")

    def _format_user_setting(self, user_setting: Any) -> str:
        """user_setting을 일관된 문자열 형식으로 변환"""
        if isinstance(user_setting, str):
            return user_setting
        elif isinstance(user_setting, dict):
            formatted_setting = "시대적/공간적 배경:\n"
            for category, settings in user_setting.items():
                if isinstance(settings, dict):
                    formatted_setting += f"- {category}:\n"
                    for key, value in settings.items():
                        formatted_setting += f"  - {key}: {value}\n"
                elif isinstance(settings, list):
                    formatted_setting += f"- {category}:\n"
                    for item in settings:
                        if isinstance(item, dict):
                            for k, v in item.items():
                                formatted_setting += f"  - {k}: {v}\n"
                        else:
                            formatted_setting += f"  - {item}\n"
                else:
                    formatted_setting += f"- {category}: {settings}\n"
            return formatted_setting
        else:
            # 다른 타입의 경우 문자열 변환 시도 또는 기본값 반환
            try:
                return str(user_setting)
            except Exception:
                return "사용자 설정 정보 없음"

    def __call__(
        self, user_setting: Any, original_content: str, user_input: str
    ) -> Dict[str, Any]:
        """동기식 호출"""
        formatted_user_setting = self._format_user_setting(user_setting)

        # 초기 상태 설정 (ResearchState 정의에 맞게 필드 추가/수정)
        initial_state: ResearchState = {
            "messages": [HumanMessage(content=user_input)],
            "user_setting": formatted_user_setting,
            "original_content": original_content,
            # 초기값 설정: mode는 detect_mode에서, 나머지는 아래에서 명시적으로 설정
            "mode": "",  # detect_mode에서 설정됨
            "error": None,
            "research_steps": None,
            "current_step_index": 0,
            "step_results": [],
            "final_answer": None,
            "temp_step_result": None,
            # 'search_results', 'verification_results', 'needs_more_research'는 제거됨
        }

        try:
            print(f"[{self.session_id or 'default'}] 그래프 실행 시작...")
            # Stream 대신 invoke 사용 시 최종 상태 반환
            final_state = self.graph.invoke(initial_state)
            print(f"[{self.session_id or 'default'}] 그래프 실행 완료.")

            # 최종 답변 가져오기
            output = final_state.get(
                "final_answer", "죄송합니다. 연구 결과를 생성할 수 없었습니다."
            )
            if final_state.get("error") and not output.startswith("죄송합니다"):
                output += f"\n(참고: 작업 중 오류 발생: {final_state['error']})"

            # 메모리에 저장 (선택적)
            if self.memory:
                try:
                    self.memory.save_context({"input": user_input}, {"output": output})
                    print(f"[{self.session_id or 'default'}] 메모리에 결과 저장 완료.")
                except Exception as mem_e:
                    print(f"[{self.session_id or 'default'}] 메모리 저장 실패: {mem_e}")

            return {"output": output}

        except Exception as e:
            import traceback

            error_details = (
                f"연구 에이전트 실행 오류: {str(e)}\n{traceback.format_exc()}"
            )
            print(error_details)
            # 최종 사용자에게 보여줄 에러 메시지
            error_output = f"죄송합니다. 예상치 못한 오류가 발생했습니다: {str(e)}"
            # 상태에 에러 기록 시도 (최선 노력)
            try:
                initial_state["error"] = str(e)  # 또는 더 상세한 정보
            except Exception:
                pass  # 상태 업데이트 실패 무시
            return {"output": error_output}

    async def astream(
        self, user_setting: str, original_content: str, user_input: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """비동기 스트리밍 호출 (개선된 그래프 구조 반영)"""

        formatted_user_setting = self._format_user_setting(user_setting)

        initial_state: ResearchState = {
            "messages": [HumanMessage(content=user_input)],
            "user_setting": formatted_user_setting,
            "original_content": original_content,
            "mode": "",
            "error": None,
            "research_steps": None,
            "current_step_index": 0,
            "step_results": [],
            "final_answer": None,
            "temp_step_result": None,
        }

        try:
            print(f"[{self.session_id or 'default'}] 비동기 스트리밍 시작...")
            async for event in self.graph.astream(initial_state):
                # 이벤트에서 어떤 내용을 스트리밍할지 결정
                # 예: 각 노드 실행 후 메시지나 특정 상태 값
                for node_name, node_state in event.items():
                    if node_name != "__end__":
                        # 마지막 메시지 (주로 시스템 메시지나 AI 메시지) 스트리밍
                        if (
                            node_state
                            and "messages" in node_state
                            and node_state["messages"]
                        ):
                            last_msg = node_state["messages"][-1]
                            if isinstance(last_msg, AIMessage) or (
                                isinstance(last_msg, SystemMessage)
                                and "단계" in last_msg.content
                            ):  # 예: 단계 시작 알림
                                # 어떤 노드의 메시지인지 표시
                                yield {"chunk": f"[{node_name}] {last_msg.content}\n"}
                        # 또는 최종 답변 스트리밍
                        if (
                            node_name == "synthesize_all_steps"
                            and "final_answer" in node_state
                            and node_state["final_answer"]
                        ):
                            yield {"final_answer": node_state["final_answer"]}
            print(f"[{self.session_id or 'default'}] 비동기 스트리밍 완료.")

        except Exception as e:
            import traceback

            error_details = f"스트리밍 오류: {str(e)}\n{traceback.format_exc()}"
            print(error_details)
            error_msg = (
                f"죄송합니다. 스트리밍 중 예상치 못한 오류가 발생했습니다: {str(e)}"
            )
            yield {"error": error_msg}
