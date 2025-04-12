import os
from typing import Any, Dict, Optional

import weaviate
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings

from src.vectorstores.chunk_manager import chunk_manager
from src.vectorstores.vectorstore_manager import vectorstore_manager

load_dotenv()


class DifferentialVectorStore:
    """
    문서 임베딩을 효율적으로 저장하고 관리하는 클래스
    변경된 청크만 임베딩하여 Weaviate에 저장
    """

    _instance = None
    _clients: Dict[str, weaviate.Client] = {}
    _embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")

    @classmethod
    def get_instance(cls) -> "DifferentialVectorStore":
        """싱글톤 인스턴스 반환"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def get_client(self, tenant_id: str) -> weaviate.Client:
        """테넌트별 Weaviate 클라이언트를 반환하거나 생성"""
        if tenant_id not in self._clients:
            weaviate_url = os.getenv("WEAVIATE_URL", "http://weaviate:8080")
            self._clients[tenant_id] = weaviate.Client(
                url=weaviate_url,
                additional_headers={"X-Tenant-Id": tenant_id},
            )
            self._ensure_schema(tenant_id)
        return self._clients[tenant_id]

    def _ensure_schema(self, tenant_id: str) -> None:
        """테넌트의 스키마가 존재하는지 확인하고 없으면 생성"""
        client = self.get_client(tenant_id)
        safe_tenant_id = vectorstore_manager._get_safe_index_name(tenant_id)
        index_name = f"Tenant_{safe_tenant_id}"

        if not client.schema.exists(index_name):
            class_obj = {
                "class": index_name,
                "vectorizer": "none",
                "properties": [
                    {"name": "text", "dataType": ["text"]},
                    {"name": "tenant_id", "dataType": ["text"]},
                    {"name": "chunk_id", "dataType": ["text"]},
                    {"name": "chunk_index", "dataType": ["int"]},
                    {"name": "metadata", "dataType": ["text"]},
                ],
            }
            client.schema.create_class(class_obj)

    def process_document(
        self, tenant_id: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, int]:
        """
        문서를 처리하고, 변경된 청크만 임베딩하여 저장

        Args:
            tenant_id: 테넌트 ID (문서의 고유 식별자)
            content: 문서 내용
            metadata: 문서 메타데이터

        Returns:
            Dict[str, int]: 처리 결과 (추가/수정/삭제된 청크 수)
        """
        if metadata is None:
            metadata = {}

        new_chunks, modified_chunks, deleted_chunk_ids = chunk_manager.process_document(
            tenant_id, content, metadata
        )

        client = self.get_client(tenant_id)
        safe_tenant_id = vectorstore_manager._get_safe_index_name(tenant_id)
        index_name = f"Tenant_{safe_tenant_id}"
        batch = client.batch.configure(batch_size=50)

        for chunk_id in deleted_chunk_ids:
            self._delete_chunk(client, index_name, chunk_id)

        with batch:
            for chunk in new_chunks:
                self._add_chunk_to_batch(batch, index_name, chunk)

            for chunk in modified_chunks:
                self._delete_chunk(client, index_name, chunk["chunk_id"])
                self._add_chunk_to_batch(batch, index_name, chunk)

        return {
            "added": len(new_chunks),
            "modified": len(modified_chunks),
            "deleted": len(deleted_chunk_ids),
        }

    def _add_chunk_to_batch(
        self, batch: weaviate.batch.Batch, index_name: str, chunk: Dict[str, Any]
    ) -> None:
        """
        청크를 임베딩하여 Weaviate 배치에 추가

        Args:
            batch: Weaviate 배치
            index_name: 인덱스 이름
            chunk: 청크 정보
        """
        try:
            embedding = self._embeddings.embed_query(chunk["content"])

            metadata = chunk["metadata"]
            chunk_index = metadata.get("chunk_index", 0)

            batch.add_data_object(
                data_object={
                    "text": chunk["content"],
                    "tenant_id": metadata.get("tenant_id", ""),
                    "chunk_id": chunk["chunk_id"],
                    "chunk_index": chunk_index,
                    "metadata": str(metadata),
                },
                class_name=index_name,
                vector=embedding,
            )
        except Exception as e:
            print(f"임베딩 처리 중 오류 발생: {str(e)}")

    def _delete_chunk(
        self, client: weaviate.Client, index_name: str, chunk_id: str
    ) -> None:
        """
        Weaviate에서 청크 삭제

        Args:
            client: Weaviate 클라이언트
            index_name: 인덱스 이름
            chunk_id: 삭제할 청크 ID
        """
        try:
            result = (
                client.query.get(index_name, ["_additional {id}"])
                .with_where(
                    {
                        "path": ["chunk_id"],
                        "operator": "Equal",
                        "valueString": chunk_id,
                    }
                )
                .do()
            )

            if "data" in result and "Get" in result["data"]:
                objects = result["data"]["Get"][index_name]
                for obj in objects:
                    if "_additional" in obj and "id" in obj["_additional"]:
                        client.data_object.delete(obj["_additional"]["id"], index_name)
        except Exception as e:
            print(f"청크 삭제 중 오류 발생: {str(e)}")


# 전역 인스턴스
differential_vectorstore = DifferentialVectorStore.get_instance()
