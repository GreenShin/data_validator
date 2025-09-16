"""
Error handling models and utilities for CSV validation.

이 모듈은 CSV 검증 과정에서 발생하는 오류를 처리하고 분류하는 기능을 제공합니다.
"""

from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field


class ErrorType(str, Enum):
    """검증 오류 유형 열거형"""

    # 구조정확성 오류
    STRUCTURAL_INVALID_FORMAT = "structural_invalid_format"
    STRUCTURAL_INVALID_ENCODING = "structural_invalid_encoding"
    STRUCTURAL_INVALID_DELIMITER = "structural_invalid_delimiter"
    STRUCTURAL_ROW_COUNT_MISMATCH = "structural_row_count_mismatch"
    STRUCTURAL_MISSING_HEADER = "structural_missing_header"
    STRUCTURAL_EMPTY_FILE = "structural_empty_file"

    # 형식정확성 오류
    FORMAT_INVALID_TYPE = "format_invalid_type"
    FORMAT_OUT_OF_RANGE = "format_out_of_range"
    FORMAT_INVALID_LENGTH = "format_invalid_length"
    FORMAT_INVALID_CATEGORY = "format_invalid_category"
    FORMAT_INVALID_PATTERN = "format_invalid_pattern"
    FORMAT_INVALID_DATETIME = "format_invalid_datetime"
    FORMAT_MISSING_REQUIRED = "format_missing_required"
    FORMAT_INVALID_EMAIL = "format_invalid_email"
    FORMAT_INVALID_PHONE = "format_invalid_phone"

    # 시스템 오류
    SYSTEM_FILE_NOT_FOUND = "system_file_not_found"
    SYSTEM_PERMISSION_DENIED = "system_permission_denied"
    SYSTEM_IO_ERROR = "system_io_error"
    SYSTEM_CONFIG_ERROR = "system_config_error"


class ErrorSeverity(str, Enum):
    """오류 심각도 열거형"""

    LOW = "low"  # 경고 수준
    MEDIUM = "medium"  # 중간 수준
    HIGH = "high"  # 높은 수준
    CRITICAL = "critical"  # 치명적 수준


class ValidationErrorInfo(BaseModel):
    """검증 오류에 대한 상세 정보를 제공하는 모델"""

    error_type: ErrorType = Field(..., description="오류 유형")
    severity: ErrorSeverity = Field(..., description="오류 심각도")
    description: str = Field(..., description="오류 설명")
    suggestion: Optional[str] = Field(None, description="수정 제안")
    documentation_url: Optional[str] = Field(None, description="관련 문서 URL")

    class Config:
        """Pydantic 모델 설정"""

        use_enum_values = True
        validate_assignment = True
        extra = "forbid"


class ErrorRegistry:
    """오류 정보를 관리하는 레지스트리 클래스"""

    _error_info: Dict[ErrorType, ValidationErrorInfo] = {
        # 구조정확성 오류
        ErrorType.STRUCTURAL_INVALID_FORMAT: ValidationErrorInfo(
            error_type=ErrorType.STRUCTURAL_INVALID_FORMAT,
            severity=ErrorSeverity.HIGH,
            description="CSV 파일 형식이 올바르지 않습니다",
            suggestion="파일이 올바른 CSV 형식인지 확인하세요",
            documentation_url="https://tools.ietf.org/html/rfc4180",
        ),
        ErrorType.STRUCTURAL_INVALID_ENCODING: ValidationErrorInfo(
            error_type=ErrorType.STRUCTURAL_INVALID_ENCODING,
            severity=ErrorSeverity.MEDIUM,
            description="파일 인코딩을 읽을 수 없습니다",
            suggestion="파일을 UTF-8로 저장하거나 올바른 인코딩을 설정하세요",
        ),
        ErrorType.STRUCTURAL_INVALID_DELIMITER: ValidationErrorInfo(
            error_type=ErrorType.STRUCTURAL_INVALID_DELIMITER,
            severity=ErrorSeverity.MEDIUM,
            description="CSV 구분자가 일관되지 않습니다",
            suggestion="모든 행에서 동일한 구분자를 사용하세요",
        ),
        ErrorType.STRUCTURAL_ROW_COUNT_MISMATCH: ValidationErrorInfo(
            error_type=ErrorType.STRUCTURAL_ROW_COUNT_MISMATCH,
            severity=ErrorSeverity.HIGH,
            description="예상 행 수와 실제 행 수가 일치하지 않습니다",
            suggestion="데이터가 완전히 로드되었는지 확인하세요",
        ),
        ErrorType.STRUCTURAL_MISSING_HEADER: ValidationErrorInfo(
            error_type=ErrorType.STRUCTURAL_MISSING_HEADER,
            severity=ErrorSeverity.HIGH,
            description="필수 헤더 행이 없습니다",
            suggestion="파일의 첫 번째 행에 컬럼 헤더를 추가하세요",
        ),
        ErrorType.STRUCTURAL_EMPTY_FILE: ValidationErrorInfo(
            error_type=ErrorType.STRUCTURAL_EMPTY_FILE,
            severity=ErrorSeverity.CRITICAL,
            description="파일이 비어있습니다",
            suggestion="유효한 데이터가 포함된 파일을 사용하세요",
        ),
        # 형식정확성 오류
        ErrorType.FORMAT_INVALID_TYPE: ValidationErrorInfo(
            error_type=ErrorType.FORMAT_INVALID_TYPE,
            severity=ErrorSeverity.MEDIUM,
            description="데이터 타입이 예상과 다릅니다",
            suggestion="올바른 데이터 타입으로 값을 수정하세요",
        ),
        ErrorType.FORMAT_OUT_OF_RANGE: ValidationErrorInfo(
            error_type=ErrorType.FORMAT_OUT_OF_RANGE,
            severity=ErrorSeverity.MEDIUM,
            description="값이 허용 범위를 벗어났습니다",
            suggestion="값이 지정된 범위 내에 있는지 확인하세요",
        ),
        ErrorType.FORMAT_INVALID_LENGTH: ValidationErrorInfo(
            error_type=ErrorType.FORMAT_INVALID_LENGTH,
            severity=ErrorSeverity.LOW,
            description="문자열 길이가 허용 범위를 벗어났습니다",
            suggestion="문자열 길이를 조정하세요",
        ),
        ErrorType.FORMAT_INVALID_CATEGORY: ValidationErrorInfo(
            error_type=ErrorType.FORMAT_INVALID_CATEGORY,
            severity=ErrorSeverity.MEDIUM,
            description="값이 허용된 범주에 속하지 않습니다",
            suggestion="허용된 값 목록에서 적절한 값을 선택하세요",
        ),
        ErrorType.FORMAT_INVALID_PATTERN: ValidationErrorInfo(
            error_type=ErrorType.FORMAT_INVALID_PATTERN,
            severity=ErrorSeverity.MEDIUM,
            description="값이 지정된 패턴과 일치하지 않습니다",
            suggestion="값이 정규표현식 패턴을 만족하는지 확인하세요",
        ),
        ErrorType.FORMAT_INVALID_DATETIME: ValidationErrorInfo(
            error_type=ErrorType.FORMAT_INVALID_DATETIME,
            severity=ErrorSeverity.MEDIUM,
            description="날짜/시간 형식이 올바르지 않습니다",
            suggestion="지정된 날짜/시간 형식으로 값을 수정하세요",
        ),
        ErrorType.FORMAT_MISSING_REQUIRED: ValidationErrorInfo(
            error_type=ErrorType.FORMAT_MISSING_REQUIRED,
            severity=ErrorSeverity.HIGH,
            description="필수 필드가 누락되었습니다",
            suggestion="필수 필드에 값을 입력하세요",
        ),
        ErrorType.FORMAT_INVALID_EMAIL: ValidationErrorInfo(
            error_type=ErrorType.FORMAT_INVALID_EMAIL,
            severity=ErrorSeverity.MEDIUM,
            description="이메일 형식이 올바르지 않습니다",
            suggestion="올바른 이메일 주소 형식을 사용하세요",
        ),
        ErrorType.FORMAT_INVALID_PHONE: ValidationErrorInfo(
            error_type=ErrorType.FORMAT_INVALID_PHONE,
            severity=ErrorSeverity.MEDIUM,
            description="전화번호 형식이 올바르지 않습니다",
            suggestion="올바른 전화번호 형식을 사용하세요",
        ),
        # 시스템 오류
        ErrorType.SYSTEM_FILE_NOT_FOUND: ValidationErrorInfo(
            error_type=ErrorType.SYSTEM_FILE_NOT_FOUND,
            severity=ErrorSeverity.CRITICAL,
            description="파일을 찾을 수 없습니다",
            suggestion="파일 경로가 올바른지 확인하세요",
        ),
        ErrorType.SYSTEM_PERMISSION_DENIED: ValidationErrorInfo(
            error_type=ErrorType.SYSTEM_PERMISSION_DENIED,
            severity=ErrorSeverity.CRITICAL,
            description="파일 접근 권한이 없습니다",
            suggestion="파일 읽기 권한을 확인하세요",
        ),
        ErrorType.SYSTEM_IO_ERROR: ValidationErrorInfo(
            error_type=ErrorType.SYSTEM_IO_ERROR,
            severity=ErrorSeverity.CRITICAL,
            description="파일 입출력 오류가 발생했습니다",
            suggestion="파일이 다른 프로그램에서 사용 중인지 확인하세요",
        ),
        ErrorType.SYSTEM_CONFIG_ERROR: ValidationErrorInfo(
            error_type=ErrorType.SYSTEM_CONFIG_ERROR,
            severity=ErrorSeverity.CRITICAL,
            description="설정 파일에 오류가 있습니다",
            suggestion="YAML 설정 파일의 형식과 내용을 확인하세요",
        ),
    }

    @classmethod
    def get_error_info(cls, error_type: ErrorType) -> Optional[ValidationErrorInfo]:
        """오류 유형에 대한 정보를 반환합니다"""
        return cls._error_info.get(error_type)

    @classmethod
    def get_all_error_types(cls) -> list[ErrorType]:
        """모든 오류 유형을 반환합니다"""
        return list(cls._error_info.keys())

    @classmethod
    def get_errors_by_severity(cls, severity: ErrorSeverity) -> list[ErrorType]:
        """심각도별 오류 유형을 반환합니다"""
        return [
            error_type
            for error_type, info in cls._error_info.items()
            if info.severity == severity
        ]

    @classmethod
    def get_structural_errors(cls) -> list[ErrorType]:
        """구조정확성 관련 오류 유형을 반환합니다"""
        return [
            error_type
            for error_type in cls._error_info.keys()
            if error_type.value.startswith("structural_")
        ]

    @classmethod
    def get_format_errors(cls) -> list[ErrorType]:
        """형식정확성 관련 오류 유형을 반환합니다"""
        return [
            error_type
            for error_type in cls._error_info.keys()
            if error_type.value.startswith("format_")
        ]

    @classmethod
    def get_system_errors(cls) -> list[ErrorType]:
        """시스템 관련 오류 유형을 반환합니다"""
        return [
            error_type
            for error_type in cls._error_info.keys()
            if error_type.value.startswith("system_")
        ]
