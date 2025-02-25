import os
from typing import Any, Dict

from dotenv import load_dotenv
from fastapi import APIRouter, FastAPI
from fastapi.responses import StreamingResponse

from src.server.docs.api_docs import (
    AUTO_MODIFY_DOCS,
    AUTO_MODIFY_STREAM_DOCS,
    FEEDBACK_DOCS,
    FEEDBACK_STREAM_DOCS,
    PLANNER_DOCS,
    PLANNER_STREAM_DOCS,
    RESEARCH_DOCS,
    USER_MODIFY_DOCS,
    USER_MODIFY_STREAM_DOCS,
)
from src.server.endpoints import (
    auto_modify_endpoint,
    document_endpoint,
    feedback_endpoint,
    planner_endpoint,
    research_endpoint,
    user_modify_endpoint,
)

load_dotenv()
# 앱 설정
app = FastAPI(
    title="AI Assistant API",
    version="1.0",
    description="Literary AI assistant API with multi-tenant support",
    openapi_tags=[
        {
            "name": "assistant",
            "description": "문학 작품 분석 및 피드백 관련 API",
        },
        {
            "name": "planner",
            "description": "소설 기획 및 설정 생성 관련 API",
        },
        {
            "name": "document",
            "description": "문서 관리 관련 API",
        },
    ],
)

# Assistant 관련 라우터
assistant_router = APIRouter(prefix="/v1/assistant", tags=["assistant"])


@assistant_router.post(
    "/auto-modify",
    summary=AUTO_MODIFY_DOCS["summary"],
    description=AUTO_MODIFY_DOCS["description"],
    responses=AUTO_MODIFY_DOCS["responses"],
)
async def query_rag(request: auto_modify_endpoint.AutoModifyQuery) -> Dict[str, Any]:
    return await auto_modify_endpoint.query_auto_modify(request)


@assistant_router.post(
    "/auto-modify/stream",
    summary=AUTO_MODIFY_STREAM_DOCS["summary"],
    description=AUTO_MODIFY_STREAM_DOCS["description"],
    responses=AUTO_MODIFY_STREAM_DOCS["responses"],
)
async def stream_auto_modify_endpoint(
    request: auto_modify_endpoint.AutoModifyQuery,
) -> StreamingResponse:
    return await auto_modify_endpoint.stream_auto_modify(request)


@assistant_router.post(
    "/user-modify",
    summary=USER_MODIFY_DOCS["summary"],
    description=USER_MODIFY_DOCS["description"],
    responses=USER_MODIFY_DOCS["responses"],
)
async def modify_text(request: user_modify_endpoint.UserModifyQuery) -> Dict[str, Any]:
    return await user_modify_endpoint.query_user_modify(request)


@assistant_router.post(
    "/user-modify/stream",
    summary=USER_MODIFY_STREAM_DOCS["summary"],
    description=USER_MODIFY_STREAM_DOCS["description"],
    responses=USER_MODIFY_STREAM_DOCS["responses"],
)
async def stream_user_modify_endpoint(
    request: user_modify_endpoint.UserModifyQuery,
) -> StreamingResponse:
    return await user_modify_endpoint.stream_user_modify(request)


@assistant_router.post(
    "/feedback",
    summary=FEEDBACK_DOCS["summary"],
    description=FEEDBACK_DOCS["description"],
    responses=FEEDBACK_DOCS["responses"],
)
async def query_feedback_endpoint(
    request: feedback_endpoint.FeedbackQuery,
) -> Dict[str, Any]:
    return await feedback_endpoint.query_feedback(request)


@assistant_router.post(
    "/feedback/stream",
    summary=FEEDBACK_STREAM_DOCS["summary"],
    description=FEEDBACK_STREAM_DOCS["description"],
    responses=FEEDBACK_STREAM_DOCS["responses"],
)
async def stream_feedback_endpoint(
    request: feedback_endpoint.FeedbackQuery,
) -> StreamingResponse:
    return await feedback_endpoint.stream_feedback(request)


@assistant_router.post(
    "/research",
    summary=RESEARCH_DOCS["summary"],
    description=RESEARCH_DOCS["description"],
    responses=RESEARCH_DOCS["responses"],
)
async def query_research_endpoint(
    request: research_endpoint.ResearchQuery,
) -> Dict[str, Any]:
    return await research_endpoint.query_research(request)


# TODO: 스트리밍 기능 추가 후 활성화
# @assistant_router.post(
#     "/research/stream",
#     summary=RESEARCH_STREAM_DOCS["summary"],
#     description=RESEARCH_STREAM_DOCS["description"],
#     responses=RESEARCH_STREAM_DOCS["responses"],
# )
# async def stream_research_endpoint(
#     request: research_endpoint.ResearchQuery,
# ) -> StreamingResponse:
#     return await research_endpoint.stream_research(request)


# 플래너 관련 라우터
planner_router = APIRouter(prefix="/v1/planner", tags=["planner"])


@planner_router.post(
    "/generate",
    summary=PLANNER_DOCS["summary"],
    description=PLANNER_DOCS["description"],
    responses=PLANNER_DOCS["responses"],
)
async def query_planner_endpoint(
    request: planner_endpoint.PlannerQuery,
) -> Dict[str, Any]:
    return await planner_endpoint.query_planner(request)


@planner_router.post(
    "/generate/stream",
    summary=PLANNER_STREAM_DOCS["summary"],
    description=PLANNER_STREAM_DOCS["description"],
    responses=PLANNER_STREAM_DOCS["responses"],
)
async def stream_planner_endpoint(
    request: planner_endpoint.PlannerQuery,
) -> StreamingResponse:
    return await planner_endpoint.stream_planner(request)


# 문서 관리 라우터
document_router = APIRouter(prefix="/v1/documents", tags=["document"])


@document_router.post("/upload")
async def upload_documents(
    request: document_endpoint.DocumentsUploadRequest,
) -> Dict[str, Any]:
    return await document_endpoint.upload_documents(request)


# 라우터들을 앱에 포함
app.include_router(assistant_router)
app.include_router(planner_router)
app.include_router(document_router)


@app.get("/health", tags=["health"])
async def health_check() -> Dict[str, str]:
    """서비스 헬스 체크 엔드포인트"""
    return {"status": "healthy", "version": "1.0"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", 8000))
    )
