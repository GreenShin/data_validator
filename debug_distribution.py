#!/usr/bin/env python3
"""
분포 분석 결과 디버깅 스크립트
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from core.validator import DataValidator

def main():
    print("분포 분석 결과 디버깅 시작...")
    
    # DataValidator 초기화
    validator = DataValidator('sample_config.yml', verbose=True)
    validator.enable_distribution_analysis()
    
    # 파일 검증
    result = validator.validate_file('test_data_with_distribution.csv')
    
    # 결과 확인
    print(f"\n=== ValidationResult 객체 정보 ===")
    print(f"분포 분석 속성 존재: {hasattr(result, 'distribution_analysis')}")
    print(f"분포 분석 값: {result.distribution_analysis}")
    print(f"분포 분석 타입: {type(result.distribution_analysis)}")
    
    if result.distribution_analysis:
        print(f"분포 분석 컬럼 수: {len(result.distribution_analysis)}")
        for column_name, analysis_result in result.distribution_analysis.items():
            print(f"  - {column_name}: {type(analysis_result)}")
    
    # to_dict() 결과 확인
    result_dict = result.to_dict()
    print(f"\n=== to_dict() 결과 ===")
    print(f"분포 분석 키 존재: {'distribution_analysis' in result_dict}")
    if 'distribution_analysis' in result_dict:
        print(f"분포 분석 값: {result_dict['distribution_analysis']}")
    
    validator.close()

if __name__ == "__main__":
    main()
