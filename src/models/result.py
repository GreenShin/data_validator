"""
Result models for CSV validation.

이 모듈은 CSV 검증 결과와 오류 정보를 정의하는 데이터 모델을 포함합니다.
"""

from datetime import datetime
from typing import List, Any, Optional
from pydantic import BaseModel, Field, validator


class ValidationError(BaseModel):
    """개별 검증 오류를 나타내는 모델"""

    row_number: int = Field(..., description="오류가 발생한 행 번호 (1부터 시작)")
    column_name: str = Field(..., description="오류가 발생한 컬럼 이름")
    error_type: str = Field(..., description="오류 유형")
    actual_value: Any = Field(..., description="실제 값")
    expected_value: Any = Field(..., description="예상 값 또는 범위")
    message: str = Field(..., description="오류 메시지")

    @validator("row_number")
    def validate_row_number(cls, v):
        """행 번호 유효성 검사"""
        if v < 1:
            raise ValueError("row_number는 1 이상이어야 합니다")
        return v

    @validator("column_name")
    def validate_column_name(cls, v):
        """컬럼 이름 유효성 검사"""
        if not v or not isinstance(v, str):
            raise ValueError("column_name은 비어있지 않은 문자열이어야 합니다")
        return v.strip()

    @validator("error_type")
    def validate_error_type(cls, v):
        """오류 유형 유효성 검사"""
        if not v or not isinstance(v, str):
            raise ValueError("error_type은 비어있지 않은 문자열이어야 합니다")
        return v.strip()

    @validator("message")
    def validate_message(cls, v):
        """오류 메시지 유효성 검사"""
        if not v or not isinstance(v, str):
            raise ValueError("message는 비어있지 않은 문자열이어야 합니다")
        return v.strip()

    def to_dict(self) -> dict:
        """딕셔너리 형태로 변환"""
        return {
            "row_number": self.row_number,
            "column_name": self.column_name,
            "error_type": self.error_type,
            "actual_value": self.actual_value,
            "expected_value": self.expected_value,
            "message": self.message,
        }

    class Config:
        """Pydantic 모델 설정"""

        validate_assignment = True
        extra = "forbid"


class ValidationResult(BaseModel):
    """전체 검증 결과를 나타내는 모델"""

    file_name: str = Field(..., description="검증된 파일 이름")
    total_rows: int = Field(..., description="총 행 수")
    total_columns: int = Field(..., description="총 컬럼 수")
    structural_valid: bool = Field(..., description="구조정확성 검증 결과")
    format_valid: bool = Field(..., description="형식정확성 검증 결과")
    errors: List[ValidationError] = Field(
        default_factory=list, description="발견된 오류 목록"
    )
    processing_time: float = Field(..., description="처리 시간 (초)")
    timestamp: datetime = Field(
        default_factory=datetime.now, description="검증 수행 시간"
    )

    @validator("total_rows")
    def validate_total_rows(cls, v):
        """총 행 수 유효성 검사"""
        if v < 0:
            raise ValueError("total_rows는 0 이상이어야 합니다")
        return v

    @validator("total_columns")
    def validate_total_columns(cls, v):
        """총 컬럼 수 유효성 검사"""
        if v < 0:
            raise ValueError("total_columns는 0 이상이어야 합니다")
        return v

    @validator("processing_time")
    def validate_processing_time(cls, v):
        """처리 시간 유효성 검사"""
        if v < 0:
            raise ValueError("processing_time은 0 이상이어야 합니다")
        return v

    @property
    def is_valid(self) -> bool:
        """전체 검증 결과가 유효한지 확인"""
        return self.structural_valid and self.format_valid and len(self.errors) == 0

    @property
    def error_count(self) -> int:
        """오류 개수 반환"""
        return len(self.errors)

    @property
    def success_rate(self) -> float:
        """성공률 계산 (0.0 ~ 1.0)"""
        if self.total_rows == 0:
            return 1.0
        return (self.total_rows - self.error_count) / self.total_rows

    def get_errors_by_type(self) -> dict:
        """오류 유형별로 그룹화된 오류 목록 반환"""
        errors_by_type = {}
        for error in self.errors:
            if error.error_type not in errors_by_type:
                errors_by_type[error.error_type] = []
            errors_by_type[error.error_type].append(error)
        return errors_by_type

    def get_errors_by_column(self) -> dict:
        """컬럼별로 그룹화된 오류 목록 반환"""
        errors_by_column = {}
        for error in self.errors:
            if error.column_name not in errors_by_column:
                errors_by_column[error.column_name] = []
            errors_by_column[error.column_name].append(error)
        return errors_by_column

    def get_errors_by_row(self) -> dict:
        """행별로 그룹화된 오류 목록 반환"""
        errors_by_row = {}
        for error in self.errors:
            if error.row_number not in errors_by_row:
                errors_by_row[error.row_number] = []
            errors_by_row[error.row_number].append(error)
        return errors_by_row

    def add_error(self, error: ValidationError) -> None:
        """오류 추가"""
        self.errors.append(error)

    def add_errors(self, errors: List[ValidationError]) -> None:
        """여러 오류 추가"""
        self.errors.extend(errors)

    def clear_errors(self) -> None:
        """모든 오류 제거"""
        self.errors.clear()

    def to_dict(self) -> dict:
        """딕셔너리 형태로 변환"""
        return {
            "file_name": self.file_name,
            "total_rows": self.total_rows,
            "total_columns": self.total_columns,
            "structural_valid": self.structural_valid,
            "format_valid": self.format_valid,
            "error_count": self.error_count,
            "is_valid": self.is_valid,
            "success_rate": self.success_rate,
            "processing_time": self.processing_time,
            "timestamp": self.timestamp.isoformat(),
            "errors": [error.to_dict() for error in self.errors],
        }

    def to_summary_dict(self) -> dict:
        """요약 정보만 포함한 딕셔너리 반환"""
        return {
            "file_name": self.file_name,
            "total_rows": self.total_rows,
            "total_columns": self.total_columns,
            "structural_valid": self.structural_valid,
            "format_valid": self.format_valid,
            "error_count": self.error_count,
            "is_valid": self.is_valid,
            "success_rate": self.success_rate,
            "processing_time": self.processing_time,
            "timestamp": self.timestamp.isoformat(),
        }

    class Config:
        """Pydantic 모델 설정"""

        validate_assignment = True
        extra = "forbid"
