"""
Integration Tests for Categorical Distribution Analysis

범주형 데이터 분포 분석의 통합 테스트
"""

import pytest
import sys
import os
import pandas as pd
import tempfile
from typing import List, Dict, Any

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# 실제 구현 import
from distribution.analyzer import DistributionAnalyzer
from distribution.config import DistributionConfig, ColumnConfig
from distribution.models import ColumnDistribution, CategoricalDistribution


class TestCategoricalDistributionIntegration:
    """범주형 분포 분석 통합 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        # 테스트용 CSV 데이터 생성
        self.test_data = {
            'category': ['Electronics', 'Books', 'Electronics', 'Clothing', 'Books', 'Electronics'],
            'status': ['Active', 'Inactive', 'Active', 'Active', 'Inactive', 'Active'],
            'region': ['North', 'South', 'North', 'East', 'West', 'North']
        }
        self.df = pd.DataFrame(self.test_data)
        
        # 임시 CSV 파일 생성
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.df.to_csv(self.temp_file.name, index=False)
        self.temp_file.close()
    
    def teardown_method(self):
        """각 테스트 메서드 실행 후 정리"""
        if os.path.exists(self.temp_file.name):
            os.unlink(self.temp_file.name)
    
    def test_categorical_analysis_basic(self):
        """기본 범주형 분석 테스트"""
        # 구현이 완료되었으므로 테스트 활성화
        config = DistributionConfig(
            enabled=True,
            columns=[ColumnConfig(name="category", type="categorical", max_categories=100)]
        )
        
        analyzer = DistributionAnalyzer(config)
        result = analyzer.analyze_column("category", self.df["category"].tolist())
        
        assert isinstance(result, ColumnDistribution)
        assert result.column_name == "category"
        assert result.data_type == "categorical"
        assert result.total_count == 6
        assert result.null_count == 0
        assert result.null_percentage == 0.0
        assert isinstance(result.distribution, CategoricalDistribution)
        
        # Electronics가 3개, Books가 2개, Clothing이 1개
        categories = result.distribution.categories
        assert len(categories) == 3
        
        # Electronics 확인
        electronics = next(cat for cat in categories if cat.value == "Electronics")
        assert electronics.count == 3
        assert electronics.percentage == 50.0
        
        # Books 확인
        books = next(cat for cat in categories if cat.value == "Books")
        assert books.count == 2
        assert books.percentage == pytest.approx(33.33, rel=1e-2)
        
        # Clothing 확인
        clothing = next(cat for cat in categories if cat.value == "Clothing")
        assert clothing.count == 1
        assert clothing.percentage == pytest.approx(16.67, rel=1e-2)
    
    def test_categorical_analysis_with_nulls(self):
        """null 값이 포함된 범주형 분석 테스트"""
        # 구현이 완료되었으므로 테스트 활성화
        data_with_nulls = ['A', 'B', None, 'A', '', 'B', 'A']
        
        config = DistributionConfig(
            enabled=True,
            columns=[ColumnConfig(name="test_col", type="categorical", max_categories=100)]
        )
        
        analyzer = DistributionAnalyzer(config)
        result = analyzer.analyze_column("test_col", data_with_nulls)
        
        assert result.total_count == 7
        assert result.null_count == 2  # None과 '' 모두 null로 처리
        assert result.null_percentage == pytest.approx(28.57, rel=1e-2)
    
    def test_categorical_analysis_high_cardinality(self):
        """높은 카디널리티 범주형 분석 테스트"""
        pytest.skip("Implementation not ready - will be enabled after core implementation")
        
        # TODO: 1000개 이상의 고유값을 가진 데이터로 테스트
        # high_cardinality_data = [f"category_{i}" for i in range(1500)]
        # 
        # config = DistributionConfig(
        #     enabled=True,
        #     columns=[ColumnConfig(name="high_card_col", type="categorical", max_categories=1000)]
        # )
        # 
        # analyzer = DistributionAnalyzer(config)
        # result = analyzer.analyze_column("high_card_col", high_cardinality_data)
        # 
        # assert result.distribution.unique_count == 1500
        # assert result.distribution.other_count > 0  # 1000개 제한으로 인한 "기타" 카테고리
        # assert result.distribution.other_percentage > 0
    
    def test_categorical_analysis_case_sensitivity(self):
        """대소문자 구분 범주형 분석 테스트"""
        pytest.skip("Implementation not ready - will be enabled after core implementation")
        
        # TODO: 대소문자가 다른 범주들로 테스트
        # case_sensitive_data = ['Apple', 'apple', 'APPLE', 'Banana', 'banana']
        # 
        # config = DistributionConfig(
        #     enabled=True,
        #     columns=[ColumnConfig(name="case_col", type="categorical", max_categories=100)]
        # )
        # 
        # analyzer = DistributionAnalyzer(config)
        # result = analyzer.analyze_column("case_col", case_sensitive_data)
        # 
        # # 대소문자를 구분하므로 5개의 서로 다른 범주
        # assert len(result.distribution.categories) == 5
    
    def test_categorical_analysis_empty_data(self):
        """빈 데이터 범주형 분석 테스트"""
        pytest.skip("Implementation not ready - will be enabled after core implementation")
        
        # TODO: 빈 데이터로 테스트
        # config = DistributionConfig(
        #     enabled=True,
        #     columns=[ColumnConfig(name="empty_col", type="categorical", max_categories=100)]
        # )
        # 
        # analyzer = DistributionAnalyzer(config)
        # result = analyzer.analyze_column("empty_col", [])
        # 
        # assert result.total_count == 0
        # assert result.null_count == 0
        # assert len(result.distribution.categories) == 0
    
    def test_categorical_analysis_single_value(self):
        """단일 값 범주형 분석 테스트"""
        pytest.skip("Implementation not ready - will be enabled after core implementation")
        
        # TODO: 모든 값이 동일한 데이터로 테스트
        # single_value_data = ['A'] * 100
        # 
        # config = DistributionConfig(
        #     enabled=True,
        #     columns=[ColumnConfig(name="single_col", type="categorical", max_categories=100)]
        # )
        # 
        # analyzer = DistributionAnalyzer(config)
        # result = analyzer.analyze_column("single_col", single_value_data)
        # 
        # assert result.total_count == 100
        # assert len(result.distribution.categories) == 1
        # assert result.distribution.categories[0].value == 'A'
        # assert result.distribution.categories[0].count == 100
        # assert result.distribution.categories[0].percentage == 100.0
    
    def test_categorical_analysis_performance(self):
        """범주형 분석 성능 테스트"""
        pytest.skip("Implementation not ready - will be enabled after core implementation")
        
        # TODO: 대용량 데이터로 성능 테스트
        # import time
        # large_data = ['A', 'B', 'C'] * 100000  # 30만 개 데이터
        # 
        # config = DistributionConfig(
        #     enabled=True,
        #     columns=[ColumnConfig(name="perf_col", type="categorical", max_categories=100)]
        # )
        # 
        # analyzer = DistributionAnalyzer(config)
        # start_time = time.time()
        # result = analyzer.analyze_column("perf_col", large_data)
        # end_time = time.time()
        # 
        # processing_time = end_time - start_time
        # assert processing_time < 5.0  # 5초 이내 처리
        # assert result.processing_time < 5.0


if __name__ == "__main__":
    pytest.main([__file__])