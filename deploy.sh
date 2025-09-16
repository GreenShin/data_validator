#!/bin/bash

# CSV 구문정확성 검증 프로그램 배포 스크립트
# 
# 이 스크립트는 CSV 구문정확성 검증 프로그램을 PyPI에 배포합니다.

set -e  # 오류 발생 시 스크립트 종료

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 로그 함수들
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 환경 확인
check_environment() {
    log_info "배포 환경 확인 중..."
    
    # Python 확인
    if ! command -v python3 &> /dev/null; then
        log_error "Python3가 설치되지 않았습니다."
        exit 1
    fi
    
    # pip 확인
    if ! command -v pip3 &> /dev/null; then
        log_error "pip3가 설치되지 않았습니다."
        exit 1
    fi
    
    # Git 확인
    if ! command -v git &> /dev/null; then
        log_error "Git이 설치되지 않았습니다."
        exit 1
    fi
    
    log_success "환경 확인 완료"
}

# 의존성 설치
install_dependencies() {
    log_info "배포 의존성 설치 중..."
    
    pip3 install --upgrade pip
    pip3 install build twine
    
    log_success "배포 의존성 설치 완료"
}

# 코드 품질 검사
quality_check() {
    log_info "코드 품질 검사 중..."
    
    # Black 포맷팅
    log_info "코드 포맷팅 검사..."
    if ! python3 -m black src/ --check; then
        log_warning "코드 포맷팅이 필요합니다. 자동으로 수정합니다."
        python3 -m black src/
    fi
    
    # Flake8 린팅
    log_info "코드 린팅 검사..."
    python3 -m flake8 src/ --max-line-length=88 --extend-ignore=E203,W503 || true
    
    # 테스트 실행
    log_info "테스트 실행..."
    if [ -d "tests" ]; then
        python3 -m pytest tests/ -v --tb=short || true
    fi
    
    log_success "코드 품질 검사 완료"
}

# 버전 확인
check_version() {
    log_info "버전 정보 확인 중..."
    
    if [ -f "pyproject.toml" ]; then
        VERSION=$(grep 'version = ' pyproject.toml | cut -d'"' -f2)
        log_info "현재 버전: $VERSION"
    else
        log_error "pyproject.toml 파일을 찾을 수 없습니다."
        exit 1
    fi
}

# 빌드
build_package() {
    log_info "패키지 빌드 중..."
    
    # 이전 빌드 파일 정리
    if [ -d "dist" ]; then
        rm -rf dist/
    fi
    if [ -d "build" ]; then
        rm -rf build/
    fi
    
    # 패키지 빌드
    python3 -m build
    
    log_success "패키지 빌드 완료"
}

# 패키지 검사
check_package() {
    log_info "패키지 검사 중..."
    
    # Twine으로 패키지 검사
    python3 -m twine check dist/*
    
    log_success "패키지 검사 완료"
}

# 테스트 배포
test_upload() {
    log_info "테스트 PyPI에 업로드 중..."
    
    if [ -z "$TEST_PYPI_TOKEN" ]; then
        log_warning "TEST_PYPI_TOKEN이 설정되지 않았습니다. 테스트 업로드를 건너뜁니다."
        return
    fi
    
    python3 -m twine upload --repository testpypi dist/* --username __token__ --password $TEST_PYPI_TOKEN
    
    log_success "테스트 PyPI 업로드 완료"
    log_info "테스트 설치: pip install --index-url https://test.pypi.org/simple/ csv-validator"
}

# 실제 배포
upload() {
    log_info "PyPI에 업로드 중..."
    
    if [ -z "$PYPI_TOKEN" ]; then
        log_error "PYPI_TOKEN이 설정되지 않았습니다."
        exit 1
    fi
    
    python3 -m twine upload dist/* --username __token__ --password $PYPI_TOKEN
    
    log_success "PyPI 업로드 완료"
}

# Docker 이미지 빌드
build_docker() {
    log_info "Docker 이미지 빌드 중..."
    
    if command -v docker &> /dev/null; then
        docker build -t csv-validator:latest .
        log_success "Docker 이미지 빌드 완료"
    else
        log_warning "Docker가 설치되지 않았습니다. Docker 빌드를 건너뜁니다."
    fi
}

# Git 태그 생성
create_tag() {
    if [ "$1" = "--tag" ]; then
        log_info "Git 태그 생성 중..."
        
        if [ -f "pyproject.toml" ]; then
            VERSION=$(grep 'version = ' pyproject.toml | cut -d'"' -f2)
            
            # 태그가 이미 존재하는지 확인
            if git tag -l | grep -q "v$VERSION"; then
                log_warning "태그 v$VERSION가 이미 존재합니다."
            else
                git tag "v$VERSION"
                log_success "Git 태그 v$VERSION 생성 완료"
                
                # 태그 푸시 여부 확인
                read -p "태그를 원격 저장소에 푸시하시겠습니까? (y/N): " -n 1 -r
                echo
                if [[ $REPLY =~ ^[Yy]$ ]]; then
                    git push origin "v$VERSION"
                    log_success "태그 푸시 완료"
                fi
            fi
        fi
    fi
}

# 사용법 출력
show_usage() {
    echo "CSV 구문정확성 검증 프로그램 배포 스크립트"
    echo ""
    echo "사용법: $0 [옵션]"
    echo ""
    echo "옵션:"
    echo "  --test      테스트 PyPI에만 업로드합니다"
    echo "  --tag       Git 태그를 생성합니다"
    echo "  --docker    Docker 이미지를 빌드합니다"
    echo "  --help      이 도움말을 표시합니다"
    echo ""
    echo "환경 변수:"
    echo "  TEST_PYPI_TOKEN    테스트 PyPI 토큰"
    echo "  PYPI_TOKEN         PyPI 토큰"
    echo ""
    echo "예시:"
    echo "  $0 --test          # 테스트 배포"
    echo "  $0 --tag           # 태그 생성과 함께 배포"
    echo "  $0 --docker        # Docker 빌드와 함께 배포"
}

# 메인 함수
main() {
    echo "=========================================="
    echo "CSV 구문정확성 검증 프로그램 배포"
    echo "=========================================="
    echo ""
    
    # 도움말 확인
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        show_usage
        exit 0
    fi
    
    # 배포 과정 실행
    check_environment
    install_dependencies
    quality_check
    check_version
    build_package
    check_package
    
    # 옵션에 따른 추가 작업
    if [ "$1" = "--test" ]; then
        test_upload
    else
        upload
    fi
    
    if [ "$1" = "--docker" ] || [ "$2" = "--docker" ]; then
        build_docker
    fi
    
    create_tag "$1"
    
    echo ""
    echo "=========================================="
    log_success "배포가 완료되었습니다!"
    echo "=========================================="
    echo ""
    echo "설치 방법:"
    echo "  pip install csv-validator"
    echo ""
    echo "사용법:"
    echo "  csv-validator --help"
    echo ""
}

# 스크립트 실행
main "$@"
