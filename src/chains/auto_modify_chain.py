from typing import Any, AsyncGenerator, Dict

import weaviate
from langchain.schema import BaseMessage
from langchain_community.vectorstores import Weaviate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from src.prompts.auto_modify_prompts import AUTO_MODIFY_PROMPT


class AutoModifyChain:
    _instances: Dict[str, "AutoModifyChain"] = {}

    @classmethod
    def get_instance(
        cls,
        client: weaviate.Client,
        index_name: str,
        embeddings: GoogleGenerativeAIEmbeddings,
    ) -> "AutoModifyChain":
        tenant_id = index_name.split("_", 1)[1] if "_" in index_name else index_name

        if tenant_id not in cls._instances:
            cls._instances[tenant_id] = cls(client, index_name, embeddings)
        return cls._instances[tenant_id]

    def __init__(
        self,
        client: weaviate.Client,
        index_name: str,
        embeddings: GoogleGenerativeAIEmbeddings,
    ) -> None:
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
        )

        tenant_id = index_name.split("_", 1)[1] if "_" in index_name else index_name

        self.vectorstore = Weaviate(
            client=client,
            index_name=index_name,
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
                    "valueString": tenant_id,
                },
            },
        )

        self.chain: Any = (
            {
                "context": lambda x: retriever.invoke(x["query"]),
                "user_setting": lambda x: x["user_setting"],
                "query": lambda x: x["query"],
            }
            | AUTO_MODIFY_PROMPT
            | self.llm
        )

    def __call__(self, user_setting: str, query: str) -> Dict[str, Any]:
        result = self.chain.invoke({"user_setting": user_setting, "query": query})
        return {"output": result}

    async def astream(
        self, user_setting: str, query: str
    ) -> AsyncGenerator[BaseMessage, None]:
        async for chunk in self.chain.astream(
            {"user_setting": user_setting, "query": query}
        ):
            yield chunk
