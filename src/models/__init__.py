"""
Data models for CSV validation.

이 모듈은 검증 규칙, 결과, 오류 등의 데이터 모델을 정의합니다.
"""

from .validation_rule import ValidationRule, DataType, FileType, FileInfo, ValidationConfig
from .result import ValidationResult, ValidationError
from .error import ErrorType, ErrorSeverity, ValidationErrorInfo, ErrorRegistry

__all__ = [
    "ValidationRule",
    "DataType",
    "FileType",
    "FileInfo",
    "ValidationConfig",
    "ValidationResult",
    "ValidationError",
    "ErrorType",
    "ErrorSeverity",
    "ValidationErrorInfo",
    "ErrorRegistry",
]
