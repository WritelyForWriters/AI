from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Weaviate
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
import weaviate
from typing import Dict
import os
from src.prompts.auto_modify_prompts import AUTO_MODIFY_PROMPT

class AutoModifyChain:
    def __init__(self, client: weaviate.Client, index_name: str, embeddings: GoogleGenerativeAIEmbeddings):
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
            by_text=False
        )
        
        retriever = self.vectorstore.as_retriever(
            search_type="similarity",
            search_kwargs={
                "k": 3,
                "alpha": 0.75,
                "where_filter": {
                    "path": ["tenant_id"],
                    "operator": "Equal",
                    "valueString": index_name.split("_")[1]
                }
            }
        )
        
        self.chain = (
            {
                "context": lambda x: retriever.invoke(x["query"]),
                "user_setting": lambda x: x["user_setting"],
                "query": lambda x: x["query"],
            }
            | AUTO_MODIFY_PROMPT
            | self.llm
            | (lambda x: {"output": x})
        )
    
    def __call__(self, user_setting: str, context: str, query: str) -> Dict:
        result = self.chain.invoke({"user_setting": user_setting, "context": context, "query": query})
        return result
