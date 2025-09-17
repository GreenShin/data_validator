"""
Utility functions for distribution analysis.

분포 분석을 위한 유틸리티 함수들을 정의합니다.
"""

import re
from typing import List, Any, Union
import numpy as np
from .models import DataType


class DataTypeDetector:
    """데이터 타입을 자동으로 감지하는 클래스"""
    
    @staticmethod
    def detect_data_type(data: List[Any]) -> DataType:
        """
        데이터 리스트의 타입을 자동으로 감지합니다.
        
        Args:
            data: 분석할 데이터 리스트
            
        Returns:
            DataType: 감지된 데이터 타입
        """
        if not data:
            return DataType.CATEGORICAL
        
        # null 값 제거
        clean_data = [x for x in data if x is not None and x != '']
        
        if not clean_data:
            return DataType.CATEGORICAL
        
        # 숫자형 데이터 감지
        numeric_count = 0
        total_count = len(clean_data)
        
        for value in clean_data:
            if DataTypeDetector._is_numeric(value):
                numeric_count += 1
        
        # 80% 이상이 숫자형이면 숫자형으로 판단
        numeric_ratio = numeric_count / total_count
        if numeric_ratio >= 0.8:
            return DataType.NUMERICAL
        else:
            return DataType.CATEGORICAL
    
    @staticmethod
    def _is_numeric(value: Any) -> bool:
        """값이 숫자인지 확인합니다."""
        if isinstance(value, (int, float)):
            return True
        
        if isinstance(value, str):
            # 빈 문자열은 숫자가 아님
            if not value.strip():
                return False
            
            # 숫자 패턴 확인 (정수, 실수, 과학적 표기법)
            numeric_pattern = r'^-?\d+(\.\d+)?([eE][+-]?\d+)?$'
            return bool(re.match(numeric_pattern, value.strip()))
        
        return False
    
    @staticmethod
    def convert_to_numeric(data: List[Any]) -> List[float]:
        """데이터를 숫자형으로 변환합니다."""
        numeric_data = []
        
        for value in data:
            # None, 빈 문자열, NaN 값은 건너뜀
            if value is None or value == '' or (isinstance(value, float) and np.isnan(value)):
                continue
            
            try:
                if isinstance(value, (int, float)):
                    numeric_data.append(float(value))
                elif isinstance(value, str):
                    numeric_data.append(float(value.strip()))
            except (ValueError, TypeError):
                # 변환할 수 없는 값은 건너뜀
                continue
        
        return numeric_data
    
    @staticmethod
    def get_unique_values(data: List[Any], max_categories: int = None) -> List[str]:
        """고유값 리스트를 반환합니다."""
        unique_values = []
        seen = set()
        
        for value in data:
            if value is None or value == '':
                continue
            
            str_value = str(value)
            if str_value not in seen:
                seen.add(str_value)
                unique_values.append(str_value)
                
                # 최대 범주 수 제한
                if max_categories and len(unique_values) >= max_categories:
                    break
        
        return unique_values
    
    @staticmethod
    def calculate_percentage(count: int, total: int) -> float:
        """비율을 계산합니다."""
        if total == 0:
            return 0.0
        return round((count / total) * 100, 2)
    
    @staticmethod
    def create_auto_bins(data: List[float], bin_count: int = 10) -> List[float]:
        """자동으로 구간을 생성합니다."""
        if not data:
            return []
        
        data_array = np.array(data)
        min_val = np.min(data_array)
        max_val = np.max(data_array)
        
        # 동일한 값이면 구간을 만들 수 없음
        if min_val == max_val:
            return [min_val, max_val + 0.1]
        
        # numpy의 histogram_bin_edges를 사용하여 구간 생성
        bins = np.linspace(min_val, max_val, bin_count + 1)
        return bins.tolist()
    
    @staticmethod
    def count_values_in_bins(data: List[float], bins: List[float]) -> List[int]:
        """각 구간에 속하는 값의 개수를 계산합니다."""
        if not data or len(bins) < 2:
            return []
        
        data_array = np.array(data)
        counts, _ = np.histogram(data_array, bins=bins)
        return counts.tolist()