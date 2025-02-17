from typing import Any, Dict
import weaviate
from langchain_community.vectorstores import Weaviate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings, HarmBlockThreshold, HarmCategory
from src.prompts.user_modify_prompts import USER_MODIFY_PROMPT


class UserModifyChain:
    def __init__(
        self,
        client: weaviate.Client,
        index_name: str,
        embeddings: GoogleGenerativeAIEmbeddings,
    ) -> None:

        #  LLM 객체 생성
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-1.5-pro",
            temperature=0.7,
            max_tokens=512,
            # safety settings 폭력성 완화
            safety_settings={
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            }
        )

        self.vectorstore = Weaviate(
            client=client,
            index_name="Tenant_" + index_name.split("_")[1],
            text_key="text",
            embedding=embeddings,
            attributes=["tenant_id"],
            by_text=False,
        )

        self.retriever = self.vectorstore.as_retriever(
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

        self.chain = (
            {
                "context": lambda x: self.retriever.invoke(x["text"]),
                "user_setting": lambda x: x["user_setting"],
                "prompt": lambda x: x["prompt"],
                "text": lambda x: x["text"],
            }
            | USER_MODIFY_PROMPT
            | self.llm
            | (lambda x: {"modified_text": x})
        )

    def __call__(self, user_setting: str, text: str, prompt: str) -> Dict[str, Any]:
        print("__call__ 호출")
        # text : origin 소설, prompt: 사용자 입력
        result = self.chain.invoke(
            {"user_setting": user_setting, "text": text, "prompt": prompt}
        )
        return {"status": "success", "modified_text": result.get("modified_text", "")}
