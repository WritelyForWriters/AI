from typing import Any, AsyncGenerator, Dict, Optional

from langchain.schema import BaseMessage

# 기존 에이전트 대신 LangGraph 에이전트 사용
from src.chains.research_agent_langgraph import LangGraphResearchAgent


class ResearchChain:
    _instances: Dict[str, "ResearchChain"] = {}

    @classmethod
    def get_instance(cls, session_id: Optional[str] = None) -> "ResearchChain":
        """싱글톤 인스턴스 반환"""
        if session_id:
            if session_id not in cls._instances:
                cls._instances[session_id] = cls(session_id)
            return cls._instances[session_id]

        if "default" not in cls._instances:
            cls._instances["default"] = cls()
        return cls._instances["default"]

    def __init__(self, session_id: Optional[str] = None) -> None:
        # LangGraphResearchAgent 인스턴스 생성
        self.agent = LangGraphResearchAgent.get_instance(session_id)

    def __call__(
        self, user_setting: str, query: str, user_input: str
    ) -> Dict[str, Any]:
        """동기식 호출 - LangGraphResearchAgent로 위임하여 출처 정보도 포함하여 반환"""
        result = self.agent(user_setting, query, user_input)
        # result는 이제 {"output": str, "sources": List[str]} 형태
        return result

    async def astream(
        self, user_setting: str, query: str, user_input: str
    ) -> AsyncGenerator[BaseMessage, None]:
        """비동기 스트리밍 - LangGraphResearchAgent로 위임"""
        async for chunk in self.agent.astream(user_setting, query, user_input):
            yield chunk
