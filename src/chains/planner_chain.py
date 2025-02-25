from typing import Any, AsyncGenerator, Dict, Literal

from langchain.schema import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI

from src.prompts.planner_prompts import PLANNER_PROMPT

PlannerSection = Literal[
    "example",  # 예시문장
    # 세계관
    "geography",
    "history",
    "politics",
    "society",
    "religion",
    "economy",
    "technology",
    "lifestyle",
    "language",
    "culture",
    "species",
    "occupation",
    "conflict",
    "custom_field",
    # 등장인물
    "character",
    # 줄거리
    "exposition",
    "complication",
    "climax",
    "resolution",
]


class PlannerChain:
    _instances: Dict[str, "PlannerChain"] = {}

    @classmethod
    def get_instance(cls, tenant_id: str) -> "PlannerChain":
        """테넌트별 인스턴스 반환"""
        if tenant_id not in cls._instances:
            cls._instances[tenant_id] = cls(tenant_id)
        return cls._instances[tenant_id]

    def __init__(self, tenant_id: str) -> None:
        self.tenant_id = tenant_id

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

        self.chain: Any = (
            {
                "genre": lambda x: x["genre"],
                "logline": lambda x: x["logline"],
                "prompt": lambda x: x["prompt"],
                "section": lambda x: x["section"],
                "tenant_id": lambda x: self.tenant_id,
            }
            | PLANNER_PROMPT
            | self.llm
        )

    def __call__(
        self,
        genre: str,
        logline: str,
        prompt: str,
        section: PlannerSection,
    ) -> Dict[str, Any]:
        """동기식 호출"""
        result = self.chain.invoke(
            {
                "genre": genre,
                "logline": logline,
                "prompt": prompt,
                "section": section,
            }
        )
        return {"output": result}

    async def astream(
        self,
        genre: str,
        logline: str,
        prompt: str,
        section: PlannerSection,
    ) -> AsyncGenerator[BaseMessage, None]:
        """비동기 스트리밍"""
        async for chunk in self.chain.astream(
            {
                "genre": genre,
                "logline": logline,
                "prompt": prompt,
                "section": section,
            }
        ):
            yield chunk
