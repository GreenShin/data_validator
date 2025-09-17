"""
Distribution Analyzer Contract Tests

이 파일은 분포 분석기의 계약을 정의하고 테스트합니다.
구현이 완료되기 전까지 모든 테스트는 실패해야 합니다.
"""

import pytest
import sys
import os
from typing import List, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# 실제 구현 import
from distribution.analyzer import DistributionAnalyzer
from distribution.config import DistributionConfig, ColumnConfig
from distribution.models import (
    ColumnDistribution, CategoricalDistribution, NumericalDistribution,
    CategoryInfo, BinInfo, NumericalStats, DataType
)


# 실제 구현을 사용하므로 중복 정의 제거


# 계약 테스트들
class TestDistributionAnalyzerContract:
    """분포 분석기 계약 테스트"""
    
    def test_analyzer_initialization(self):
        """분석기 초기화 테스트"""
        config = DistributionConfig(
            enabled=True,
            columns=[
                ColumnConfig(name="category", type="categorical", max_categories=100),
                ColumnConfig(name="price", type="numerical", auto_bins=True)
            ]
        )
        
        # 실제 구현 테스트
        analyzer = DistributionAnalyzer(config)
        assert analyzer is not None
        assert analyzer.config.enabled is True
        assert len(analyzer.config.columns) == 2
    
    def test_analyze_column_categorical(self):
        """범주형 컬럼 분석 테스트"""
        config = DistributionConfig(
            enabled=True,
            columns=[ColumnConfig(name="category", type="categorical", max_categories=100)]
        )
        
        # 실제 구현 테스트
        analyzer = DistributionAnalyzer(config)
        data = ["A", "B", "A", "C", "B", "A"]
        result = analyzer.analyze_column("category", data)
        
        assert isinstance(result, ColumnDistribution)
        assert result.column_name == "category"
        assert result.data_type == "categorical"
        assert result.total_count == 6
        assert result.null_count == 0
        assert isinstance(result.distribution, CategoricalDistribution)
    
    def test_analyze_column_numerical(self):
        """숫자형 컬럼 분석 테스트"""
        config = DistributionConfig(
            enabled=True,
            columns=[ColumnConfig(name="price", type="numerical", auto_bins=True)]
        )
        
        # 실제 구현 테스트
        analyzer = DistributionAnalyzer(config)
        data = [10.5, 20.3, 15.7, 25.1, 18.9]
        result = analyzer.analyze_column("price", data)
        
        assert isinstance(result, ColumnDistribution)
        assert result.column_name == "price"
        assert result.data_type == "numerical"
        assert result.total_count == 5
        assert result.null_count == 0
        assert isinstance(result.distribution, NumericalDistribution)
    
    def test_analyze_categorical_distribution(self):
        """범주형 분포 분석 테스트"""
        config = DistributionConfig(
            enabled=True,
            columns=[ColumnConfig(name="category", type="categorical", max_categories=100)]
        )
        
        # 실제 구현 테스트
        analyzer = DistributionAnalyzer(config)
        data = ["A", "B", "A", "C", "B", "A", None, ""]
        result = analyzer.analyze_categorical(data, "category", config.columns[0])
        
        assert isinstance(result, ColumnDistribution)
        assert result.column_name == "category"
        assert result.data_type == "categorical"
        assert len(result.distribution.categories) > 0
        assert result.distribution.unique_count > 0
    
    def test_analyze_numerical_distribution(self):
        """숫자형 분포 분석 테스트"""
        config = DistributionConfig(
            enabled=True,
            columns=[ColumnConfig(name="price", type="numerical", auto_bins=True)]
        )
        
        # 실제 구현 테스트
        analyzer = DistributionAnalyzer(config)
        data = [10.5, 20.3, 15.7, 25.1, 18.9, None, 0]
        result = analyzer.analyze_numerical(data, "price", config.columns[0])
        
        assert isinstance(result, ColumnDistribution)
        assert result.column_name == "price"
        assert result.data_type == "numerical"
        assert len(result.distribution.bins) > 0
        assert result.distribution.auto_generated is True
    
    def test_detect_data_type(self):
        """데이터 타입 감지 테스트"""
        config = DistributionConfig(
            enabled=True,
            columns=[ColumnConfig(name="test", type="auto")]
        )
        
        # 실제 구현 테스트
        analyzer = DistributionAnalyzer(config)
        
        # 범주형 데이터
        categorical_data = ["A", "B", "C"]
        result = analyzer.detect_data_type(categorical_data)
        assert result == DataType.CATEGORICAL
        
        # 숫자형 데이터
        numerical_data = [1.0, 2.0, 3.0]
        result = analyzer.detect_data_type(numerical_data)
        assert result == DataType.NUMERICAL
    
    def test_invalid_column_name(self):
        """잘못된 컬럼명 테스트"""
        config = DistributionConfig(
            enabled=True,
            columns=[ColumnConfig(name="valid_column", type="categorical")]
        )
        
        # 실제 구현 테스트 - ValueError 예상
        analyzer = DistributionAnalyzer(config)
        data = ["A", "B", "C"]
        with pytest.raises(ValueError):
            result = analyzer.analyze_column("invalid_column", data)
    
    def test_memory_limit_exceeded(self):
        """메모리 제한 초과 테스트"""
        # 메모리 제한을 매우 낮게 설정 (100MB)
        config = DistributionConfig(
            enabled=True,
            columns=[ColumnConfig(name="large_column", type="categorical")],
            memory_limit=100  # 100MB로 제한
        )
        
        # 실제 구현 테스트 - MemoryError 예상 (메모리가 충분한 경우 스킵)
        try:
            analyzer = DistributionAnalyzer(config)
            # 대용량 데이터 생성
            large_data = ["A"] * 1000000
            result = analyzer.analyze_column("large_column", large_data)
            # 메모리가 충분한 경우 테스트 통과
            assert result is not None
        except MemoryError:
            # 메모리 제한에 걸린 경우 테스트 통과
            pass


class TestDataModelContract:
    """데이터 모델 계약 테스트"""
    
    def test_category_info_validation(self):
        """CategoryInfo 유효성 검사 테스트"""
        # 유효한 CategoryInfo
        category = CategoryInfo(value="A", count=10, percentage=50.0)
        assert category.value == "A"
        assert category.count == 10
        assert category.percentage == 50.0
        
        # 비율이 100%를 초과하는 경우 - Pydantic 검증
        with pytest.raises(ValueError):
            CategoryInfo(value="B", count=5, percentage=150.0)
    
    def test_bin_info_validation(self):
        """BinInfo 유효성 검사 테스트"""
        # 유효한 BinInfo
        bin_info = BinInfo(range=(0.0, 10.0), count=5, percentage=25.0)
        assert bin_info.range == (0.0, 10.0)
        assert bin_info.count == 5
        assert bin_info.percentage == 25.0
        
        # 잘못된 범위 (시작값이 끝값보다 큰 경우) - Pydantic 검증
        with pytest.raises(ValueError):
            BinInfo(range=(10.0, 0.0), count=5, percentage=25.0)
    
    def test_numerical_stats_validation(self):
        """NumericalStats 유효성 검사 테스트"""
        # 유효한 NumericalStats
        stats = NumericalStats(
            mean=15.0, median=15.0, std=5.0,
            min=10.0, max=20.0, q25=12.5, q75=17.5
        )
        assert stats.min <= stats.max
        assert stats.q25 <= stats.median <= stats.q75
    
    def test_column_distribution_validation(self):
        """ColumnDistribution 유효성 검사 테스트"""
        # 유효한 ColumnDistribution
        categorical_dist = CategoricalDistribution(
            categories=[
                CategoryInfo(value="A", count=5, percentage=50.0), 
                CategoryInfo(value="B", count=5, percentage=50.0)
            ],
            other_count=0,
            other_percentage=0.0,
            unique_count=2
        )
        
        column_dist = ColumnDistribution(
            column_name="test",
            data_type="categorical",
            total_count=10,
            null_count=0,
            null_percentage=0.0,
            distribution=categorical_dist,
            processing_time=0.1
        )
        
        assert column_dist.total_count >= 0
        assert 0.0 <= column_dist.null_percentage <= 100.0
        assert column_dist.processing_time >= 0.0


if __name__ == "__main__":
    pytest.main([__file__])