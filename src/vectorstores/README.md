# 효율적인 소설 문서 임베딩 시스템

이 모듈은 소설과 같은 긴 문서의 변경사항을 효율적으로 추적하고, 변경된 청크만 임베딩하는 시스템을 제공합니다.

## 주요 구성 요소

1. **ChunkManager**: 문서를 효율적으로 청킹하고 각 청크마다 해시값을 생성하며, Redis를 사용하여 변경 사항을 추적합니다.
2. **DifferentialVectorStore**: 변경된 청크만 임베딩하여 Weaviate에 저장합니다.
3. **VectorStoreManager**: 기존 벡터스토어 관리 기능을 제공합니다.

## 특징

- 문서가 업데이트될 때마다 전체 문서를 재임베딩하지 않고, 변경된 부분만 처리하여 비용과 시간을 절약합니다.
- tenant_id를 고유 식별자로 사용하여 소설과 같은 작품별로 효율적으로 관리합니다.
- Redis를 사용하여 청크 해시값을 캐싱하고, 변경 여부를 빠르게 감지합니다.
- Weaviate를 사용하여 임베딩된 청크를 저장하고 RAG 시스템에 활용합니다.

## 사용 방법

```python
from src.vectorstores.differential_vectorstore import differential_vectorstore

# 문서 처리 및 변경된 청크만 임베딩
result = differential_vectorstore.process_document(
    tenant_id="novel-001",  # 작품 고유 ID
    content="소설 전체 내용...",
    metadata={"title": "장편소설", "author": "작가명"}
)

# 처리 결과
print(f"새로 추가된 청크: {result['added']}")
print(f"수정된 청크: {result['modified']}")
print(f"삭제된 청크: {result['deleted']}")
```

## API 엔드포인트

- `POST /v1/document/upload`: 단일 문서 업로드 및 처리
- `POST /v1/document/upload/batch`: 여러 문서 일괄 업로드 및 처리 