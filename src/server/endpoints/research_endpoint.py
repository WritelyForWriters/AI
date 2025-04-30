from typing import Any, AsyncGenerator, Dict, Optional

from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.chains.research_chain import ResearchChain
from src.server.models.story_settings import settings_to_xml


class ResearchQuery(BaseModel):
    user_setting: Dict[str, Any]
    query: str  # 선택된 구간 정보
    user_input: str  # 사용자 입력
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
        result = chain(settings_xml, request.query or "", request.user_input)
        return {"status": "success", "result": result["output"]}
    except Exception as err:
        # 에러 로깅
        import traceback

        error_details = f"Research query failed: {str(err)}\n{traceback.format_exc()}"
        print(error_details)

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process research query: {str(err)}",
        ) from err


async def stream_research(request: ResearchQuery) -> StreamingResponse:
    """리서치 결과를 스트리밍으로 반환하는 핸들러"""
    try:
        settings_xml = settings_to_xml(request.user_setting)
        chain = ResearchChain.get_instance(request.session_id)

        async def generate() -> AsyncGenerator[str, None]:
            try:
                async for chunk in chain.astream(
                    settings_xml, request.query or "", request.user_input
                ):
                    if chunk and hasattr(chunk, "content"):
                        yield f"data: {chunk.content}\n\n"
                yield "data: [DONE]\n\n"
            except Exception as e:
                import traceback

                error_details = f"Streaming error: {str(e)}\n{traceback.format_exc()}"
                print(error_details)
                yield f"data: 죄송합니다. 스트리밍 중 오류가 발생했습니다: {str(e)}\n\n"
                yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        import traceback

        error_details = f"Stream setup error: {str(e)}\n{traceback.format_exc()}"
        print(error_details)
        raise HTTPException(status_code=500, detail=str(e)) from e
