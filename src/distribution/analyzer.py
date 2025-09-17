"""
Main distribution analyzer module.

분포 분석의 메인 엔진을 담당하는 모듈입니다.
"""

import time
from typing import List, Any, Optional, Dict
from .config import DistributionConfig, ColumnConfig
from .models import ColumnDistribution, DataType
from .categorical import CategoricalAnalyzer
from .numerical import NumericalAnalyzer
from .utils import DataTypeDetector


class DistributionAnalyzer:
    """분포 분석 메인 클래스"""
    
    def __init__(self, config: DistributionConfig):
        """
        DistributionAnalyzer 초기화
        
        Args:
            config: 분포 분석 설정
        """
        self.config = config
        self.categorical_analyzer = CategoricalAnalyzer()
        self.numerical_analyzer = NumericalAnalyzer()
    
    def analyze_column(self, column_name: str, data: List[Any]) -> ColumnDistribution:
        """
        특정 컬럼의 분포를 분석합니다.
        
        Args:
            column_name: 컬럼명
            data: 분석할 데이터 리스트
            
        Returns:
            ColumnDistribution: 분석 결과
            
        Raises:
            ValueError: 컬럼이 설정에 없는 경우
        """
        # 컬럼 설정 확인
        column_config = self.config.get_column_config(column_name)
        if not column_config:
            raise ValueError(f"컬럼 '{column_name}'이 분포 분석 설정에 없습니다")
        
        # 데이터 타입 결정
        if column_config.type == "auto":
            detected_type = DataTypeDetector.detect_data_type(data)
        elif column_config.type == "categorical":
            detected_type = DataType.CATEGORICAL
        elif column_config.type == "numerical":
            detected_type = DataType.NUMERICAL
        else:
            raise ValueError(f"지원하지 않는 데이터 타입: {column_config.type}")
        
        # 타입별 분석 실행
        if detected_type == DataType.CATEGORICAL:
            return self.analyze_categorical(data, column_name, column_config)
        else:
            return self.analyze_numerical(data, column_name, column_config)
    
    def analyze_categorical(
        self, 
        data: List[Any], 
        column_name: str, 
        column_config: ColumnConfig
    ) -> ColumnDistribution:
        """
        범주형 데이터를 분석합니다.
        
        Args:
            data: 분석할 데이터 리스트
            column_name: 컬럼명
            column_config: 컬럼 설정
            
        Returns:
            ColumnDistribution: 분석 결과
        """
        # 최대 범주 수 설정
        max_categories = column_config.max_categories or 100
        self.categorical_analyzer.max_categories = max_categories
        
        return self.categorical_analyzer.analyze(data, column_name)
    
    def analyze_numerical(
        self, 
        data: List[Any], 
        column_name: str, 
        column_config: ColumnConfig
    ) -> ColumnDistribution:
        """
        숫자형 데이터를 분석합니다.
        
        Args:
            data: 분석할 데이터 리스트
            column_name: 컬럼명
            column_config: 컬럼 설정
            
        Returns:
            ColumnDistribution: 분석 결과
        """
        # 구간 설정
        custom_bins = column_config.bins
        auto_bins = column_config.auto_bins
        bin_count = column_config.bin_count or 10
        
        # 분석기 설정 업데이트
        self.numerical_analyzer.auto_bins = auto_bins
        self.numerical_analyzer.bin_count = bin_count
        
        return self.numerical_analyzer.analyze(data, column_name, custom_bins)
    
    def detect_data_type(self, data: List[Any]) -> DataType:
        """
        데이터 타입을 감지합니다.
        
        Args:
            data: 분석할 데이터 리스트
            
        Returns:
            DataType: 감지된 데이터 타입
        """
        return DataTypeDetector.detect_data_type(data)
    
    def analyze_multiple_columns(
        self, 
        data_dict: Dict[str, List[Any]]
    ) -> List[ColumnDistribution]:
        """
        여러 컬럼의 분포를 분석합니다.
        
        Args:
            data_dict: 컬럼명을 키로 하는 데이터 딕셔너리
            
        Returns:
            List[ColumnDistribution]: 분석 결과 리스트
        """
        results = []
        
        for column_name, data in data_dict.items():
            if self.config.is_column_enabled(column_name):
                try:
                    result = self.analyze_column(column_name, data)
                    results.append(result)
                except Exception as e:
                    # 개별 컬럼 분석 실패 시 로그만 남기고 계속 진행
                    print(f"컬럼 '{column_name}' 분석 실패: {e}")
                    continue
        
        return results
    
    def get_analysis_summary(self, results: List[ColumnDistribution]) -> Dict[str, Any]:
        """
        분석 결과 요약을 반환합니다.
        
        Args:
            results: 분석 결과 리스트
            
        Returns:
            Dict[str, Any]: 요약 정보
        """
        if not results:
            return {
                "total_columns": 0,
                "categorical_columns": 0,
                "numerical_columns": 0,
                "total_processing_time": 0.0
            }
        
        categorical_count = sum(1 for r in results if r.data_type == "categorical")
        numerical_count = sum(1 for r in results if r.data_type == "numerical")
        total_processing_time = sum(r.processing_time for r in results)
        
        return {
            "total_columns": len(results),
            "categorical_columns": categorical_count,
            "numerical_columns": numerical_count,
            "total_processing_time": round(total_processing_time, 3)
        }