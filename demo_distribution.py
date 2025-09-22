#!/usr/bin/env python3
"""
컬럼 분포 분석 기능 데모

이 스크립트는 새로 구현된 컬럼 분포 분석 기능을 시연합니다.
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from distribution.analyzer import DistributionAnalyzer
from distribution.config import DistributionConfig, ColumnConfig
from distribution.models import DataType

def demo_categorical_analysis():
    """범주형 데이터 분석 데모"""
    print("=== 범주형 데이터 분석 데모 ===")
    
    # 테스트 데이터
    category_data = [
        "Electronics", "Books", "Electronics", "Clothing", 
        "Books", "Electronics", "Clothing", "Books", 
        "Electronics", "Books", "Clothing", "Electronics"
    ]
    
    # 설정
    config = DistributionConfig(
        enabled=True,
        columns=[ColumnConfig(name="category", type="categorical", max_categories=100)]
    )
    
    # 분석기 생성 및 분석 실행
    analyzer = DistributionAnalyzer(config)
    result = analyzer.analyze_column("category", category_data)
    
    # 결과 출력
    print(f"컬럼명: {result.column_name}")
    print(f"데이터 타입: {result.data_type}")
    print(f"전체 행 수: {result.total_count}")
    print(f"null 값 수: {result.null_count}")
    print(f"null 비율: {result.null_percentage:.2f}%")
    print(f"처리 시간: {result.processing_time:.4f}초")
    print()
    
    print("범주별 분포:")
    for category in result.distribution.categories:
        print(f"  {category.value}: {category.count}개 ({category.percentage:.2f}%)")
    
    if result.distribution.other_count > 0:
        print(f"  기타: {result.distribution.other_count}개 ({result.distribution.other_percentage:.2f}%)")
    
    print(f"고유값 총 개수: {result.distribution.unique_count}")
    print()

def demo_numerical_analysis():
    """숫자형 데이터 분석 데모"""
    print("=== 숫자형 데이터 분석 데모 ===")
    
    # 테스트 데이터
    price_data = [
        10.5, 20.3, 15.7, 25.1, 18.9, 30.0, 12.4, 22.8,
        35.2, 28.6, 19.3, 24.7, 16.8, 31.5, 14.2, 27.9
    ]
    
    # 설정
    config = DistributionConfig(
        enabled=True,
        columns=[ColumnConfig(name="price", type="numerical", auto_bins=True)]
    )
    
    # 분석기 생성 및 분석 실행
    analyzer = DistributionAnalyzer(config)
    result = analyzer.analyze_column("price", price_data)
    
    # 결과 출력
    print(f"컬럼명: {result.column_name}")
    print(f"데이터 타입: {result.data_type}")
    print(f"전체 행 수: {result.total_count}")
    print(f"null 값 수: {result.null_count}")
    print(f"null 비율: {result.null_percentage:.2f}%")
    print(f"처리 시간: {result.processing_time:.4f}초")
    print()
    
    # 통계 정보
    stats = result.distribution.statistics
    print("통계 정보:")
    print(f"  평균: {stats.mean:.2f}")
    print(f"  중앙값: {stats.median:.2f}")
    print(f"  표준편차: {stats.std:.2f}")
    print(f"  최솟값: {stats.min:.2f}")
    print(f"  최댓값: {stats.max:.2f}")
    print(f"  25% 분위수: {stats.q25:.2f}")
    print(f"  75% 분위수: {stats.q75:.2f}")
    print()
    
    # 구간별 분포
    print("구간별 분포:")
    for bin_info in result.distribution.bins:
        print(f"  {bin_info.range[0]:.1f} - {bin_info.range[1]:.1f}: {bin_info.count}개 ({bin_info.percentage:.2f}%)")
    
    print(f"자동 생성된 구간: {result.distribution.auto_generated}")
    print()

def demo_auto_detection():
    """자동 데이터 타입 감지 데모"""
    print("=== 자동 데이터 타입 감지 데모 ===")
    
    # 범주형 데이터
    categorical_data = ["A", "B", "C", "A", "B"]
    print(f"범주형 데이터: {categorical_data}")
    
    # 숫자형 데이터
    numerical_data = [1.0, 2.0, 3.0, 4.0, 5.0]
    print(f"숫자형 데이터: {numerical_data}")
    
    # 설정
    config = DistributionConfig(
        enabled=True,
        columns=[ColumnConfig(name="test", type="auto")]
    )
    
    # 분석기 생성
    analyzer = DistributionAnalyzer(config)
    
    # 자동 감지
    cat_type = analyzer.detect_data_type(categorical_data)
    num_type = analyzer.detect_data_type(numerical_data)
    
    print(f"범주형 데이터 감지 결과: {cat_type.value}")
    print(f"숫자형 데이터 감지 결과: {num_type.value}")
    print()

def main():
    """메인 함수"""
    print("컬럼 분포 분석 기능 데모")
    print("=" * 50)
    print()
    
    try:
        demo_categorical_analysis()
        demo_numerical_analysis()
        demo_auto_detection()
        
        print("모든 데모가 성공적으로 완료되었습니다! 🎉")
        
    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
