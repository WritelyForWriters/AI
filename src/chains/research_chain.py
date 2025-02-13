from typing import Any, AsyncGenerator, Dict, Optional

from langchain.schema import BaseMessage
from langchain_community.chat_models import ChatPerplexity
from langchain_google_genai import ChatGoogleGenerativeAI

from src.memory.redis_memory import RedisConversationMemory
from src.prompts.research_prompts import (
    QUERY_GENERATION_PROMPT,
    SEARCH_PROMPT,
)


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
        # 쿼리 생성용 Gemini
        self.query_llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.3,
            convert_system_message_to_human=True,
        )

        # 검색용 Perplexity
        self.search_llm = ChatPerplexity(
            temperature=0,
            model="llama-3.1-sonar-small-128k-online",
            timeout=10,
        )

        self.memory = RedisConversationMemory(session_id) if session_id else None

        # 1. 검색 쿼리 생성 체인
        self.query_chain: Any = (
            {
                "chat_history": lambda x: self.memory.load_memory_variables({})[
                    "chat_history"
                ]
                if self.memory
                else [],
                "user_setting": lambda x: x["user_setting"],
                "query": lambda x: x["query"],
            }
            | QUERY_GENERATION_PROMPT
            | self.query_llm
        )

        # 2. 검색 체인 (최종 응답)
        self.chain: Any = (
            {
                "query": lambda x: self.query_chain.invoke(x).content,
            }
            | SEARCH_PROMPT
            | self.search_llm
        )

    def __call__(self, user_setting: str, query: str) -> Dict[str, Any]:
        """동기식 호출"""
        result = self.chain.invoke({"user_setting": user_setting, "query": query})
        if self.memory:
            self.memory.save_context({"input": query}, {"output": result})
        return {"output": result}

    async def astream(
        self, user_setting: str, query: str
    ) -> AsyncGenerator[BaseMessage, None]:
        """비동기 스트리밍"""
        async for chunk in self.chain.astream(
            {
                "user_setting": user_setting,
                "query": query,
            }
        ):
            yield chunk

        if self.memory:
            self.memory.save_context({"input": query}, {"output": chunk.content})
