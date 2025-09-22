"""
Categorical distribution analysis module.

범주형 데이터의 분포 분석을 담당하는 모듈입니다.
"""

import time
import numpy as np
from typing import List, Any, Dict
from collections import Counter
from .models import CategoricalDistribution, CategoryInfo, ColumnDistribution
from .utils import DataTypeDetector


class CategoricalAnalyzer:
    """범주형 데이터 분석기"""
    
    def __init__(self, max_categories: int = 100):
        """
        CategoricalAnalyzer 초기화
        
        Args:
            max_categories: 최대 범주 수
        """
        self.max_categories = max_categories
    
    def analyze(self, data: List[Any], column_name: str) -> ColumnDistribution:
        """
        범주형 데이터의 분포를 분석합니다.
        
        Args:
            data: 분석할 데이터 리스트
            column_name: 컬럼명
            
        Returns:
            ColumnDistribution: 분석 결과
        """
        start_time = time.time()
        
        # null 값 처리 (None, 빈 문자열, NaN 모두 포함)
        null_count = sum(1 for x in data if x is None or x == '' or (isinstance(x, float) and np.isnan(x)))
        total_count = len(data)
        valid_data = [x for x in data if x is not None and x != '' and not (isinstance(x, float) and np.isnan(x))]
        
        # 범주별 개수 계산
        counter = Counter(str(x) for x in valid_data)
        
        # 범주 정보 생성
        categories = []
        other_count = 0
        
        # 빈도순으로 정렬
        sorted_items = counter.most_common()
        
        for i, (value, count) in enumerate(sorted_items):
            if i < self.max_categories:
                percentage = DataTypeDetector.calculate_percentage(count, total_count)
                category_info = CategoryInfo(
                    value=value,
                    count=count,
                    percentage=percentage
                )
                categories.append(category_info)
            else:
                other_count += count
        
        # 기타 범주 비율 계산
        other_percentage = DataTypeDetector.calculate_percentage(other_count, total_count)
        
        # 분포 정보 생성
        distribution = CategoricalDistribution(
            categories=categories,
            other_count=other_count,
            other_percentage=other_percentage,
            unique_count=len(counter)
        )
        
        # null 값 비율 계산
        null_percentage = DataTypeDetector.calculate_percentage(null_count, total_count)
        
        processing_time = time.time() - start_time
        
        return ColumnDistribution(
            column_name=column_name,
            data_type="categorical",
            total_count=total_count,
            null_count=null_count,
            null_percentage=null_percentage,
            distribution=distribution,
            processing_time=processing_time
        )
    
    def get_top_categories(self, data: List[Any], top_n: int = 10) -> List[CategoryInfo]:
        """
        상위 N개 범주를 반환합니다.
        
        Args:
            data: 분석할 데이터 리스트
            top_n: 반환할 상위 범주 수
            
        Returns:
            List[CategoryInfo]: 상위 범주 정보 리스트
        """
        valid_data = [x for x in data if x is not None and x != '']
        counter = Counter(str(x) for x in valid_data)
        total_count = len(data)
        
        categories = []
        for value, count in counter.most_common(top_n):
            percentage = DataTypeDetector.calculate_percentage(count, total_count)
            category_info = CategoryInfo(
                value=value,
                count=count,
                percentage=percentage
            )
            categories.append(category_info)
        
        return categories
    
    def get_category_frequency(self, data: List[Any]) -> Dict[str, int]:
        """
        범주별 빈도를 반환합니다.
        
        Args:
            data: 분석할 데이터 리스트
            
        Returns:
            Dict[str, int]: 범주별 빈도 딕셔너리
        """
        valid_data = [x for x in data if x is not None and x != '']
        return dict(Counter(str(x) for x in valid_data))