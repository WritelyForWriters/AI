from typing import Any, AsyncGenerator, Dict

from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.chains.feedback_chain import FeedbackChain
from src.server.models.story_settings import settings_to_xml
from src.vectorstores.vectorstore_manager import vectorstore_manager


class FeedbackQuery(BaseModel):
    user_setting: Dict[str, Any]
    query: str
    tenant_id: str


async def query_feedback(request: FeedbackQuery) -> Dict[str, str]:
    """
    구간 피드백 체인을 사용하여 쿼리에 응답하는 엔드포인트 로직

    Args:
        request: 테넌트 ID와 쿼리를 포함한 요청

    Returns:
        Dict: 구간 피드백 체인의 응답
    """
    try:
        client = vectorstore_manager.get_client(request.tenant_id)
        index_name = f"Tenant_{request.tenant_id}"
        chain = FeedbackChain.get_instance(
            client=client,
            index_name=index_name,
            embeddings=vectorstore_manager._embeddings,
        )
        result = chain(settings_to_xml(request.user_setting), request.query)
        return {"status": "success", "result": result["output"]}
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process feedback",
        ) from err


async def stream_feedback(request: FeedbackQuery) -> StreamingResponse:
    """피드백을 스트리밍으로 반환하는 핸들러"""
    try:
        client = vectorstore_manager.get_client(request.tenant_id)
        index_name = f"Tenant_{request.tenant_id}"
        chain = FeedbackChain.get_instance(
            client=client,
            index_name=index_name,
            embeddings=vectorstore_manager._embeddings,
        )

        async def generate() -> AsyncGenerator[str, None]:
            async for chunk in chain.astream(
                settings_to_xml(request.user_setting), request.query
            ):
                if chunk:
                    yield f"data: {chunk.content}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
