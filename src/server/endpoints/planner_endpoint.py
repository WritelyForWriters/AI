from typing import AsyncGenerator, Dict

from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.chains.planner_chain import PlannerChain, PlannerSection


class PlannerQuery(BaseModel):
    genre: str
    logline: str
    prompt: str
    section: PlannerSection
    tenant_id: str


async def query_planner(request: PlannerQuery) -> Dict[str, str]:
    """
    플래너 체인을 사용하여 소설 기획 내용을 생성하는 엔드포인트 로직

    Args:
        request: 장르, 로그라인, 프롬프트, 섹션 정보를 포함한 요청

    Returns:
        Dict: 플래너 체인의 응답
    """
    try:
        chain = PlannerChain.get_instance(request.tenant_id)
        result = chain(
            request.genre,
            request.logline,
            request.prompt,
            request.section,
        )
        return {"status": "success", "result": result["output"]}
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to generate planner content",
        ) from err


async def stream_planner(request: PlannerQuery) -> StreamingResponse:
    """플래너 생성 결과를 스트리밍으로 반환하는 핸들러"""
    try:
        chain = PlannerChain.get_instance(request.tenant_id)

        async def generate() -> AsyncGenerator[str, None]:
            async for chunk in chain.astream(
                request.genre,
                request.logline,
                request.prompt,
                request.section,
            ):
                if chunk:
                    yield f"data: {chunk.content}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
