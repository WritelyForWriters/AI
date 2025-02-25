from typing import Any, AsyncGenerator, Dict

import weaviate
from langchain.schema import BaseMessage
from langchain_community.vectorstores import Weaviate
from langchain_google_genai import (
    ChatGoogleGenerativeAI,
    GoogleGenerativeAIEmbeddings,
    HarmBlockThreshold,
    HarmCategory,
)

from src.prompts.user_modify_prompts import USER_MODIFY_PROMPT

SafetySettings = Dict[HarmCategory, HarmBlockThreshold]


class UserModifyChain:
    _instances: Dict[str, "UserModifyChain"] = {}

    @classmethod
    def get_instance(
        cls,
        client: weaviate.Client,
        index_name: str,
        embeddings: GoogleGenerativeAIEmbeddings,
    ) -> "UserModifyChain":
        tenant_id = index_name.split("_")[1]
        if tenant_id not in cls._instances:
            cls._instances[tenant_id] = cls(client, index_name, embeddings)
        return cls._instances[tenant_id]

    def __init__(
        self,
        client: weaviate.Client,
        index_name: str,
        embeddings: GoogleGenerativeAIEmbeddings,
    ) -> None:
        safety_config: SafetySettings = {
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        }

        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.7,
            max_tokens=None,
            timeout=None,
            max_retries=2,
            safety_settings=safety_config,  # type: ignore[arg-type]
        )

        self.vectorstore = Weaviate(
            client=client,
            index_name="Tenant_" + index_name.split("_")[1],
            text_key="text",
            embedding=embeddings,
            attributes=["tenant_id"],
            by_text=False,
        )

        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 3,
                "alpha": 0.75,
                "where_filter": {
                    "path": ["tenant_id"],
                    "operator": "Equal",
                    "valueString": index_name.split("_")[1],
                },
            },
        )

        self.chain: Any = (
            {
                "context": lambda x: retriever.invoke(x["query"]),
                "user_setting": lambda x: x["user_setting"],
                "query": lambda x: x["query"],
                "how_polish": lambda x: x["how_polish"],
            }
            | USER_MODIFY_PROMPT
            | self.llm
        )

    def __call__(
        self, user_setting: str, query: str, how_polish: str
    ) -> Dict[str, Any]:
        result = self.chain.invoke(
            {"user_setting": user_setting, "query": query, "how_polish": how_polish}
        )
        return {"output": result}

    async def astream(
        self, user_setting: str, query: str, how_polish: str
    ) -> AsyncGenerator[BaseMessage, None]:
        async for chunk in self.chain.astream(
            {"user_setting": user_setting, "query": query, "how_polish": how_polish}
        ):
            yield chunk
