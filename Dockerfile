FROM python:3.12-slim

WORKDIR /app

# Poetry 설치
RUN pip install poetry

# 프로젝트 파일 복사
COPY pyproject.toml poetry.lock ./
COPY .env ./
COPY src/ ./src/

# Poetry 설정: 가상환경 생성 비활성화 및 의존성 설치
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root

# 프로젝트 설치
RUN poetry install --no-interaction --no-ansi

# 서버 실행
CMD ["uvicorn", "src.server.api.router:app", "--host", "0.0.0.0", "--port", "8000"] 