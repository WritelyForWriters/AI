from typing import AsyncGenerator

from fastapi import HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from src.chains.feedback_chain import FeedbackChain
from src.vectorstores.vectorstore_manager import vectorstore_manager


class FeedbackQuery(BaseModel):
    user_setting: str
    query: str
    tenant_id: str


async def stream_feedback(request: FeedbackQuery) -> StreamingResponse:
    """피드백을 스트리밍으로 반환하는 핸들러"""
    try:
        # 벡터스토어 설정
        client = vectorstore_manager.get_client(request.tenant_id)
        index_name = f"Tenant_{request.tenant_id}"

        # 피드백 체인 생성
        chain = FeedbackChain(
            client=client,
            index_name=index_name,
            embeddings=vectorstore_manager._embeddings,
        )

        async def generate() -> AsyncGenerator[str, None]:
            async for chunk in chain.astream(request.user_setting, request.query):
                if chunk:
                    yield f"data: {chunk.content}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=str(e)
        ) from e  # 원인이 되는 예외를 명시적으로 연결
