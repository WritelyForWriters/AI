from fastapi import HTTPException
from pydantic import BaseModel
from typing import List, Dict
from langchain.schema import Document
from src.vectorstores.vectorstore_manager import vectorstore_manager

class DocumentInput(BaseModel):
    content: str
    metadata: dict = {}

class DocumentsUploadRequest(BaseModel):
    tenant_id: str
    documents: List[DocumentInput]

async def upload_documents(request: DocumentsUploadRequest) -> Dict:
    """
    문서들을 벡터 스토어에 업로드하는 엔드포인트 로직
    
    Args:
        request: 테넌트 ID와 업로드할 문서들을 포함한 요청
        
    Returns:
        Dict: 업로드 결과 메시지
    """
    try:
        documents = [
            Document(page_content=doc.content, metadata=doc.metadata)
            for doc in request.documents
        ]
        
        vectorstore_manager.add_documents(request.tenant_id, documents)
        
        return {"status": "success", "message": f"{len(documents)}개의 문서가 추가되었습니다."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 