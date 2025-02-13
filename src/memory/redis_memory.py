import os
from typing import Any, Dict, List

from dotenv import load_dotenv
from langchain.memory import ConversationBufferWindowMemory
from langchain.schema import BaseMessage
from langchain_community.chat_message_histories import RedisChatMessageHistory

load_dotenv()


class RedisConversationMemory(ConversationBufferWindowMemory):
    def __init__(self, session_id: str, k: int = 5, ttl: int = 3600):
        message_history = RedisChatMessageHistory(
            url=f"redis://{os.getenv("REDIS_HOST")}:{os.getenv("REDIS_PORT")}",
            session_id=session_id,
            ttl=ttl,
        )
        super().__init__(
            memory_key="chat_history",
            return_messages=True,
            chat_memory=message_history,
            k=k,
        )

    def get_messages(self) -> List[BaseMessage]:
        """저장된 메시지 목록 반환"""
        messages: List[BaseMessage] = list(self.chat_memory.messages)
        return messages

    def clear(self) -> None:
        """대화 기록 삭제"""
        self.chat_memory.clear()

    def save_context(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> None:
        """대화 컨텍스트 저장"""
        output_str = (
            outputs["output"].content
            if hasattr(outputs["output"], "content")
            else str(outputs["output"])
        )
        super().save_context(inputs, {"output": output_str})
