"""
Main entry point for Data Validator.

이 모듈은 Data Validator 프로그램의 메인 진입점입니다.
CSV, JSON, JSONL 파일의 구문정확성을 검증합니다.
"""

import sys
import os
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.cli.commands import cli


def main():
    """
    Data Validator의 메인 함수

    명령행 인터페이스를 통해 CSV, JSON, JSONL 파일 검증 기능을 제공합니다.
    """
    try:
        # CLI 실행
        cli()
    except KeyboardInterrupt:
        print("\n❌ 사용자에 의해 중단되었습니다.")
        sys.exit(1)
    except Exception as e:
        print(f"❌ 예상치 못한 오류가 발생했습니다: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
