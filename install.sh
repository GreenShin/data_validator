#!/bin/bash

# CSV 구문정확성 검증 프로그램 설치 스크립트
# 
# 이 스크립트는 CSV 구문정확성 검증 프로그램을 시스템에 설치합니다.

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

# Python 버전 확인
check_python() {
    log_info "Python 버전 확인 중..."
    
    if command -v python3 &> /dev/null; then
        PYTHON_CMD="python3"
    elif command -v python &> /dev/null; then
        PYTHON_CMD="python"
    else
        log_error "Python이 설치되지 않았습니다. Python 3.8 이상을 설치해주세요."
        exit 1
    fi
    
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
        log_error "Python 3.8 이상이 필요합니다. 현재 버전: $PYTHON_VERSION"
        exit 1
    fi
    
    log_success "Python 버전 확인 완료: $PYTHON_VERSION"
}

# pip 확인
check_pip() {
    log_info "pip 확인 중..."
    
    if ! command -v pip3 &> /dev/null && ! command -v pip &> /dev/null; then
        log_error "pip이 설치되지 않았습니다. pip을 설치해주세요."
        exit 1
    fi
    
    log_success "pip 확인 완료"
}

# 가상환경 생성 (선택사항)
create_venv() {
    if [ "$1" = "--venv" ]; then
        log_info "가상환경 생성 중..."
        
        if [ -d "venv" ]; then
            log_warning "기존 가상환경이 있습니다. 삭제하고 새로 생성합니다."
            rm -rf venv
        fi
        
        $PYTHON_CMD -m venv venv
        
        if [ -f "venv/bin/activate" ]; then
            source venv/bin/activate
            log_success "가상환경 생성 및 활성화 완료"
        else
            log_error "가상환경 생성에 실패했습니다."
            exit 1
        fi
    fi
}

# 의존성 설치
install_dependencies() {
    log_info "의존성 설치 중..."
    
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        log_success "의존성 설치 완료"
    else
        log_error "requirements.txt 파일을 찾을 수 없습니다."
        exit 1
    fi
}

# 개발 의존성 설치 (선택사항)
install_dev_dependencies() {
    if [ "$1" = "--dev" ]; then
        log_info "개발 의존성 설치 중..."
        
        if [ -f "pyproject.toml" ]; then
            pip install -e ".[dev]"
            log_success "개발 의존성 설치 완료"
        else
            log_warning "pyproject.toml 파일을 찾을 수 없습니다. 기본 개발 도구만 설치합니다."
            pip install pytest black flake8 mypy
            log_success "기본 개발 도구 설치 완료"
        fi
    fi
}

# 설치 검증
verify_installation() {
    log_info "설치 검증 중..."
    
    if $PYTHON_CMD -m src.main --version &> /dev/null; then
        log_success "설치 검증 완료"
        
        # 버전 정보 출력
        VERSION=$($PYTHON_CMD -m src.main --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+\.[0-9]\+')
        log_success "CSV 구문정확성 검증 프로그램 v$VERSION 설치 완료"
    else
        log_error "설치 검증에 실패했습니다."
        exit 1
    fi
}

# 사용법 출력
show_usage() {
    echo "CSV 구문정확성 검증 프로그램 설치 스크립트"
    echo ""
    echo "사용법: $0 [옵션]"
    echo ""
    echo "옵션:"
    echo "  --venv     가상환경을 생성하고 활성화합니다"
    echo "  --dev      개발 의존성을 포함하여 설치합니다"
    echo "  --help     이 도움말을 표시합니다"
    echo ""
    echo "예시:"
    echo "  $0                    # 기본 설치"
    echo "  $0 --venv             # 가상환경과 함께 설치"
    echo "  $0 --venv --dev       # 가상환경과 개발 도구와 함께 설치"
}

# 메인 함수
main() {
    echo "=========================================="
    echo "CSV 구문정확성 검증 프로그램 설치"
    echo "=========================================="
    echo ""
    
    # 도움말 확인
    if [ "$1" = "--help" ] || [ "$1" = "-h" ]; then
        show_usage
        exit 0
    fi
    
    # 설치 과정 실행
    check_python
    check_pip
    create_venv "$1"
    install_dependencies
    install_dev_dependencies "$1"
    verify_installation
    
    echo ""
    echo "=========================================="
    log_success "설치가 완료되었습니다!"
    echo "=========================================="
    echo ""
    echo "사용법:"
    echo "  $PYTHON_CMD -m src.main --help"
    echo ""
    echo "예시:"
    echo "  # 샘플 설정 파일 생성"
    echo "  $PYTHON_CMD -m src.main init -o my_config.yml"
    echo ""
    echo "  # CSV 파일 검증"
    echo "  $PYTHON_CMD -m src.main validate -c my_config.yml -i data.csv"
    echo ""
    
    if [ "$1" = "--venv" ]; then
        echo "가상환경을 비활성화하려면 'deactivate' 명령을 사용하세요."
    fi
}

# 스크립트 실행
main "$@"
