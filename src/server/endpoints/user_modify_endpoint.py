from typing import Dict
from fastapi import HTTPException, status
from pydantic.main import BaseModel
from src.chains.user_modify_chain import UserModifyChain
from src.vectorstores.vectorstore_manager import vectorstore_manager


class UserModifyQuery(BaseModel):
    user_setting: str
    context: str  # 사용자가 입력한 소설
    prompt: str  # 사용자가 입력한 프롬프트
    tenant_id: str


async def query_user_modify(request: UserModifyQuery) -> Dict[str, str]:
    """
    사용자가 입력한 프롬프트와 텍스트를 기반으로 문장을 수정하는 엔드포인트 로직

    Args:
        request: 사용자 입력 텍스트와 프롬프트 포함 요청

    Returns:
        Dict: 수정된 문장을 포함한 응답
    """
    try:
        client = vectorstore_manager.get_client(request.tenant_id)
        index_name = f"Tenant_{request.tenant_id}"

        # 피드백 체인 생성
        chain = UserModifyChain(
            client=client,
            index_name=index_name,
            embeddings=vectorstore_manager._embeddings,
        )
        print("chain 생성 후:", chain)

        # if not isinstance(chain, UserModifyChain):
        #     raise ValueError(f"오류: tenant_id={request.tenant_id}에 대한 체인이 존재 하지 않음")

        prompt_text = f"사용자 요청: '{request.prompt}'\n"
        # print("request.context", request.context, "request.prompt", request.prompt)
        # 체인을 사용 하여 결과 처리
        result = chain(request.user_setting, request.context, prompt_text)  # 정보, 사용자 입력 소설, 사용자 입력한 프롬프트
        print("result", result)
        return {"status": "success", "modified_text": result["modified_text"]}

    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process user modification",
        ) from err
