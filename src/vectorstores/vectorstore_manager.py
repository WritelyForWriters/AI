from typing import Dict, List

import weaviate
from dotenv import load_dotenv
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.chains.auto_modify_chain import AutoModifyChain

load_dotenv()


class VectorStoreManager:
    _instance = None
    _clients: Dict[str, weaviate.Client] = {}
    _chains: Dict[str, AutoModifyChain] = {}
    _embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    @classmethod
    def get_instance(cls) -> "VectorStoreManager":
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_client(self, tenant_id: str) -> weaviate.Client:
        """테넌트별 Weaviate 클라이언트를 반환하거나 생성"""
        if tenant_id not in self._clients:
            self._clients[tenant_id] = weaviate.Client(
                url="http://weaviate:8080",
                additional_headers={"X-Tenant-Id": tenant_id},
            )
            self._ensure_schema(tenant_id)
        return self._clients[tenant_id]

    def _ensure_schema(self, tenant_id: str) -> None:
        """테넌트의 스키마가 존재하는지 확인하고 없으면 생성"""
        client = self.get_client(tenant_id)
        index_name = f"Tenant_{tenant_id}"  # 대문자로 시작

        if not client.schema.exists(index_name):
            class_obj = {
                "class": index_name,
                "vectorizer": "none",
                "properties": [
                    {"name": "text", "dataType": ["text"]},
                    {"name": "tenant_id", "dataType": ["text"]},
                    {"name": "metadata", "dataType": ["text"]},
                ],
            }
            client.schema.create_class(class_obj)

    def add_documents(self, tenant_id: str, documents: List[Document]) -> None:
        """문서들을 청킹하여 테넌트의 벡터스토어에 추가"""
        client = self.get_client(tenant_id)
        index_name = f"Tenant_{tenant_id}"

        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,
            chunk_overlap=50,
            length_function=len,
            is_separator_regex=False,
        )

        batch = client.batch.configure(batch_size=50)

        with batch:
            chunks = text_splitter.split_documents(documents)
            for chunk in chunks:
                try:
                    embedding = self._embeddings.embed_query(chunk.page_content)
                    client.batch.add_data_object(
                        data_object={
                            "text": chunk.page_content,
                            "tenant_id": tenant_id,
                            "metadata": str(chunk.metadata),
                        },
                        class_name=index_name,
                        vector=embedding,
                    )
                except Exception as e:
                    print(f"Error embedding chunk: {str(e)}")
                    continue

    def initialize_tenant(self, tenant_id: str) -> None:
        """테넌트 초기화 (스키마 생성 등)"""
        pass

    def delete_tenant(self, tenant_id: str) -> None:
        """테넌트 삭제"""
        pass

    def tenant_exists(self, tenant_id: str) -> None:
        """테넌트 존재 여부 확인"""
        pass


# 전역 매니저 인스턴스
vectorstore_manager = VectorStoreManager.get_instance()
