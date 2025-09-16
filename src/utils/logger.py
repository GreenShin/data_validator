"""
Logging utilities for CSV validation.

이 모듈은 로깅 및 진행률 표시 기능을 제공합니다.
"""

import logging
import sys
from datetime import datetime
from typing import Optional, Any, Dict
from pathlib import Path

try:
    from rich.console import Console
    from rich.progress import (
        Progress,
        SpinnerColumn,
        TextColumn,
        BarColumn,
        TimeElapsedColumn,
    )
    from rich.logging import RichHandler
    from rich.table import Table
    from rich.panel import Panel
    from rich.text import Text

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class Logger:
    """로깅 및 진행률 표시를 담당하는 클래스"""

    def __init__(self, verbose: bool = False, log_file: Optional[str] = None):
        """
        Logger 초기화

        Args:
            verbose: 상세 로그 출력 여부
            log_file: 로그 파일 경로 (선택적)
        """
        self.verbose = verbose
        self.log_file = log_file
        self.console = Console() if RICH_AVAILABLE else None
        self.logger = self._setup_logger()
        self.progress = None
        self.task_id = None

    def _setup_logger(self) -> logging.Logger:
        """로거를 설정합니다."""
        logger = logging.getLogger("csv_validator")
        logger.setLevel(logging.DEBUG if self.verbose else logging.INFO)

        # 기존 핸들러 제거
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)

        # 콘솔 핸들러 설정
        if RICH_AVAILABLE and self.console:
            # Rich 핸들러 사용
            console_handler = RichHandler(
                console=self.console,
                show_time=True,
                show_path=False,
                rich_tracebacks=True,
            )
            console_handler.setLevel(logging.DEBUG if self.verbose else logging.INFO)
        else:
            # 기본 핸들러 사용
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(logging.DEBUG if self.verbose else logging.INFO)
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                datefmt="%Y-%m-%d %H:%M:%S",
            )
            console_handler.setFormatter(formatter)

        logger.addHandler(console_handler)

        # 파일 핸들러 설정 (로그 파일이 지정된 경우)
        if self.log_file:
            try:
                log_path = Path(self.log_file)
                log_path.parent.mkdir(parents=True, exist_ok=True)

                file_handler = logging.FileHandler(log_path, encoding="utf-8")
                file_handler.setLevel(logging.DEBUG)
                file_formatter = logging.Formatter(
                    "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
                file_handler.setFormatter(file_formatter)
                logger.addHandler(file_handler)

            except Exception as e:
                logger.warning(f"로그 파일 설정 실패: {e}")

        return logger

    def info(self, message: str, **kwargs) -> None:
        """정보 로그를 출력합니다."""
        self.logger.info(message, **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """디버그 로그를 출력합니다."""
        self.logger.debug(message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """경고 로그를 출력합니다."""
        self.logger.warning(message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """오류 로그를 출력합니다."""
        self.logger.error(message, **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """치명적 오류 로그를 출력합니다."""
        self.logger.critical(message, **kwargs)

    def log_progress(
        self, current: int, total: int, message: str = "처리 중..."
    ) -> None:
        """
        진행률을 표시합니다.

        Args:
            current: 현재 진행 단계
            total: 전체 단계 수
            message: 진행 메시지
        """
        if not self.console or not RICH_AVAILABLE:
            # Rich가 없는 경우 기본 출력
            percentage = (current / total * 100) if total > 0 else 0
            print(
                f"\r{message}: {current}/{total} ({percentage:.1f}%)",
                end="",
                flush=True,
            )
            if current >= total:
                print()  # 완료 시 줄바꿈
            return

        if self.progress is None:
            # 진행률 바 초기화
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=self.console,
            )
            self.progress.start()
            self.task_id = self.progress.add_task(message, total=total)

        # 진행률 업데이트
        self.progress.update(self.task_id, completed=current, description=message)

        if current >= total:
            self.progress.stop()
            self.progress = None
            self.task_id = None

    def log_success(self, message: str) -> None:
        """성공 메시지를 출력합니다."""
        if self.console and RICH_AVAILABLE:
            self.console.print(f"✅ {message}", style="green")
        else:
            self.info(f"✅ {message}")

    def log_error(self, error: Exception, context: str = "") -> None:
        """
        오류를 로깅합니다.

        Args:
            error: 발생한 오류
            context: 오류 발생 컨텍스트
        """
        error_message = f"❌ {context}: {str(error)}" if context else f"❌ {str(error)}"

        if self.console and RICH_AVAILABLE:
            self.console.print(error_message, style="red")
        else:
            self.error(error_message)

        # 상세 오류 정보 (verbose 모드에서만)
        if self.verbose:
            import traceback

            self.debug(f"오류 상세 정보:\n{traceback.format_exc()}")

    def log_validation_start(self, file_name: str, total_rows: int) -> None:
        """검증 시작을 로깅합니다."""
        message = f"검증 시작: {file_name} ({total_rows:,}행)"
        if self.console and RICH_AVAILABLE:
            self.console.print(f"🚀 {message}", style="blue")
        else:
            self.info(f"🚀 {message}")

    def log_validation_complete(
        self, file_name: str, errors: int, processing_time: float
    ) -> None:
        """검증 완료를 로깅합니다."""
        status = "✅ 성공" if errors == 0 else f"⚠️ {errors}개 오류 발견"
        message = f"검증 완료: {file_name} - {status} ({processing_time:.2f}초)"

        if self.console and RICH_AVAILABLE:
            style = "green" if errors == 0 else "yellow"
            self.console.print(f"🏁 {message}", style=style)
        else:
            self.info(f"🏁 {message}")

    def log_file_processing(self, file_path: str, status: str) -> None:
        """파일 처리 상태를 로깅합니다."""
        file_name = Path(file_path).name
        message = f"파일 처리: {file_name} - {status}"

        if status == "시작":
            if self.console and RICH_AVAILABLE:
                self.console.print(f"📁 {message}", style="blue")
            else:
                self.info(f"📁 {message}")
        elif status == "완료":
            if self.console and RICH_AVAILABLE:
                self.console.print(f"✅ {message}", style="green")
            else:
                self.info(f"✅ {message}")
        elif status == "오류":
            if self.console and RICH_AVAILABLE:
                self.console.print(f"❌ {message}", style="red")
            else:
                self.error(f"❌ {message}")

    def log_summary(self, results: Dict[str, Any]) -> None:
        """검증 결과 요약을 로깅합니다."""
        if not self.console or not RICH_AVAILABLE:
            # 기본 출력
            self.info("=" * 50)
            self.info("검증 결과 요약")
            self.info("=" * 50)
            for key, value in results.items():
                self.info(f"{key}: {value}")
            return

        # Rich 테이블로 요약 표시
        table = Table(
            title="검증 결과 요약", show_header=True, header_style="bold magenta"
        )
        table.add_column("항목", style="cyan", no_wrap=True)
        table.add_column("값", style="green")

        for key, value in results.items():
            table.add_row(key, str(value))

        self.console.print(table)

    def log_config_info(self, config_path: str, config_summary: Dict[str, Any]) -> None:
        """설정 정보를 로깅합니다."""
        if self.console and RICH_AVAILABLE:
            panel_content = f"설정 파일: {config_path}\n"
            panel_content += f"인코딩: {config_summary.get('file_info', {}).get('encoding', 'N/A')}\n"
            panel_content += f"구분자: {config_summary.get('file_info', {}).get('delimiter', 'N/A')}\n"
            panel_content += (
                f"총 컬럼 수: {config_summary.get('columns', {}).get('total', 'N/A')}\n"
            )
            panel_content += (
                f"필수 컬럼: {config_summary.get('columns', {}).get('required', 'N/A')}"
            )

            panel = Panel(
                panel_content,
                title="[bold blue]설정 정보[/bold blue]",
                border_style="blue",
            )
            self.console.print(panel)
        else:
            self.info("설정 정보:")
            self.info(f"  설정 파일: {config_path}")
            self.info(
                f"  인코딩: {config_summary.get('file_info', {}).get('encoding', 'N/A')}"
            )
            self.info(
                f"  구분자: {config_summary.get('file_info', {}).get('delimiter', 'N/A')}"
            )
            self.info(
                f"  총 컬럼 수: {config_summary.get('columns', {}).get('total', 'N/A')}"
            )
            self.info(
                f"  필수 컬럼: {config_summary.get('columns', {}).get('required', 'N/A')}"
            )

    def log_error_details(self, errors: list) -> None:
        """오류 상세 정보를 로깅합니다."""
        if not errors:
            return

        if self.console and RICH_AVAILABLE:
            table = Table(
                title="발견된 오류", show_header=True, header_style="bold red"
            )
            table.add_column("행", style="cyan", width=6)
            table.add_column("컬럼", style="magenta", width=12)
            table.add_column("오류 유형", style="yellow", width=20)
            table.add_column("실제 값", style="red", width=15)
            table.add_column("메시지", style="white")

            for error in errors[:10]:  # 최대 10개만 표시
                table.add_row(
                    str(error.get("row_number", "")),
                    str(error.get("column_name", "")),
                    str(error.get("error_type", "")),
                    str(error.get("actual_value", "")),
                    str(error.get("message", "")),
                )

            if len(errors) > 10:
                table.add_row(
                    "...", "...", "...", "...", f"그 외 {len(errors) - 10}개 오류"
                )

            self.console.print(table)
        else:
            self.error("발견된 오류:")
            for i, error in enumerate(errors[:10], 1):
                self.error(
                    f"  {i}. 행 {error.get('row_number', '')}, 컬럼 {error.get('column_name', '')}: {error.get('message', '')}"
                )

            if len(errors) > 10:
                self.error(f"  ... 그 외 {len(errors) - 10}개 오류")

    def log_performance_info(
        self, file_name: str, rows: int, processing_time: float
    ) -> None:
        """성능 정보를 로깅합니다."""
        rows_per_second = rows / processing_time if processing_time > 0 else 0

        if self.console and RICH_AVAILABLE:
            performance_text = Text()
            performance_text.append(f"파일: {file_name}\n", style="cyan")
            performance_text.append(f"행 수: {rows:,}\n", style="green")
            performance_text.append(
                f"처리 시간: {processing_time:.2f}초\n", style="yellow"
            )
            performance_text.append(
                f"처리 속도: {rows_per_second:.0f} 행/초", style="magenta"
            )

            panel = Panel(
                performance_text,
                title="[bold green]성능 정보[/bold green]",
                border_style="green",
            )
            self.console.print(panel)
        else:
            self.info(
                f"성능 정보 - 파일: {file_name}, 행 수: {rows:,}, 처리 시간: {processing_time:.2f}초, 속도: {rows_per_second:.0f} 행/초"
            )

    def create_progress_bar(
        self, total: int, description: str = "처리 중..."
    ) -> "ProgressBar":
        """
        진행률 바를 생성합니다.

        Args:
            total: 전체 진행 단계 수
            description: 진행률 바 설명

        Returns:
            ProgressBar: 진행률 바 객체
        """
        return ProgressBar(self, total, description)

    def close(self) -> None:
        """로거를 종료합니다."""
        if self.progress:
            self.progress.stop()
            self.progress = None
            self.task_id = None


class ProgressBar:
    """진행률 바를 관리하는 클래스"""

    def __init__(self, logger: Logger, total: int, description: str = "처리 중..."):
        """
        ProgressBar 초기화

        Args:
            logger: 로거 인스턴스
            total: 전체 진행 단계 수
            description: 진행률 바 설명
        """
        self.logger = logger
        self.total = total
        self.description = description
        self.current = 0
        self.start_time = datetime.now()

        if logger.console and RICH_AVAILABLE:
            self.progress = Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeElapsedColumn(),
                console=logger.console,
            )
            self.progress.start()
            self.task_id = self.progress.add_task(description, total=total)
        else:
            self.progress = None
            self.task_id = None

    def update(self, increment: int = 1, description: Optional[str] = None) -> None:
        """
        진행률을 업데이트합니다.

        Args:
            increment: 증가할 진행 단계 수
            description: 새로운 설명 (선택적)
        """
        self.current += increment

        if self.progress and self.task_id is not None:
            desc = description or self.description
            self.progress.update(self.task_id, completed=self.current, description=desc)
        else:
            # Rich가 없는 경우 기본 출력
            percentage = (self.current / self.total * 100) if self.total > 0 else 0
            desc = description or self.description
            print(
                f"\r{desc}: {self.current}/{self.total} ({percentage:.1f}%)",
                end="",
                flush=True,
            )

    def finish(self, description: str = "완료") -> None:
        """진행률 바를 완료합니다."""
        if self.progress:
            self.progress.update(
                self.task_id, completed=self.total, description=description
            )
            self.progress.stop()
        else:
            print(f"\r{description}: {self.total}/{self.total} (100.0%)")
            print()  # 줄바꿈

        # 처리 시간 로깅
        processing_time = (datetime.now() - self.start_time).total_seconds()
        self.logger.debug(f"진행률 바 완료 - 처리 시간: {processing_time:.2f}초")

    def __enter__(self):
        """컨텍스트 매니저 진입"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """컨텍스트 매니저 종료"""
        self.finish()
