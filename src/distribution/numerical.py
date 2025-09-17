"""
Numerical distribution analysis module.

숫자형 데이터의 분포 분석을 담당하는 모듈입니다.
"""

import time
from typing import List, Any, Optional
import numpy as np
from .models import NumericalDistribution, BinInfo, NumericalStats, ColumnDistribution
from .utils import DataTypeDetector


class NumericalAnalyzer:
    """숫자형 데이터 분석기"""
    
    def __init__(self, auto_bins: bool = True, bin_count: int = 10):
        """
        NumericalAnalyzer 초기화
        
        Args:
            auto_bins: 자동 구간 생성 여부
            bin_count: 자동 생성할 구간 수
        """
        self.auto_bins = auto_bins
        self.bin_count = bin_count
    
    def analyze(
        self, 
        data: List[Any], 
        column_name: str,
        custom_bins: Optional[List[float]] = None
    ) -> ColumnDistribution:
        """
        숫자형 데이터의 분포를 분석합니다.
        
        Args:
            data: 분석할 데이터 리스트
            column_name: 컬럼명
            custom_bins: 사용자 정의 구간 (선택적)
            
        Returns:
            ColumnDistribution: 분석 결과
        """
        start_time = time.time()
        
        # null 값 처리 (None, 빈 문자열, NaN 모두 포함)
        null_count = sum(1 for x in data if x is None or x == '' or (isinstance(x, float) and np.isnan(x)))
        total_count = len(data)
        
        # 숫자형 데이터로 변환
        numeric_data = DataTypeDetector.convert_to_numeric(data)
        
        if not numeric_data:
            # 숫자형 데이터가 없는 경우 빈 분포 반환
            distribution = NumericalDistribution(
                bins=[],
                auto_generated=False,
                stats=None
            )
            
            processing_time = time.time() - start_time
            
            return ColumnDistribution(
                column_name=column_name,
                data_type="numerical",
                total_count=total_count,
                null_count=null_count,
                null_percentage=DataTypeDetector.calculate_percentage(null_count, total_count),
                distribution=distribution,
                processing_time=processing_time
            )
        
        # 구간 생성
        if custom_bins:
            bins = custom_bins
            auto_generated = False
        elif self.auto_bins:
            bins = DataTypeDetector.create_auto_bins(numeric_data, self.bin_count)
            auto_generated = True
        else:
            # 기본 구간 생성
            bins = DataTypeDetector.create_auto_bins(numeric_data, 10)
            auto_generated = True
        
        # 구간별 개수 계산
        bin_counts = DataTypeDetector.count_values_in_bins(numeric_data, bins)
        
        # 구간 정보 생성
        bin_infos = []
        for i in range(len(bins) - 1):
            count = bin_counts[i] if i < len(bin_counts) else 0
            percentage = DataTypeDetector.calculate_percentage(count, total_count)
            
            bin_info = BinInfo(
                range=(bins[i], bins[i + 1]),
                count=count,
                percentage=percentage
            )
            bin_infos.append(bin_info)
        
        # 통계 정보 계산
        stats = self._calculate_stats(numeric_data)
        
        # 분포 정보 생성
        distribution = NumericalDistribution(
            bins=bin_infos,
            auto_generated=auto_generated,
            stats=stats
        )
        
        # null 값 비율 계산
        null_percentage = DataTypeDetector.calculate_percentage(null_count, total_count)
        
        processing_time = time.time() - start_time
        
        return ColumnDistribution(
            column_name=column_name,
            data_type="numerical",
            total_count=total_count,
            null_count=null_count,
            null_percentage=null_percentage,
            distribution=distribution,
            processing_time=processing_time
        )
    
    def _calculate_stats(self, data: List[float]) -> NumericalStats:
        """통계 정보를 계산합니다."""
        if not data:
            return None
        
        data_array = np.array(data)
        
        # NaN 값 처리
        mean_val = np.mean(data_array)
        median_val = np.median(data_array)
        std_val = np.std(data_array)
        min_val = np.min(data_array)
        max_val = np.max(data_array)
        q25_val = np.percentile(data_array, 25)
        q75_val = np.percentile(data_array, 75)
        
        # NaN 값을 0으로 대체
        if np.isnan(std_val):
            std_val = 0.0
        
        return NumericalStats(
            mean=float(mean_val) if not np.isnan(mean_val) else 0.0,
            median=float(median_val) if not np.isnan(median_val) else 0.0,
            std=float(std_val),
            min=float(min_val) if not np.isnan(min_val) else 0.0,
            max=float(max_val) if not np.isnan(max_val) else 0.0,
            q25=float(q25_val) if not np.isnan(q25_val) else 0.0,
            q75=float(q75_val) if not np.isnan(q75_val) else 0.0
        )
    
    def analyze_with_custom_bins(
        self, 
        data: List[Any], 
        column_name: str, 
        bins: List[float]
    ) -> ColumnDistribution:
        """
        사용자 정의 구간으로 숫자형 데이터를 분석합니다.
        
        Args:
            data: 분석할 데이터 리스트
            column_name: 컬럼명
            bins: 사용자 정의 구간
            
        Returns:
            ColumnDistribution: 분석 결과
        """
        return self.analyze(data, column_name, custom_bins=bins)
    
    def get_basic_stats(self, data: List[Any]) -> Optional[NumericalStats]:
        """
        기본 통계 정보를 반환합니다.
        
        Args:
            data: 분석할 데이터 리스트
            
        Returns:
            NumericalStats: 통계 정보 (데이터가 없는 경우 None)
        """
        numeric_data = DataTypeDetector.convert_to_numeric(data)
        return self._calculate_stats(numeric_data)