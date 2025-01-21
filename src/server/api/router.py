from fastapi import APIRouter, FastAPI
from langserve import add_routes
from src.chains.research_chain import create_research_chain
from src.server.endpoints import document_endpoint, rag_endpoint
from dotenv import load_dotenv
import os

load_dotenv()
# 앱 설정
app = FastAPI(
    title="Research Assistant API",
    version="1.0",
    description="Literary research assistant API with multi-tenant support"
)

# Assistant 관련 라우터
assistant_router = APIRouter(prefix="/v1/assistant")

# RAG 쿼리 라우트
@assistant_router.post("/rag")
async def query_rag(request: rag_endpoint.RAGQuery):
    return await rag_endpoint.query_rag(request)

# 문서 관리 라우터
document_router = APIRouter(prefix="/v1/documents")

@document_router.post("/upload")
async def upload_documents(request: document_endpoint.DocumentsUploadRequest):
    return await document_endpoint.upload_documents(request)

# 라우터들을 앱에 포함
app.include_router(assistant_router)
app.include_router(document_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host=os.getenv("HOST", "127.0.0.1"), port=int(os.getenv("PORT", 8000)))