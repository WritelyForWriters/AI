from typing import Any, AsyncGenerator, Dict, Optional

from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.chains.chat_chain import ChatChain
from src.server.models.story_settings import settings_to_xml


class ChatQuery(BaseModel):
    user_setting: Dict[str, Any]
    query: Optional[str] = None  # 선택된 구간 정보 (선택적)
    user_input: str  # 사용자 입력
    session_id: Optional[str] = None


async def query_chat(request: ChatQuery) -> Dict[str, str]:
    """
    일반 채팅 기능을 제공하는 엔드포인트 로직

    Args:
        request: 사용자 설정과 질문을 포함한 요청

    Returns:
        Dict: 채팅 응답
    """
    try:
        settings_xml = settings_to_xml(request.user_setting)
        chain = ChatChain.get_instance(request.session_id)
        query = request.query or ""  # None일 경우 빈 문자열 사용
        result = chain(settings_xml, query, request.user_input)
        return {"status": "success", "result": result["output"]}
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process chat query",
        ) from err


async def stream_chat(request: ChatQuery) -> StreamingResponse:
    """채팅 응답을 스트리밍으로 반환하는 핸들러"""
    try:
        chain = ChatChain.get_instance(request.session_id)
        query = request.query or ""  # None일 경우 빈 문자열 사용

        async def generate() -> AsyncGenerator[str, None]:
            async for chunk in chain.astream(
                settings_to_xml(request.user_setting), query, request.user_input
            ):
                if chunk:
                    yield f"data: {chunk.content}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
