# CSV 구문정확성 검증 프로그램 Docker 이미지
FROM python:3.11-slim

# 메타데이터
LABEL maintainer="CSV Validator Team"
LABEL description="CSV 구문정확성 검증 프로그램"
LABEL version="0.1.0"

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 패키지 업데이트 및 필요한 도구 설치
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 파일 복사
COPY requirements.txt .

# Python 의존성 설치
RUN pip install --no-cache-dir -r requirements.txt

# 애플리케이션 코드 복사
COPY src/ ./src/
COPY pyproject.toml .
COPY setup.py .

# 패키지 설치
RUN pip install -e .

# 데이터 디렉토리 생성
RUN mkdir -p /app/data /app/results

# 환경 변수 설정
ENV PYTHONPATH=/app
ENV CSV_VALIDATOR_DATA_DIR=/app/data
ENV CSV_VALIDATOR_RESULTS_DIR=/app/results

# 볼륨 마운트 포인트
VOLUME ["/app/data", "/app/results"]

# 기본 명령어
CMD ["python", "-m", "src.main", "--help"]

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -m src.main --version || exit 1
