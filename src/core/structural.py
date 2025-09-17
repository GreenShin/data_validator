"""
Structural validation for CSV files.

이 모듈은 CSV 파일의 구조정확성을 검증하는 기능을 제공합니다.
"""

import os
import csv
import chardet
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path

from ..models import FileInfo, ValidationError, ErrorType, ErrorRegistry
from ..utils import FileHandler


class StructuralValidator:
    """CSV 파일의 구조정확성을 검증하는 클래스"""

    def __init__(self):
        """StructuralValidator 초기화"""
        self.file_handler = FileHandler()
        self.errors: List[ValidationError] = []

    def validate_csv_format(self, file_path: str, config: FileInfo) -> bool:
        """
        CSV 파일의 기본 포맷을 검증합니다.

        Args:
            file_path: 검증할 CSV 파일 경로
            config: 파일 정보 설정

        Returns:
            bool: CSV 포맷이 유효한지 여부
        """
        self.errors.clear()

        try:
            # 파일 존재 여부 확인
            if not self.file_handler.validate_file_exists(file_path):
                error = ValidationError(
                    row_number=1,
                    column_name="file",
                    error_type=ErrorType.SYSTEM_FILE_NOT_FOUND.value,
                    actual_value=file_path,
                    expected_value="존재하는 파일",
                    message=f"파일을 찾을 수 없습니다: {file_path}",
                )
                self.errors.append(error)
                return False

            # 파일 읽기 권한 확인
            if not self.file_handler.validate_file_readable(file_path):
                error = ValidationError(
                    row_number=1,
                    column_name="file",
                    error_type=ErrorType.SYSTEM_PERMISSION_DENIED.value,
                    actual_value=file_path,
                    expected_value="읽기 가능한 파일",
                    message=f"파일 읽기 권한이 없습니다: {file_path}",
                )
                self.errors.append(error)
                return False

            # 파일이 비어있는지 확인
            if os.path.getsize(file_path) == 0:
                error = ValidationError(
                    row_number=1,
                    column_name="file",
                    error_type=ErrorType.STRUCTURAL_EMPTY_FILE.value,
                    actual_value="0 bytes",
                    expected_value="비어있지 않은 파일",
                    message="파일이 비어있습니다",
                )
                self.errors.append(error)
                return False

            # CSV 구조 검증
            return self._validate_csv_structure(file_path, config)

        except Exception as e:
            error = ValidationError(
                row_number=1,
                column_name="file",
                error_type=ErrorType.SYSTEM_IO_ERROR.value,
                actual_value=str(e),
                expected_value="정상적인 파일",
                message=f"파일 처리 중 오류 발생: {e}",
            )
            self.errors.append(error)
            return False

    def validate_row_count(self, file_path: str, expected_rows: int) -> bool:
        """
        CSV 파일의 행 수를 검증합니다.

        Args:
            file_path: 검증할 CSV 파일 경로
            expected_rows: 예상 행 수

        Returns:
            bool: 행 수가 예상과 일치하는지 여부
        """
        try:
            # 파일 정보 가져오기
            file_info = self.file_handler.get_file_info(file_path)
            actual_rows = file_info.get("estimated_rows", 0)

            # 정확한 행 수 계산
            actual_rows = self._count_actual_rows(
                file_path, file_info.get("encoding", "utf-8")
            )

            if actual_rows != expected_rows:
                error = ValidationError(
                    row_number=1,
                    column_name="file",
                    error_type=ErrorType.STRUCTURAL_ROW_COUNT_MISMATCH.value,
                    actual_value=actual_rows,
                    expected_value=expected_rows,
                    message=f"예상 행 수({expected_rows})와 실제 행 수({actual_rows})가 일치하지 않습니다",
                )
                self.errors.append(error)
                return False

            return True

        except Exception as e:
            error = ValidationError(
                row_number=1,
                column_name="file",
                error_type=ErrorType.SYSTEM_IO_ERROR.value,
                actual_value=str(e),
                expected_value="정상적인 파일",
                message=f"행 수 계산 중 오류 발생: {e}",
            )
            self.errors.append(error)
            return False

    def validate_encoding(self, file_path: str, expected_encoding: str) -> bool:
        """
        CSV 파일의 인코딩을 검증합니다.

        Args:
            file_path: 검증할 CSV 파일 경로
            expected_encoding: 예상 인코딩

        Returns:
            bool: 인코딩이 예상과 일치하거나 호환되는지 여부
        """
        try:
            detected_encoding = self.file_handler.detect_encoding(file_path)

            # 인코딩 정규화 (대소문자 통일)
            detected_encoding = detected_encoding.lower()
            expected_encoding = expected_encoding.lower()

            # 인코딩 호환성 검사
            if self._is_encoding_compatible(detected_encoding, expected_encoding):
                return True

            # 호환되지 않는 경우 오류 추가
            error = ValidationError(
                row_number=1,
                column_name="file",
                error_type=ErrorType.STRUCTURAL_INVALID_ENCODING.value,
                actual_value=detected_encoding,
                expected_value=expected_encoding,
                message=f"예상 인코딩({expected_encoding})과 감지된 인코딩({detected_encoding})이 호환되지 않습니다",
            )
            self.errors.append(error)
            return False

        except Exception as e:
            error = ValidationError(
                row_number=1,
                column_name="file",
                error_type=ErrorType.SYSTEM_IO_ERROR.value,
                actual_value=str(e),
                expected_value="정상적인 인코딩",
                message=f"인코딩 검증 중 오류 발생: {e}",
            )
            self.errors.append(error)
            return False

    def _is_encoding_compatible(self, detected: str, expected: str) -> bool:
        """
        두 인코딩이 호환되는지 확인합니다.

        Args:
            detected: 감지된 인코딩
            expected: 예상 인코딩

        Returns:
            bool: 호환되는지 여부
        """
        # 정확히 일치하는 경우
        if detected == expected:
            return True

        # UTF-8 호환성 검사
        if expected == "utf-8":
            # UTF-8은 ASCII를 포함하므로 ASCII 파일도 UTF-8로 읽을 수 있음
            if detected == "ascii":
                return True
            # UTF-8은 다른 UTF-8 변형들도 포함
            if detected in ["utf-8", "utf8"]:
                return True

        # ASCII 호환성 검사
        if expected == "ascii":
            # ASCII는 UTF-8의 부분집합이므로 UTF-8 파일이 ASCII 범위 내에 있으면 호환
            if detected in ["utf-8", "utf8"]:
                return True

        # CP949와 EUC-KR 호환성
        if expected == "cp949" and detected == "euc-kr":
            return True
        if expected == "euc-kr" and detected == "cp949":
            return True

        # Latin-1 호환성
        if expected == "latin-1" and detected in ["iso-8859-1", "latin1"]:
            return True
        if detected == "latin-1" and expected in ["iso-8859-1", "latin1"]:
            return True

        return False

    def validate_delimiter(self, file_path: str, expected_delimiter: str) -> bool:
        """
        CSV 파일의 구분자를 검증합니다.

        Args:
            file_path: 검증할 CSV 파일 경로
            expected_delimiter: 예상 구분자

        Returns:
            bool: 구분자가 예상과 일치하는지 여부
        """
        try:
            file_info = self.file_handler.get_file_info(file_path)
            detected_delimiter = file_info.get("delimiter", ",")

            if detected_delimiter != expected_delimiter:
                error = ValidationError(
                    row_number=1,
                    column_name="file",
                    error_type=ErrorType.STRUCTURAL_INVALID_FORMAT.value,
                    actual_value=detected_delimiter,
                    expected_value=expected_delimiter,
                    message=f"예상 구분자('{expected_delimiter}')와 감지된 구분자('{detected_delimiter}')가 일치하지 않습니다",
                )
                self.errors.append(error)
                return False

            return True

        except Exception as e:
            error = ValidationError(
                row_number=1,
                column_name="file",
                error_type=ErrorType.SYSTEM_IO_ERROR.value,
                actual_value=str(e),
                expected_value="정상적인 구분자",
                message=f"구분자 검증 중 오류 발생: {e}",
            )
            self.errors.append(error)
            return False

    def validate_header(
        self, file_path: str, config: FileInfo, expected_columns: List[str]
    ) -> bool:
        """
        CSV 파일의 헤더를 검증합니다.

        Args:
            file_path: 검증할 CSV 파일 경로
            config: 파일 정보 설정
            expected_columns: 예상 컬럼 목록

        Returns:
            bool: 헤더가 예상과 일치하는지 여부
        """
        try:
            if not config.has_header:
                return True  # 헤더가 없어야 하는 경우는 검증하지 않음

            # 첫 번째 행 읽기
            with open(file_path, "r", encoding=config.encoding) as f:
                reader = csv.reader(f, delimiter=config.delimiter)
                try:
                    header_row = next(reader)
                except StopIteration:
                    error = ValidationError(
                        row_number=1,
                        column_name="header",
                        error_type=ErrorType.STRUCTURAL_EMPTY_FILE.value,
                        actual_value="빈 파일",
                        expected_value="헤더가 포함된 파일",
                        message="파일이 비어있어 헤더를 읽을 수 없습니다",
                    )
                    self.errors.append(error)
                    return False

            # 컬럼 수 확인
            if len(header_row) != len(expected_columns):
                if len(header_row) < len(expected_columns):
                    # 실제 컬럼 수가 설정된 컬럼 수보다 적으면 오류
                    error = ValidationError(
                        row_number=1,
                        column_name="header",
                        error_type=ErrorType.STRUCTURAL_INVALID_FORMAT.value,
                        actual_value=f"{len(header_row)}개 컬럼",
                        expected_value=f"{len(expected_columns)}개 컬럼",
                        message=f"예상 컬럼 수({len(expected_columns)})보다 실제 컬럼 수({len(header_row)})가 적습니다",
                    )
                    self.errors.append(error)
                    return False
                else:
                    # 실제 컬럼 수가 설정된 컬럼 수보다 많으면 경고만 표시
                    from ..utils.logger import Logger
                    logger = Logger()
                    logger.warning(f"실제 컬럼 수({len(header_row)})가 설정된 컬럼 수({len(expected_columns)})보다 많습니다. 추가 컬럼은 무시됩니다.")

            # 컬럼명 확인
            for i, (actual, expected) in enumerate(zip(header_row, expected_columns)):
                if actual.strip() != expected.strip():
                    error = ValidationError(
                        row_number=1,
                        column_name=f"column_{i+1}",
                        error_type=ErrorType.STRUCTURAL_INVALID_FORMAT.value,
                        actual_value=actual,
                        expected_value=expected,
                        message=f"컬럼 {i+1}: 예상 컬럼명('{expected}')과 실제 컬럼명('{actual}')이 일치하지 않습니다",
                    )
                    self.errors.append(error)
                    return False

            return True

        except Exception as e:
            error = ValidationError(
                row_number=1,
                column_name="header",
                error_type=ErrorType.SYSTEM_IO_ERROR.value,
                actual_value=str(e),
                expected_value="정상적인 헤더",
                message=f"헤더 검증 중 오류 발생: {e}",
            )
            self.errors.append(error)
            return False

    def validate_consistency(self, file_path: str, config: FileInfo) -> bool:
        """
        CSV 파일의 일관성을 검증합니다 (모든 행의 컬럼 수가 동일한지 확인).

        Args:
            file_path: 검증할 CSV 파일 경로
            config: 파일 정보 설정

        Returns:
            bool: 파일이 일관성 있는지 여부
        """
        try:
            with open(file_path, "r", encoding=config.encoding) as f:
                reader = csv.reader(f, delimiter=config.delimiter)

                # 첫 번째 행 읽기 (헤더 또는 데이터)
                try:
                    first_row = next(reader)
                    expected_columns = len(first_row)
                except StopIteration:
                    error = ValidationError(
                        row_number=1,
                        column_name="file",
                        error_type=ErrorType.STRUCTURAL_EMPTY_FILE.value,
                        actual_value="빈 파일",
                        expected_value="데이터가 포함된 파일",
                        message="파일이 비어있습니다",
                    )
                    self.errors.append(error)
                    return False

                # 나머지 행들 검증
                row_number = 2  # 헤더가 있다면 2부터, 없다면 1부터
                for row in reader:
                    if len(row) != expected_columns:
                        error = ValidationError(
                            row_number=row_number,
                            column_name="row",
                            error_type=ErrorType.STRUCTURAL_INVALID_FORMAT.value,
                            actual_value=f"{len(row)}개 컬럼",
                            expected_value=f"{expected_columns}개 컬럼",
                            message=f"행 {row_number}: 컬럼 수가 일치하지 않습니다 (예상: {expected_columns}, 실제: {len(row)})",
                        )
                        self.errors.append(error)
                        return False
                    row_number += 1

            return True

        except Exception as e:
            error = ValidationError(
                row_number=1,
                column_name="file",
                error_type=ErrorType.SYSTEM_IO_ERROR.value,
                actual_value=str(e),
                expected_value="정상적인 파일",
                message=f"일관성 검증 중 오류 발생: {e}",
            )
            self.errors.append(error)
            return False

    def validate_all(
        self,
        file_path: str,
        config: FileInfo,
        expected_columns: Optional[List[str]] = None,
    ) -> Tuple[bool, List[ValidationError]]:
        """
        모든 구조정확성 검증을 수행합니다.

        Args:
            file_path: 검증할 CSV 파일 경로
            config: 파일 정보 설정
            expected_columns: 예상 컬럼 목록 (선택적)

        Returns:
            Tuple[bool, List[ValidationError]]: 검증 결과와 오류 목록
        """
        self.errors.clear()

        # 1. CSV 포맷 검증
        format_valid = self.validate_csv_format(file_path, config)

        # 2. 인코딩 검증
        encoding_valid = self.validate_encoding(file_path, config.encoding)

        # 3. 구분자 검증
        delimiter_valid = self.validate_delimiter(file_path, config.delimiter)

        # 4. 일관성 검증
        consistency_valid = self.validate_consistency(file_path, config)

        # 5. 헤더 검증 (예상 컬럼이 제공된 경우)
        header_valid = True
        if expected_columns and config.has_header:
            header_valid = self.validate_header(file_path, config, expected_columns)

        # 6. 행 수 검증 (예상 행 수가 설정된 경우)
        row_count_valid = True
        if config.expected_rows is not None:
            row_count_valid = self.validate_row_count(file_path, config.expected_rows)

        # 전체 결과
        all_valid = (
            format_valid
            and encoding_valid
            and delimiter_valid
            and consistency_valid
            and header_valid
            and row_count_valid
        )

        return all_valid, self.errors.copy()

    def _validate_csv_structure(self, file_path: str, config: FileInfo) -> bool:
        """
        CSV 파일의 기본 구조를 검증합니다.

        Args:
            file_path: 검증할 CSV 파일 경로
            config: 파일 정보 설정

        Returns:
            bool: CSV 구조가 유효한지 여부
        """
        try:
            # CSV 파일을 읽어서 기본 구조 확인
            with open(file_path, "r", encoding=config.encoding) as f:
                reader = csv.reader(f, delimiter=config.delimiter)

                # 최소한 하나의 행이 있는지 확인
                try:
                    first_row = next(reader)
                    if not first_row:
                        error = ValidationError(
                            row_number=1,
                            column_name="file",
                            error_type=ErrorType.STRUCTURAL_EMPTY_FILE.value,
                            actual_value="빈 행",
                            expected_value="데이터가 포함된 행",
                            message="첫 번째 행이 비어있습니다",
                        )
                        self.errors.append(error)
                        return False
                except StopIteration:
                    error = ValidationError(
                        row_number=1,
                        column_name="file",
                        error_type=ErrorType.STRUCTURAL_EMPTY_FILE.value,
                        actual_value="빈 파일",
                        expected_value="데이터가 포함된 파일",
                        message="파일이 비어있습니다",
                    )
                    self.errors.append(error)
                    return False

            return True

        except UnicodeDecodeError as e:
            error = ValidationError(
                row_number=1,
                column_name="file",
                error_type=ErrorType.STRUCTURAL_INVALID_ENCODING.value,
                actual_value=config.encoding,
                expected_value="올바른 인코딩",
                message=f"인코딩 오류: {e}",
            )
            self.errors.append(error)
            return False
        except Exception as e:
            error = ValidationError(
                row_number=1,
                column_name="file",
                error_type=ErrorType.STRUCTURAL_INVALID_FORMAT.value,
                actual_value=str(e),
                expected_value="올바른 CSV 형식",
                message=f"CSV 구조 오류: {e}",
            )
            self.errors.append(error)
            return False

    def _count_actual_rows(self, file_path: str, encoding: str) -> int:
        """
        CSV 파일의 실제 행 수를 계산합니다.

        Args:
            file_path: 계산할 CSV 파일 경로
            encoding: 파일 인코딩

        Returns:
            int: 실제 데이터 행 수 (헤더 제외)
        """
        try:
            with open(file_path, "r", encoding=encoding) as f:
                reader = csv.reader(f)
                total_rows = sum(1 for _ in reader)
                
                # 헤더가 있다고 가정하고 1을 빼서 데이터 행 수만 반환
                # 실제로는 config에서 has_header 정보를 확인해야 하지만,
                # 여기서는 일반적인 경우를 처리
                return max(0, total_rows - 1)
        except Exception:
            return 0

    def get_errors(self) -> List[ValidationError]:
        """발견된 오류 목록을 반환합니다."""
        return self.errors.copy()

    def clear_errors(self) -> None:
        """오류 목록을 초기화합니다."""
        self.errors.clear()
