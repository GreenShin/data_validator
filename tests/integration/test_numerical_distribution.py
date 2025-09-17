"""
Integration Tests for Numerical Distribution Analysis

숫자형 데이터 분포 분석의 통합 테스트
"""

import pytest
import sys
import os
import pandas as pd
import tempfile
import numpy as np
from typing import List, Dict, Any

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# 실제 구현 import
from distribution.analyzer import DistributionAnalyzer
from distribution.config import DistributionConfig, ColumnConfig
from distribution.models import ColumnDistribution, NumericalDistribution, NumericalStats


class TestNumericalDistributionIntegration:
    """숫자형 분포 분석 통합 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        # 테스트용 숫자형 데이터 생성
        np.random.seed(42)  # 재현 가능한 결과를 위해
        
        self.test_data = {
            'price': [10.5, 20.3, 15.7, 25.1, 18.9, 30.0, 12.4, 22.8],
            'quantity': [1, 5, 3, 8, 2, 10, 4, 6],
            'score': [85.2, 92.1, 78.5, 88.9, 91.3, 76.8, 89.4, 82.7]
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
    
    def test_numerical_analysis_basic(self):
        """기본 숫자형 분석 테스트"""
        # 구현이 완료되었으므로 테스트 활성화
        config = DistributionConfig(
            enabled=True,
            columns=[ColumnConfig(name="price", type="numerical", auto_bins=True, bin_count=5)]
        )
        
        analyzer = DistributionAnalyzer(config)
        result = analyzer.analyze_column("price", self.df["price"].tolist())
        
        assert isinstance(result, ColumnDistribution)
        assert result.column_name == "price"
        assert result.data_type == "numerical"
        assert result.total_count == 8
        assert result.null_count == 0
        assert result.null_percentage == 0.0
        assert isinstance(result.distribution, NumericalDistribution)
        
        # 구간 정보 확인
        bins = result.distribution.bins
        assert len(bins) == 5  # 5개 구간
        assert result.distribution.auto_generated is True
        
        # 통계 정보 확인
        stats = result.distribution.stats
        assert stats is not None
        assert stats.min == 10.5
        assert stats.max == 30.0
        assert stats.mean == pytest.approx(19.6, rel=1e-1)
    
    def test_numerical_analysis_custom_bins(self):
        """사용자 정의 구간 숫자형 분석 테스트"""
        # 구현이 완료되었으므로 테스트 활성화
        custom_bins = [0, 15, 20, 25, 35]  # 사용자 정의 구간
        
        config = DistributionConfig(
            enabled=True,
            columns=[ColumnConfig(name="price", type="numerical", bins=custom_bins)]
        )
        
        analyzer = DistributionAnalyzer(config)
        result = analyzer.analyze_column("price", self.df["price"].tolist())
        
        assert isinstance(result, ColumnDistribution)
        assert result.data_type == "numerical"
        assert result.distribution.auto_generated is False
        
        # 구간 정보 확인
        bins = result.distribution.bins
        assert len(bins) == 4  # 4개 구간 (0-15, 15-20, 20-25, 25-35)
        
        # 각 구간의 범위 확인
        assert bins[0].range == (0, 15)
        assert bins[1].range == (15, 20)
        assert bins[2].range == (20, 25)
        assert bins[3].range == (25, 35)
    
    def test_numerical_analysis_with_nulls(self):
        """null 값이 포함된 숫자형 분석 테스트"""
        pytest.skip("Implementation not ready - will be enabled after core implementation")
    
    def test_numerical_analysis_performance(self):
        """숫자형 분석 성능 테스트"""
        pytest.skip("Implementation not ready - will be enabled after core implementation")


if __name__ == "__main__":
    pytest.main([__file__])