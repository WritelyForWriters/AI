from typing import Any, AsyncGenerator, Dict

import weaviate
from langchain_community.vectorstores import Weaviate
from langchain_core.messages import BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

from src.prompts.feedback_prompts import FEEDBACK_PROMPT


class FeedbackChain:
    _instances: Dict[str, "FeedbackChain"] = {}

    @classmethod
    def get_instance(
        cls,
        client: weaviate.Client,
        index_name: str,
        embeddings: GoogleGenerativeAIEmbeddings,
    ) -> "FeedbackChain":
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
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0,
            max_tokens=None,
            timeout=None,
            max_retries=2,
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
            }
            | FEEDBACK_PROMPT
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
