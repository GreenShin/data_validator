"""
Core validation engine for CSV files.

이 모듈은 전체 검증 워크플로우를 관리하는 핵심 엔진입니다.
"""

import os
import time
from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from ..models import ValidationResult, ValidationError, ValidationConfig, FileInfo, FileType
from ..core.structural import StructuralValidator
from ..core.format import FormatValidator
from ..core.config import ConfigManager
from ..utils.file_handler import FileHandler
from ..utils.formatter import ReportFormatter
from ..utils.logger import Logger
from ..distribution.analyzer import DistributionAnalyzer
from ..distribution.config import DistributionConfig


class DataValidator:
    """데이터 파일 검증을 담당하는 핵심 클래스 (CSV, JSON, JSONL 지원)"""

    def __init__(
        self, config_path: str, verbose: bool = False, log_file: Optional[str] = None
    ):
        """
        DataValidator 초기화

        Args:
            config_path: YAML 설정 파일 경로
            verbose: 상세 로그 출력 여부
            log_file: 로그 파일 경로 (선택적)
        """
        self.config_path = config_path
        self.verbose = verbose
        self.log_file = log_file

        # 컴포넌트 초기화
        self.config_manager = ConfigManager()
        self.structural_validator = StructuralValidator()
        self.format_validator = FormatValidator()
        self.file_handler = FileHandler()
        self.formatter = ReportFormatter()
        self.logger = Logger(verbose=verbose, log_file=log_file)

        # 설정 로드
        self.config: Optional[ValidationConfig] = None
        self._load_config()
        
        # 분포 분석 관련
        self.distribution_analyzer: Optional[DistributionAnalyzer] = None
        self.distribution_enabled: bool = False

    def _load_config(self) -> None:
        """설정 파일을 로드합니다."""
        try:
            self.config = self.config_manager.load_config(self.config_path)
            self.logger.info(f"설정 파일 로드 완료: {self.config_path}")

            if self.verbose:
                config_summary = self.config_manager.get_config_summary()
                self.logger.log_config_info(self.config_path, config_summary)

        except Exception as e:
            self.logger.log_error(e, "설정 파일 로드")
            raise
    
    def enable_distribution_analysis(self) -> None:
        """분포 분석을 활성화합니다."""
        try:
            # 설정에서 분포 분석 설정 확인
            if hasattr(self.config, 'distribution_analysis') and self.config.distribution_analysis:
                from ..distribution.config import DistributionConfig
                from ..distribution.analyzer import DistributionAnalyzer
                
                # DistributionConfig 생성
                dist_config = DistributionConfig(
                    enabled=True,
                    columns=self.config.distribution_analysis.get('columns', [])
                )
                
                # DistributionAnalyzer 초기화
                self.distribution_analyzer = DistributionAnalyzer(dist_config)
                self.distribution_enabled = True
                
                self.logger.log_success("분포 분석이 활성화되었습니다")
            else:
                self.logger.log_warning("설정 파일에 distribution_analysis 섹션이 없습니다")
                self.distribution_enabled = False
                
        except Exception as e:
            self.logger.log_error(e, "분포 분석 활성화 실패")
            self.distribution_enabled = False

    def validate_file(self, file_path: str) -> ValidationResult:
        """
        단일 파일을 검증합니다 (CSV, JSON, JSONL 지원).

        Args:
            file_path: 검증할 파일 경로

        Returns:
            ValidationResult: 검증 결과
        """
        start_time = time.time()
        file_name = Path(file_path).name

        self.logger.log_validation_start(file_name, 0)  # 행 수는 나중에 업데이트

        try:
            # 1. 파일 존재 여부 확인
            if not self.file_handler.validate_file_exists(file_path):
                raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")

            # 2. 파일 정보 수집
            file_info = self.file_handler.get_file_info(file_path)
            
            # 파일 타입 감지 및 설정 업데이트
            detected_file_type = self.file_handler.detect_file_type(file_path)
            self.config.file_info.file_type = detected_file_type
            
            total_rows = self.file_handler.count_rows_by_type(file_path, self.config.file_info)
            total_columns = len(self.config.columns)

            self.logger.log_validation_start(file_name, total_rows)

            # 3. 구조정확성 검증
            structural_valid, structural_errors = self._validate_structural(file_path)

            # 4. 형식정확성 검증
            format_valid, format_errors = self._validate_format(file_path)

            # 5. 분포 분석 (활성화된 경우)
            distribution_results = None
            if self.distribution_enabled:
                distribution_results = self.analyze_distribution(file_path)
                if distribution_results:
                    self.logger.log_success(f"분포 분석 완료: {len(distribution_results)}개 컬럼")

            # 6. 결과 통합
            all_errors = structural_errors + format_errors
            processing_time = time.time() - start_time

            result = ValidationResult(
                file_name=file_name,
                total_rows=total_rows,
                total_columns=total_columns,
                structural_valid=structural_valid,
                format_valid=format_valid,
                errors=all_errors,
                processing_time=processing_time,
                distribution_analysis=distribution_results,
                timestamp=datetime.now(),
            )

            # 6. 결과 로깅
            self.logger.log_validation_complete(
                file_name, len(all_errors), processing_time
            )

            if self.verbose and all_errors:
                self.logger.log_error_details([error.dict() for error in all_errors])

            if self.verbose:
                self.logger.log_performance_info(file_name, total_rows, processing_time)

            return result

        except Exception as e:
            processing_time = time.time() - start_time
            self.logger.log_error(e, f"파일 검증 중 오류 발생: {file_name}")

            # 오류 발생 시에도 결과 객체 생성
            return ValidationResult(
                file_name=file_name,
                total_rows=0,
                total_columns=0,
                structural_valid=False,
                format_valid=False,
                errors=[
                    ValidationError(
                        row_number=1,
                        column_name="system",
                        error_type="SYSTEM_ERROR",
                        actual_value=str(e),
                        expected_value="정상적인 파일",
                        message=f"검증 중 오류 발생: {e}",
                    )
                ],
                processing_time=processing_time,
                timestamp=datetime.now(),
            )

    def validate_folder(
        self, folder_path: str, output_dir: Optional[str] = None
    ) -> List[ValidationResult]:
        """
        폴더 내 모든 지원되는 파일을 검증합니다 (CSV, JSON, JSONL).

        Args:
            folder_path: 검증할 폴더 경로
            output_dir: 결과 파일 저장 디렉토리 (선택적)

        Returns:
            List[ValidationResult]: 검증 결과 목록
        """
        results = []

        try:
            # 지원되는 모든 파일 찾기
            supported_files = self.file_handler.find_supported_files(folder_path, recursive=True)

            if not supported_files:
                self.logger.warning(f"지원되는 파일을 찾을 수 없습니다: {folder_path}")
                return results

            # 파일 타입별로 분류
            csv_files = [f for f in supported_files if self.file_handler.is_csv_file(f)]
            json_files = [f for f in supported_files if self.file_handler.is_json_file(f)]
            jsonl_files = [f for f in supported_files if self.file_handler.is_jsonl_file(f)]

            self.logger.info(f"총 {len(supported_files)}개의 파일을 발견했습니다:")
            self.logger.info(f"  - CSV: {len(csv_files)}개")
            self.logger.info(f"  - JSON: {len(json_files)}개")
            self.logger.info(f"  - JSONL: {len(jsonl_files)}개")

            # 각 파일 검증
            for i, file_path in enumerate(supported_files, 1):
                self.logger.info(
                    f"파일 {i}/{len(supported_files)} 검증 중: {Path(file_path).name}"
                )

                try:
                    result = self.validate_file(file_path)
                    results.append(result)

                    # 결과 파일 저장 (output_dir이 지정된 경우)
                    if output_dir:
                        self._save_result_file(result, output_dir)

                except Exception as e:
                    self.logger.log_error(e, f"파일 검증 실패: {Path(file_path).name}")
                    continue

            # 전체 결과 요약
            self._log_summary(results)

            return results

        except Exception as e:
            self.logger.log_error(e, "폴더 검증 중 오류 발생")
            return results

    def _validate_structural(
        self, file_path: str
    ) -> Tuple[bool, List[ValidationError]]:
        """
        구조정확성 검증을 수행합니다.

        Args:
            file_path: 검증할 파일 경로

        Returns:
            Tuple[bool, List[ValidationError]]: 검증 결과와 오류 목록
        """
        try:
            file_type = self.config.file_info.file_type
            
            if file_type == FileType.CSV:
                # CSV 파일의 경우 기존 로직 사용
                expected_columns = [rule.name for rule in self.config.columns]
                return self.structural_validator.validate_all(
                    file_path, self.config.file_info, expected_columns
                )
            elif file_type in [FileType.JSON, FileType.JSONL]:
                # JSON/JSONL 파일의 경우 JSON 파서 사용
                data = self.file_handler.read_file_by_type(file_path, self.config.file_info)
                return self.file_handler.json_parser.validate_json_structure(
                    data, self.config.columns
                )
            else:
                raise ValueError(f"지원되지 않는 파일 타입: {file_type}")
                
        except Exception as e:
            self.logger.log_error(e, "구조정확성 검증")
            return False, [
                ValidationError(
                    row_number=1,
                    column_name="system",
                    error_type="SYSTEM_ERROR",
                    actual_value=str(e),
                    expected_value="정상적인 구조",
                    message=f"구조정확성 검증 중 오류: {e}",
                )
            ]

    def _validate_format(self, file_path: str) -> Tuple[bool, List[ValidationError]]:
        """
        형식정확성 검증을 수행합니다.

        Args:
            file_path: 검증할 파일 경로

        Returns:
            Tuple[bool, List[ValidationError]]: 검증 결과와 오류 목록
        """
        try:
            file_type = self.config.file_info.file_type
            
            if file_type == FileType.CSV:
                # CSV 파일의 경우 기존 로직 사용
                format_errors = []

                # CSV 파일을 청크 단위로 읽어서 검증
                # 파일 크기에 따라 동적으로 청크 크기 조정
                file_size = os.path.getsize(file_path)
                if file_size < 1024 * 1024:  # 1MB 미만
                    chunk_size = 5000
                elif file_size < 10 * 1024 * 1024:  # 10MB 미만
                    chunk_size = 2000
                else:  # 10MB 이상
                    chunk_size = 1000

                row_offset = 1 if self.config.file_info.has_header else 0

                for chunk in self.file_handler.read_csv_streaming(
                    file_path, self.config.file_info, chunk_size
                ):
                    for chunk_row_idx, (_, row) in enumerate(chunk.iterrows()):
                        actual_row_number = chunk_row_idx + row_offset + 1

                        # 각 컬럼 검증
                        for column_name, value in row.items():
                            rule = self.config.get_column_rule(column_name)
                            if rule:
                                # 형식정확성 검증 수행
                                self.format_validator.validate_all(value, rule)

                                # 오류가 있으면 행 번호 설정하여 추가
                                for error in self.format_validator.get_errors():
                                    error.row_number = actual_row_number
                                    format_errors.append(error)

                                # 오류 목록 초기화
                                self.format_validator.clear_errors()

                return len(format_errors) == 0, format_errors
                
            elif file_type in [FileType.JSON, FileType.JSONL]:
                # JSON/JSONL 파일의 경우 JSON 파서 사용
                data = self.file_handler.read_file_by_type(file_path, self.config.file_info)
                return self.file_handler.json_parser.validate_json_format(
                    data, self.config.columns
                )
            else:
                raise ValueError(f"지원되지 않는 파일 타입: {file_type}")

        except Exception as e:
            self.logger.log_error(e, "형식정확성 검증")
            return False, [
                ValidationError(
                    row_number=1,
                    column_name="system",
                    error_type="SYSTEM_ERROR",
                    actual_value=str(e),
                    expected_value="정상적인 형식",
                    message=f"형식정확성 검증 중 오류: {e}",
                )
            ]

    def _save_result_file(self, result: ValidationResult, output_dir: str) -> None:
        """
        검증 결과를 파일로 저장합니다.

        Args:
            result: 저장할 검증 결과
            output_dir: 출력 디렉토리
        """
        try:
            # 출력 디렉토리 생성
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)

            # 파일명 생성 (타임스탬프 포함)
            timestamp = result.timestamp.strftime("%Y%m%d_%H%M%S")
            base_name = Path(result.file_name).stem
            output_file = output_path / f"{base_name}_{timestamp}"

            # Markdown 리포트 생성 및 저장
            markdown_report = self.formatter.generate_markdown_report(result)
            markdown_path = self.formatter.save_report(
                markdown_report, str(output_file), "markdown"
            )

            # HTML 리포트 생성 및 저장
            html_report = self.formatter.generate_html_report(result)
            html_path = self.formatter.save_report(
                html_report, str(output_file), "html"
            )

            # JSON 리포트 생성 및 저장
            json_report = self.formatter.generate_json_report(result)
            json_path = self.formatter.save_report(
                json_report, str(output_file), "json"
            )

            if self.verbose:
                self.logger.info(f"결과 파일 저장 완료:")
                self.logger.info(f"  - Markdown: {markdown_path}")
                self.logger.info(f"  - HTML: {html_path}")
                self.logger.info(f"  - JSON: {json_path}")

        except Exception as e:
            self.logger.log_error(e, "결과 파일 저장")

    def _log_summary(self, results: List[ValidationResult]) -> None:
        """
        검증 결과 요약을 로깅합니다.

        Args:
            results: 검증 결과 목록
        """
        if not results:
            return

        total_files = len(results)
        total_rows = sum(result.total_rows for result in results)
        total_errors = sum(len(result.errors) for result in results)
        total_time = sum(result.processing_time for result in results)

        successful_files = sum(
            1 for result in results if result.structural_valid and result.format_valid
        )
        failed_files = total_files - successful_files

        summary = {
            "총 파일 수": total_files,
            "성공한 파일": successful_files,
            "실패한 파일": failed_files,
            "총 행 수": f"{total_rows:,}",
            "총 오류 수": total_errors,
            "총 처리 시간": f"{total_time:.2f}초",
            "평균 처리 속도": (
                f"{total_rows/total_time:.0f} 행/초" if total_time > 0 else "0 행/초"
            ),
        }

        self.logger.log_summary(summary)

    def get_config_summary(self) -> Dict[str, Any]:
        """
        현재 설정 요약을 반환합니다.

        Returns:
            Dict[str, Any]: 설정 요약 정보
        """
        return self.config_manager.get_config_summary()

    def reload_config(self) -> None:
        """설정 파일을 다시 로드합니다."""
        try:
            self.config = self.config_manager.reload_config()
            self.logger.info("설정 파일이 다시 로드되었습니다")
        except Exception as e:
            self.logger.log_error(e, "설정 파일 다시 로드")
            raise

    def create_sample_config(self, output_path: str) -> None:
        """
        샘플 설정 파일을 생성합니다.

        Args:
            output_path: 출력 파일 경로
        """
        try:
            self.config_manager.create_sample_config(output_path)
            self.logger.log_success(f"샘플 설정 파일이 생성되었습니다: {output_path}")
        except Exception as e:
            self.logger.log_error(e, "샘플 설정 파일 생성")
            raise

    def validate_config(self) -> bool:
        """
        현재 설정의 유효성을 검사합니다.

        Returns:
            bool: 설정이 유효한지 여부
        """
        try:
            is_valid = self.config_manager.validate_config(self.config)
            if is_valid:
                self.logger.log_success("설정 검증 통과")
            else:
                self.logger.warning("설정 검증 실패")
            return is_valid
        except Exception as e:
            self.logger.log_error(e, "설정 검증")
            return False

    def enable_distribution_analysis(self) -> None:
        """
        분포 분석을 활성화합니다.
        
        설정 파일에서 distribution_analysis 섹션을 찾아 DistributionAnalyzer를 초기화합니다.
        """
        try:
            # 설정 파일에서 분포 분석 설정 로드
            import yaml
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config_data = yaml.safe_load(f)
            
            distribution_config_data = config_data.get('distribution_analysis')
            if not distribution_config_data:
                self.logger.warning("설정 파일에 distribution_analysis 섹션이 없습니다.")
                return
            
            # DistributionConfig 생성
            distribution_config = DistributionConfig(**distribution_config_data)
            
            # DistributionAnalyzer 초기화
            self.distribution_analyzer = DistributionAnalyzer(distribution_config)
            self.distribution_enabled = True
            
            self.logger.log_success("분포 분석이 활성화되었습니다.")
            
        except Exception as e:
            self.logger.log_error(e, "분포 분석 활성화")
            self.distribution_enabled = False
    
    def analyze_distribution(self, file_path: str) -> Optional[Dict[str, Any]]:
        """
        파일의 컬럼 분포를 분석합니다.
        
        Args:
            file_path: 분석할 파일 경로
            
        Returns:
            Dict[str, Any]: 분포 분석 결과 또는 None
        """
        if not self.distribution_enabled or not self.distribution_analyzer:
            return None
        
        try:
            # CSV 파일만 지원 (현재)
            if not file_path.lower().endswith('.csv'):
                self.logger.warning(f"분포 분석은 CSV 파일만 지원됩니다: {file_path}")
                return None
            
            # CSV 파일 읽기
            import pandas as pd
            df = pd.read_csv(file_path)
            
            # 분포 분석 결과 저장
            distribution_results = {}
            
            # 설정된 컬럼들에 대해 분포 분석 수행
            for column_config in self.distribution_analyzer.config.columns:
                column_name = column_config.name
                if column_name in df.columns:
                    column_data = df[column_name].tolist()
                    result = self.distribution_analyzer.analyze_column(column_name, column_data)
                    distribution_results[column_name] = result
                else:
                    self.logger.warning(f"컬럼 '{column_name}'을 찾을 수 없습니다.")
            
            return distribution_results
            
        except Exception as e:
            self.logger.log_error(e, f"분포 분석: {file_path}")
            return None

    def close(self) -> None:
        """리소스를 정리합니다."""
        self.logger.close()
