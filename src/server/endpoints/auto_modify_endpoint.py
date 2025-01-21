from fastapi import HTTPException
from pydantic import BaseModel
from typing import Dict
from src.vectorstores.vectorstore_manager import vectorstore_manager

class RAGQuery(BaseModel):
    user_setting: str
    context: str
    query: str
    tenant_id: str

async def query_rag(request: RAGQuery) -> Dict:
    """
    RAG 체인을 사용하여 쿼리에 응답하는 엔드포인트 로직
    
    Args:
        request: 테넌트 ID와 쿼리를 포함한 요청
        
    Returns:
        Dict: RAG 체인의 응답
    """
    try:
        chain = vectorstore_manager.get_chain(request.tenant_id)
        result = chain(request.user_setting, request.context, request.query)
        return {
            "status": "success", 
            "result": result["output"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 