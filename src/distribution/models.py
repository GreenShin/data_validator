"""
Data models for distribution analysis.

분포 분석을 위한 데이터 모델들을 정의합니다.
"""

from typing import List, Optional, Union, Tuple, Any
from pydantic import BaseModel, Field, field_validator
from enum import Enum


class DataType(str, Enum):
    """데이터 타입 열거형"""
    CATEGORICAL = "categorical"
    NUMERICAL = "numerical"
    AUTO = "auto"


class CategoryInfo(BaseModel):
    """범주형 데이터의 개별 범주 정보"""
    value: str = Field(..., description="범주 값")
    count: int = Field(..., ge=0, description="해당 범주의 개수")
    percentage: float = Field(..., ge=0.0, le=100.0, description="해당 범주의 비율 (%)")
    
    @field_validator('percentage')
    @classmethod
    def validate_percentage(cls, v):
        if v < 0.0 or v > 100.0:
            raise ValueError('비율은 0.0과 100.0 사이여야 합니다')
        return v


class BinInfo(BaseModel):
    """숫자형 데이터의 구간 정보"""
    range: Tuple[float, float] = Field(..., description="구간 범위 (시작값, 끝값)")
    count: int = Field(..., ge=0, description="해당 구간의 개수")
    percentage: float = Field(..., ge=0.0, le=100.0, description="해당 구간의 비율 (%)")
    
    @field_validator('range')
    @classmethod
    def validate_range(cls, v):
        if v[0] > v[1]:
            raise ValueError('구간의 시작값은 끝값보다 작거나 같아야 합니다')
        return v
    
    @field_validator('percentage')
    @classmethod
    def validate_percentage(cls, v):
        if v < 0.0 or v > 100.0:
            raise ValueError('비율은 0.0과 100.0 사이여야 합니다')
        return v


class NumericalStats(BaseModel):
    """숫자형 데이터의 통계 정보"""
    mean: float = Field(..., description="평균")
    median: float = Field(..., description="중앙값")
    std: float = Field(..., ge=0, description="표준편차")
    min: float = Field(..., description="최솟값")
    max: float = Field(..., description="최댓값")
    q25: float = Field(..., description="1사분위수 (25%)")
    q75: float = Field(..., description="3사분위수 (75%)")
    
    @field_validator('std')
    @classmethod
    def validate_std(cls, v):
        if v < 0:
            raise ValueError('표준편차는 0 이상이어야 합니다')
        return v
    
    @field_validator('q25', 'median', 'q75')
    @classmethod
    def validate_quartiles(cls, v, info):
        values = info.data
        if 'min' in values and 'max' in values:
            if v < values['min'] or v > values['max']:
                raise ValueError('사분위수는 최솟값과 최댓값 사이여야 합니다')
        return v


class CategoricalDistribution(BaseModel):
    """범주형 데이터의 분포 정보"""
    categories: List[CategoryInfo] = Field(..., description="범주별 정보 리스트")
    other_count: int = Field(0, ge=0, description="기타 범주의 개수 (최대 범주 수 초과 시)")
    other_percentage: float = Field(0.0, ge=0.0, le=100.0, description="기타 범주의 비율 (%)")
    unique_count: int = Field(..., ge=0, description="고유 범주 수")
    
    @field_validator('other_percentage')
    @classmethod
    def validate_other_percentage(cls, v):
        if v < 0.0 or v > 100.0:
            raise ValueError('기타 범주 비율은 0.0과 100.0 사이여야 합니다')
        return v


class NumericalDistribution(BaseModel):
    """숫자형 데이터의 분포 정보"""
    bins: List[BinInfo] = Field(..., description="구간별 정보 리스트")
    auto_generated: bool = Field(False, description="구간이 자동 생성되었는지 여부")
    stats: Optional[NumericalStats] = Field(None, description="통계 정보")
    
    @field_validator('bins')
    @classmethod
    def validate_bins(cls, v):
        if not v:
            raise ValueError('구간 정보는 비어있을 수 없습니다')
        return v


class ColumnDistribution(BaseModel):
    """컬럼별 분포 분석 결과"""
    column_name: str = Field(..., description="컬럼명")
    data_type: str = Field(..., description="데이터 타입 (categorical/numerical)")
    total_count: int = Field(..., ge=0, description="전체 데이터 개수")
    null_count: int = Field(0, ge=0, description="null 값 개수")
    null_percentage: float = Field(0.0, ge=0.0, le=100.0, description="null 값 비율 (%)")
    distribution: Union[CategoricalDistribution, NumericalDistribution] = Field(
        ..., description="분포 정보"
    )
    processing_time: float = Field(..., ge=0, description="처리 시간 (초)")
    
    @field_validator('null_percentage')
    @classmethod
    def validate_null_percentage(cls, v):
        if v < 0.0 or v > 100.0:
            raise ValueError('null 값 비율은 0.0과 100.0 사이여야 합니다')
        return v
    
    @field_validator('processing_time')
    @classmethod
    def validate_processing_time(cls, v):
        if v < 0:
            raise ValueError('처리 시간은 0 이상이어야 합니다')
        return v