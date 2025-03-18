from typing import Any, AsyncGenerator, Dict, Optional

from langchain.schema import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.memory.redis_memory import RedisConversationMemory
from src.prompts.chat_prompts import CHAT_PROMPT


class ChatChain:
    _instances: Dict[str, "ChatChain"] = {}

    @classmethod
    def get_instance(cls, session_id: Optional[str] = None) -> "ChatChain":
        """싱글톤 인스턴스 반환"""
        if session_id:
            if session_id not in cls._instances:
                cls._instances[session_id] = cls(session_id)
            return cls._instances[session_id]

        if "default" not in cls._instances:
            cls._instances["default"] = cls()
        return cls._instances["default"]

    def __init__(self, session_id: Optional[str] = None) -> None:
        # Gemini 2.0 Flash 모델 사용
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash",
            temperature=0.7,
            convert_system_message_to_human=True,
        )

        # Redis를 통한 대화 기록 저장
        self.memory = RedisConversationMemory(session_id) if session_id else None

        # 채팅 체인
        self.chain: Any = (
            {
                "chat_history": lambda x: self.memory.load_memory_variables({})[
                    "chat_history"
                ]
                if self.memory
                else [],
                "user_setting": lambda x: x["user_setting"],
                "query": lambda x: x["query"],
                "user_input": lambda x: x["user_input"],
            }
            | CHAT_PROMPT
            | self.llm
        )

    def __call__(
        self, user_setting: str, query: str, user_input: str
    ) -> Dict[str, Any]:
        """동기식 호출"""
        result = self.chain.invoke(
            {"user_setting": user_setting, "query": query, "user_input": user_input}
        )
        if self.memory:
            self.memory.save_context({"input": user_input}, {"output": result})
        return {"output": result}

    async def astream(
        self, user_setting: str, query: str, user_input: str
    ) -> AsyncGenerator[BaseMessage, None]:
        """비동기 스트리밍"""
        async for chunk in self.chain.astream(
            {
                "user_setting": user_setting,
                "query": query,
                "user_input": user_input,
            }
        ):
            yield chunk

        if self.memory:
            self.memory.save_context({"input": user_input}, {"output": chunk.content})
