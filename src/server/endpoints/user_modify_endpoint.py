from typing import Any, AsyncGenerator, Dict

from fastapi import HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic.main import BaseModel

from src.chains.user_modify_chain import UserModifyChain
from src.server.models.story_settings import settings_to_xml
from src.vectorstores.vectorstore_manager import vectorstore_manager


class UserModifyQuery(BaseModel):
    tenant_id: str
    user_setting: Dict[str, Any]
    query: str
    how_polish: str


async def query_user_modify(request: UserModifyQuery) -> Dict[str, str]:
    """
    RAG 체인을 사용하여 사용자가 요청한 수정사항을 반영하여
    쿼리에 응답하는 엔드포인트 로직

    Args:
        request: 테넌트 ID와 쿼리를 포함한 요청

    Returns:
        Dict: 수정된 문장을 포함한 응답
    """
    try:
        settings_xml = settings_to_xml(request.user_setting)
        client = vectorstore_manager.get_client(request.tenant_id)
        index_name = f"Tenant_{request.tenant_id}"
        chain = UserModifyChain(
            client=client,
            index_name=index_name,
            embeddings=vectorstore_manager._embeddings,
        )
        result = chain(settings_xml, request.query, request.how_polish)
        return {"status": "success", "result": result["output"]}

    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process user modification",
        ) from err


async def stream_user_modify(request: UserModifyQuery) -> StreamingResponse:
    """사용자 수정 결과를 스트리밍으로 반환하는 핸들러"""
    try:
        client = vectorstore_manager.get_client(request.tenant_id)
        index_name = f"Tenant_{request.tenant_id}"
        chain = UserModifyChain(
            client=client,
            index_name=index_name,
            embeddings=vectorstore_manager._embeddings,
        )

        async def generate() -> AsyncGenerator[str, None]:
            async for chunk in chain.astream(
                settings_to_xml(request.user_setting),
                request.query,
                request.how_polish,
            ):
                if chunk:
                    yield f"data: {chunk.content}\n\n"
            yield "data: [DONE]\n\n"

        return StreamingResponse(generate(), media_type="text/event-stream")

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
