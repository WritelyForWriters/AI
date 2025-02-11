import os
from typing import Any, AsyncGenerator, Dict

from langchain.schema import BaseMessage
from langchain_community.chat_models import ChatPerplexity

from src.prompts.research_prompts import RESEARCH_PROMPT


class ResearchChain:
    _instances: Dict[str, "ResearchChain"] = {}

    @classmethod
    def get_instance(cls) -> "ResearchChain":
        """싱글톤 인스턴스 반환"""
        if "default" not in cls._instances:
            cls._instances["default"] = cls()
        return cls._instances["default"]

    def __init__(self) -> None:
        self.llm = ChatPerplexity(
            temperature=0,
            api_key=os.getenv("PPLX_API_KEY"),
            model="llama-3.1-sonar-small-128k-online",
            timeout=10,
        )

        self.chain = (
            {
                "user_setting": lambda x: x["user_setting"],
                "query": lambda x: x["query"],
            }
            | RESEARCH_PROMPT
            | self.llm
        )

    def __call__(self, user_setting: str, query: str) -> Dict[str, Any]:
        """동기식 호출"""
        result = self.chain.invoke({"user_setting": user_setting, "query": query})
        return {"output": result}

    async def astream(
        self, user_setting: str, query: str
    ) -> AsyncGenerator[BaseMessage, None]:
        """비동기 스트리밍"""
        params = {"user_setting": user_setting, "query": query}
        async for chunk in self.chain.astream(params):
            yield chunk
