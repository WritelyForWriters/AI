import os
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI
from fastapi.responses import StreamingResponse

from src.server.endpoints import (
    auto_modify_endpoint,
    document_endpoint,
    feedback_endpoint,
)

load_dotenv()
# 앱 설정
app = FastAPI(
    title="Research Assistant API",
    version="1.0",
    description="Literary research assistant API with multi-tenant support",
    openapi_tags=[
        {
            "name": "assistant",
            "description": "문학 작품 분석 및 피드백 관련 API",
        },
        {
            "name": "document",
            "description": "문서 관리 관련 API",
        },
    ],
)

# Assistant 관련 라우터
assistant_router = APIRouter(prefix="/v1/assistant", tags=["assistant"])


@assistant_router.post("/auto-modify")
async def query_rag(request: auto_modify_endpoint.AutoModifyQuery) -> Dict[str, Any]:
    return await auto_modify_endpoint.query_auto_modify(request)


@assistant_router.get("/feedback/stream")
async def stream_feedback_endpoint(
    tenant_id: str,
    user_setting: str,
    query: str,
) -> StreamingResponse:
    request = feedback_endpoint.FeedbackQuery(
        tenant_id=tenant_id,
        user_setting=user_setting,
        query=query,
    )
    return await feedback_endpoint.stream_feedback(request)


# 문서 관리 라우터
document_router = APIRouter(prefix="/v1/documents", tags=["document"])


@document_router.post("/upload")
async def upload_documents(
    request: document_endpoint.DocumentsUploadRequest,
) -> Dict[str, Any]:
    return await document_endpoint.upload_documents(request)


# 라우터들을 앱에 포함
app.include_router(assistant_router)
app.include_router(document_router)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", 8000))
    )
