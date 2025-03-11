import hashlib
import json
import os
from typing import Any, Callable, Dict, List, Optional, Tuple

import redis
from dotenv import load_dotenv
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter

load_dotenv()


class ChunkManager:
    """
    소설과 같은 긴 문서의 청킹 및 변경 감지를 담당하는 클래스
    Redis를 사용하여 청크 해시값을 저장하고 변경된 청크만 식별
    """

    _instance = None

    @classmethod
    def get_instance(cls) -> "ChunkManager":
        """싱글톤 인스턴스 반환"""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        length_function: Callable[[str], int] = len,
    ):
        redis_host = os.getenv("REDIS_HOST", "localhost")
        redis_port = os.getenv("REDIS_PORT", "6379")
        self.redis_client = redis.Redis(
            host=redis_host,
            port=int(redis_port),
            decode_responses=True,
        )

        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=length_function,
            is_separator_regex=False,
        )

    def process_document(
        self, tenant_id: str, content: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[str]]:
        """
        문서를 처리하고 변경된 청크만 식별하여 반환

        Args:
            tenant_id: 테넌트 ID (작품의 고유 식별자)
            content: 문서 내용
            metadata: 문서 메타데이터

        Returns:
            Tuple[List[Dict], List[Dict], List[Dict]]:
                - 새로 추가된 청크
                - 변경된 청크
                - 삭제된 청크 ID
        """
        if metadata is None:
            metadata = {}

        doc_metadata = {**metadata, "tenant_id": tenant_id}

        current_chunks = self._chunk_document(content, doc_metadata)

        redis_key = f"chunks:{tenant_id}:data"
        stored_chunks_json = self.redis_client.get(redis_key)

        if not stored_chunks_json:
            self._store_chunk_info(redis_key, current_chunks)
            return current_chunks, [], []

        try:
            stored_chunks = json.loads(stored_chunks_json)
        except json.JSONDecodeError:
            self._store_chunk_info(redis_key, current_chunks)
            return current_chunks, [], []

        new_chunks, modified_chunks, deleted_chunk_ids = self._identify_changes(
            stored_chunks, current_chunks
        )

        if new_chunks or modified_chunks or deleted_chunk_ids:
            self._store_chunk_info(redis_key, current_chunks)

        return new_chunks, modified_chunks, deleted_chunk_ids

    def _chunk_document(
        self, document: str, metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        문서를 청크로 분할하고 해시값과 함께 반환

        Args:
            document: 청킹할 텍스트 문서
            metadata: 문서의 메타데이터

        Returns:
            List[Dict]: 청크 정보 (청크 ID, 내용, 해시값, 메타데이터)
        """
        doc = Document(page_content=document, metadata=metadata)

        chunks = self.text_splitter.split_documents([doc])

        chunked_data = []
        for i, chunk in enumerate(chunks):
            tenant_id = metadata.get("tenant_id", "")
            chunk_id = f"{tenant_id}_{i}"
            chunk_hash = self._generate_hash(chunk.page_content)

            chunked_data.append(
                {
                    "chunk_id": chunk_id,
                    "content": chunk.page_content,
                    "hash": chunk_hash,
                    "metadata": {**chunk.metadata, "chunk_index": i},
                }
            )

        return chunked_data

    def _identify_changes(
        self, stored_chunks: List[Dict[str, Any]], current_chunks: List[Dict[str, Any]]
    ) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]], List[str]]:
        """
        기존 청크와 현재 청크를 비교하여 변경 사항 식별

        Args:
            stored_chunks: 저장된 청크 정보
            current_chunks: 현재 청크 정보

        Returns:
            Tuple[List[Dict], List[Dict], List[str]]:
                - 새로 추가된 청크
                - 변경된 청크
                - 삭제된 청크 ID
        """
        stored_chunk_map = {chunk["chunk_id"]: chunk for chunk in stored_chunks}
        current_chunk_map = {chunk["chunk_id"]: chunk for chunk in current_chunks}

        new_chunks = []
        modified_chunks = []
        current_chunk_ids = set(current_chunk_map.keys())
        stored_chunk_ids = set(stored_chunk_map.keys())

        for chunk_id, chunk in current_chunk_map.items():
            if chunk_id not in stored_chunk_ids:
                new_chunks.append(chunk)
            elif chunk["hash"] != stored_chunk_map[chunk_id]["hash"]:
                modified_chunks.append(chunk)

        deleted_chunk_ids = list(stored_chunk_ids - current_chunk_ids)

        return new_chunks, modified_chunks, deleted_chunk_ids

    def _store_chunk_info(self, redis_key: str, chunks: List[Dict[str, Any]]) -> None:
        """
        청크 정보를 Redis에 저장

        Args:
            redis_key: Redis 키
            chunks: 저장할 청크 정보
        """
        chunks_json = json.dumps(chunks)
        self.redis_client.set(redis_key, chunks_json)

    def get_document_chunks(self, tenant_id: str) -> Any:
        """
        문서의 저장된 청크 정보 조회

        Args:
            tenant_id: 테넌트 ID

        Returns:
            List[Dict]: 저장된 청크 정보
        """
        redis_key = f"chunks:{tenant_id}:data"
        stored_chunks_json = self.redis_client.get(redis_key)

        if not stored_chunks_json:
            return []

        try:
            return json.loads(stored_chunks_json)
        except json.JSONDecodeError:
            return []

    def _generate_hash(self, text: str) -> str:
        """
        텍스트에 대한 해시값 생성

        Args:
            text: 해시할 텍스트

        Returns:
            str: 해시값
        """
        return hashlib.md5(text.encode("utf-8")).hexdigest()


# 전역 인스턴스
chunk_manager = ChunkManager.get_instance()
