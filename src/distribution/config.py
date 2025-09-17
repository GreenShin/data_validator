"""
Configuration models for distribution analysis.

분포 분석을 위한 설정 모델들을 정의합니다.
"""

from typing import List, Optional, Union
from pydantic import BaseModel, Field, field_validator


class ColumnConfig(BaseModel):
    """컬럼별 분포 분석 설정"""
    name: str = Field(..., description="컬럼명")
    type: str = Field(..., description="데이터 타입 (categorical/numerical/auto)")
    max_categories: Optional[int] = Field(None, ge=1, description="최대 범주 수 (범주형 데이터용)")
    bins: Optional[List[float]] = Field(None, description="사용자 정의 구간 (숫자형 데이터용)")
    auto_bins: bool = Field(False, description="자동 구간 생성 여부 (숫자형 데이터용)")
    bin_count: Optional[int] = Field(None, ge=2, le=100, description="자동 생성할 구간 수")
    
    @field_validator('type')
    @classmethod
    def validate_type(cls, v):
        allowed_types = ['categorical', 'numerical', 'auto']
        if v not in allowed_types:
            raise ValueError(f'데이터 타입은 {allowed_types} 중 하나여야 합니다')
        return v
    
    @field_validator('bins')
    @classmethod
    def validate_bins(cls, v):
        if v is not None:
            if len(v) < 2:
                raise ValueError('구간은 최소 2개 이상의 값이 필요합니다')
            if v != sorted(v):
                raise ValueError('구간 값들은 오름차순으로 정렬되어야 합니다')
        return v
    
    @field_validator('bin_count')
    @classmethod
    def validate_bin_count(cls, v):
        if v is not None and (v < 2 or v > 100):
            raise ValueError('구간 수는 2와 100 사이여야 합니다')
        return v


class DistributionConfig(BaseModel):
    """분포 분석 전체 설정"""
    enabled: bool = Field(True, description="분포 분석 활성화 여부")
    columns: List[ColumnConfig] = Field(..., description="분석할 컬럼 설정 리스트")
    memory_limit: Optional[int] = Field(None, ge=100, description="메모리 제한 (MB)")
    chunk_size: int = Field(10000, ge=1000, le=100000, description="청크 크기 (행 수)")
    
    @field_validator('columns')
    @classmethod
    def validate_columns(cls, v):
        if not v:
            raise ValueError('분석할 컬럼이 최소 1개 이상 필요합니다')
        
        # 컬럼명 중복 검사
        column_names = [col.name for col in v]
        if len(column_names) != len(set(column_names)):
            raise ValueError('컬럼명은 중복될 수 없습니다')
        
        return v
    
    @field_validator('chunk_size')
    @classmethod
    def validate_chunk_size(cls, v):
        if v < 1000 or v > 100000:
            raise ValueError('청크 크기는 1000과 100000 사이여야 합니다')
        return v
    
    def get_column_config(self, column_name: str) -> Optional[ColumnConfig]:
        """특정 컬럼의 설정을 반환합니다."""
        for col_config in self.columns:
            if col_config.name == column_name:
                return col_config
        return None
    
    def is_column_enabled(self, column_name: str) -> bool:
        """특정 컬럼이 분석 대상인지 확인합니다."""
        return self.get_column_config(column_name) is not None