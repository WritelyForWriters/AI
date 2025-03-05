from typing import Any, AsyncGenerator, Dict, Optional

from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.chains.research_chain import ResearchChain
from src.server.models.story_settings import settings_to_xml


class ResearchQuery(BaseModel):
    user_setting: Dict[str, Any]
    query: str
    session_id: Optional[str] = None


async def query_research(request: ResearchQuery) -> Dict[str, str]:
    """
    리서치 체인을 사용하여 쿼리에 응답하는 엔드포인트 로직

    Args:
        request: 사용자 설정과 쿼리를 포함한 요청

    Returns:
        Dict: 리서치 체인의 응답
    """
    try:
        settings_xml = settings_to_xml(request.user_setting)
        chain = ResearchChain.get_instance(request.session_id)
        result = chain(settings_xml, request.query)
        return {"status": "success", "result": result["output"]}
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process research query",
        ) from err


async def stream_research(request: ResearchQuery) -> StreamingResponse:
    """리서치 결과를 스트리밍으로 반환하는 핸들러"""
    try:
        chain = ResearchChain.get_instance()

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
