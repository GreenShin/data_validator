#!/usr/bin/env python3
"""
대용량 CSV 파일 생성 스크립트
"""

import csv
import random
from datetime import datetime, timedelta

def generate_large_csv(filename, num_rows=10000):
    """대용량 CSV 파일을 생성합니다."""
    
    # 샘플 데이터
    names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve', 'Frank', 'Grace', 'Henry', 'Ivy', 'Jack']
    categories = ['A', 'B', 'C', 'D', 'E']
    domains = ['example.com', 'test.org', 'demo.net', 'sample.co.kr']
    
    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        
        # 헤더 작성
        writer.writerow(['id', 'name', 'email', 'age', 'category', 'created_date'])
        
        # 데이터 생성
        start_date = datetime(2020, 1, 1)
        
        for i in range(1, num_rows + 1):
            name = random.choice(names)
            domain = random.choice(domains)
            email = f"{name.lower()}{i}@{domain}"
            age = random.randint(18, 80)
            category = random.choice(categories)
            
            # 날짜 생성 (2020-2025 사이)
            days_offset = random.randint(0, 1825)  # 5년
            created_date = start_date + timedelta(days=days_offset)
            
            writer.writerow([
                i,
                name,
                email,
                age,
                category,
                created_date.strftime('%Y-%m-%d %H:%M:%S')
            ])
            
            # 진행률 표시
            if i % 1000 == 0:
                print(f"생성 중... {i:,}/{num_rows:,} ({i/num_rows*100:.1f}%)")

if __name__ == '__main__':
    print("대용량 CSV 파일 생성 중...")
    generate_large_csv('large_test_data.csv', 10000)
    print("✅ 대용량 CSV 파일 생성 완료: large_test_data.csv")
