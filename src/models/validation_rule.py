"""
Validation rule models for CSV validation.

이 모듈은 CSV 검증에 사용되는 규칙과 설정을 정의하는 데이터 모델을 포함합니다.
"""

from enum import Enum
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator


class DataType(str, Enum):
    """지원되는 데이터 타입 열거형"""

    INTEGER = "integer"
    FLOAT = "float"
    STRING = "string"
    DATETIME = "datetime"
    BOOLEAN = "boolean"
    EMAIL = "email"
    PHONE = "phone"
    OBJECT = "object"
    ARRAY = "array"
    NULL = "null"


class FileType(str, Enum):
    """지원되는 파일 타입 열거형"""
    
    CSV = "csv"
    JSON = "json"
    JSONL = "jsonl"


class ValidationRule(BaseModel):
    """개별 컬럼에 대한 검증 규칙을 정의하는 모델"""

    name: str = Field(..., description="컬럼 이름")
    type: DataType = Field(..., description="데이터 타입")
    required: bool = Field(True, description="필수 필드 여부")

    # 범위 검증 (숫자 타입용)
    range: Optional[Dict[str, float]] = Field(
        None, description="숫자 타입의 최소/최대값 범위"
    )

    # 길이 검증 (문자열 타입용)
    length: Optional[Dict[str, int]] = Field(
        None, description="문자열 타입의 최소/최대 길이"
    )

    # 범주형 데이터 검증
    allowed_values: Optional[List[str]] = Field(
        None, description="허용되는 값 목록 (범주형 데이터용)"
    )

    # 대소문자 구분 여부
    case_sensitive: bool = Field(True, description="범주형 데이터의 대소문자 구분 여부")

    # 정규표현식 패턴
    pattern: Optional[str] = Field(None, description="정규표현식 패턴 (문자열 검증용)")

    # 날짜/시간 형식
    format: Optional[str] = Field(None, description="날짜/시간 형식 문자열")

    @validator("range")
    def validate_range(cls, v, values):
        """범위 검증 규칙 유효성 검사"""
        if v is not None:
            if "min" not in v or "max" not in v:
                raise ValueError("range는 'min'과 'max' 키를 포함해야 합니다")
            if v["min"] >= v["max"]:
                raise ValueError("min 값은 max 값보다 작아야 합니다")
        return v

    @validator("length")
    def validate_length(cls, v, values):
        """길이 검증 규칙 유효성 검사"""
        if v is not None:
            if "min" not in v or "max" not in v:
                raise ValueError("length는 'min'과 'max' 키를 포함해야 합니다")
            if v["min"] < 0 or v["max"] < 0:
                raise ValueError("길이 값은 0 이상이어야 합니다")
            if v["min"] > v["max"]:
                raise ValueError("min 길이는 max 길이보다 작거나 같아야 합니다")
        return v

    @validator("allowed_values")
    def validate_allowed_values(cls, v, values):
        """허용 값 목록 유효성 검사"""
        if v is not None and len(v) == 0:
            raise ValueError("allowed_values는 비어있을 수 없습니다")
        return v

    @validator("pattern")
    def validate_pattern(cls, v):
        """정규표현식 패턴 유효성 검사"""
        if v is not None:
            import re

            try:
                re.compile(v)
            except re.error as e:
                raise ValueError(f"잘못된 정규표현식 패턴: {e}")
        return v

    class Config:
        """Pydantic 모델 설정"""

        use_enum_values = True
        validate_assignment = True
        extra = "forbid"


class FileInfo(BaseModel):
    """파일에 대한 기본 정보를 정의하는 모델"""

    file_type: FileType = Field(FileType.CSV, description="파일 타입")
    expected_rows: Optional[int] = Field(
        None, description="예상 행 수 (None이면 검증하지 않음)"
    )
    encoding: str = Field("utf-8", description="파일 인코딩")
    delimiter: str = Field(",", description="CSV 구분자")
    has_header: bool = Field(True, description="헤더 행 포함 여부")
    
    # JSON/JSONL 전용 설정
    json_schema: Optional[Dict[str, Any]] = Field(
        None, description="JSON 스키마 (JSON 파일용)"
    )
    json_root_path: Optional[str] = Field(
        None, description="JSON 루트 경로 (중첩된 JSON에서 데이터 위치 지정)"
    )
    jsonl_array_mode: bool = Field(
        False, description="JSONL을 배열로 처리할지 여부"
    )

    @validator("expected_rows")
    def validate_expected_rows(cls, v):
        """예상 행 수 유효성 검사"""
        if v is not None and v <= 0:
            raise ValueError("expected_rows는 0보다 커야 합니다")
        return v

    @validator("encoding")
    def validate_encoding(cls, v):
        """인코딩 유효성 검사"""
        if not v or not isinstance(v, str):
            raise ValueError("encoding은 비어있지 않은 문자열이어야 합니다")
        return v.lower()

    @validator("delimiter")
    def validate_delimiter(cls, v):
        """구분자 유효성 검사"""
        if not v or not isinstance(v, str):
            raise ValueError("delimiter는 비어있지 않은 문자열이어야 합니다")
        return v

    class Config:
        """Pydantic 모델 설정"""

        validate_assignment = True
        extra = "forbid"


class ValidationConfig(BaseModel):
    """전체 검증 설정을 정의하는 모델"""

    file_info: FileInfo = Field(..., description="파일 정보")
    columns: List[ValidationRule] = Field(..., description="컬럼별 검증 규칙 목록")

    @validator("columns")
    def validate_columns(cls, v):
        """컬럼 규칙 목록 유효성 검사"""
        if not v:
            raise ValueError("columns는 비어있을 수 없습니다")

        # 컬럼 이름 중복 검사
        column_names = [rule.name for rule in v]
        if len(column_names) != len(set(column_names)):
            raise ValueError("컬럼 이름은 중복될 수 없습니다")

        return v

    def get_column_rule(self, column_name: str) -> Optional[ValidationRule]:
        """컬럼 이름으로 검증 규칙을 조회합니다"""
        for rule in self.columns:
            if rule.name == column_name:
                return rule
        return None

    def get_required_columns(self) -> List[str]:
        """필수 컬럼 목록을 반환합니다"""
        return [rule.name for rule in self.columns if rule.required]

    def get_optional_columns(self) -> List[str]:
        """선택적 컬럼 목록을 반환합니다"""
        return [rule.name for rule in self.columns if not rule.required]

    class Config:
        """Pydantic 모델 설정"""

        validate_assignment = True
        extra = "forbid"
