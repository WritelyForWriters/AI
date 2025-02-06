from typing import AsyncGenerator, Dict

from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.vectorstores.vectorstore_manager import vectorstore_manager


class AutoModifyQuery(BaseModel):
    tenant_id: str
    user_setting: str
    query: str


async def query_auto_modify(request: AutoModifyQuery) -> Dict[str, str]:
    """
    RAG 체인을 사용하여 쿼리에 응답하는 엔드포인트 로직

    Args:
        request: 테넌트 ID와 쿼리를 포함한 요청

    Returns:
        Dict: RAG 체인의 응답
    """
    try:
        chain = vectorstore_manager.get_chain(request.tenant_id)
        result = chain(request.user_setting, request.query)
        return {"status": "success", "result": result["output"]}
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process auto modification",
        ) from err


async def stream_auto_modify(request: AutoModifyQuery) -> StreamingResponse:
    """자동 수정 결과를 스트리밍으로 반환하는 핸들러"""
    try:
        chain = vectorstore_manager.get_chain(request.tenant_id)

        async def generate() -> AsyncGenerator[str, None]:
            async for chunk in chain.astream(
                request.user_setting,
                request.query,
            ):
                if chunk:
                    yield f"data: {chunk.content}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
