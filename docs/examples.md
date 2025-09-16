# 사용 예제 및 튜토리얼

CSV 구문정확성 검증 프로그램의 다양한 사용 예제와 튜토리얼을 제공합니다.

## 📚 목차

- [기본 사용법](#기본-사용법)
- [실제 시나리오 예제](#실제-시나리오-예제)
- [고급 사용법](#고급-사용법)
- [문제 해결 예제](#문제-해결-예제)
- [자동화 스크립트](#자동화-스크립트)

## 기본 사용법

### 1단계: 첫 번째 검증

```bash
# 1. 샘플 설정 파일 생성
python -m src.main init -o my_first_config.yml

# 2. CSV 파일 검증
python -m src.main validate -c my_first_config.yml -i your_data.csv

# 3. 결과 확인
ls -la *.md *.html *.json
```

### 2단계: 상세한 검증

```bash
# 상세 로그와 함께 검증
python -m src.main validate -c my_first_config.yml -i your_data.csv -v

# HTML 형식으로 결과 저장
python -m src.main validate -c my_first_config.yml -i your_data.csv --format html
```

## 실제 시나리오 예제

### 시나리오 1: 고객 데이터 검증

**상황**: 고객 정보가 담긴 CSV 파일의 품질을 검증해야 합니다.

**CSV 파일 구조**:
```csv
customer_id,name,email,age,phone,join_date
1,김철수,kim@example.com,30,010-1234-5678,2023-01-15
2,이영희,lee@example.com,25,010-2345-6789,2023-02-20
3,박민수,park@example.com,35,010-3456-7890,2023-03-10
```

**설정 파일** (`customer_config.yml`):
```yaml
file_info:
  expected_rows: 1000
  encoding: "utf-8"
  delimiter: ","
  has_header: true

columns:
  - name: "customer_id"
    type: "integer"
    required: true
    range:
      min: 1
      max: 999999

  - name: "name"
    type: "string"
    required: true
    length:
      min: 2
      max: 50

  - name: "email"
    type: "email"
    required: true

  - name: "age"
    type: "integer"
    required: true
    range:
      min: 18
      max: 100

  - name: "phone"
    type: "string"
    required: true
    pattern: "^010-\\d{4}-\\d{4}$"

  - name: "join_date"
    type: "datetime"
    required: true
    format: "%Y-%m-%d"
```

**검증 실행**:
```bash
python -m src.main validate -c customer_config.yml -i customers.csv -v
```

### 시나리오 2: 제품 재고 데이터 검증

**상황**: 제품 재고 정보의 정확성을 검증해야 합니다.

**CSV 파일 구조**:
```csv
product_code;product_name;category;price;stock;last_updated
P001;노트북;전자제품;1500000;50;2023-12-01 10:30:00
P002;마우스;전자제품;25000;200;2023-12-01 11:15:00
P003;키보드;전자제품;80000;150;2023-12-01 12:00:00
```

**설정 파일** (`inventory_config.yml`):
```yaml
file_info:
  expected_rows: null  # 행 수 제한 없음
  encoding: "utf-8"
  delimiter: ";"  # 세미콜론 구분자
  has_header: true

columns:
  - name: "product_code"
    type: "string"
    required: true
    pattern: "^P\\d{3}$"  # P001, P002 형식

  - name: "product_name"
    type: "string"
    required: true
    length:
      min: 1
      max: 100

  - name: "category"
    type: "string"
    required: true
    allowed_values: ["전자제품", "의류", "도서", "식품"]
    case_sensitive: false

  - name: "price"
    type: "integer"
    required: true
    range:
      min: 0
      max: 10000000

  - name: "stock"
    type: "integer"
    required: true
    range:
      min: 0
      max: 10000

  - name: "last_updated"
    type: "datetime"
    required: true
    format: "%Y-%m-%d %H:%M:%S"
```

**검증 실행**:
```bash
python -m src.main validate -c inventory_config.yml -i inventory.csv -v
```

### 시나리오 3: 학생 성적 데이터 검증

**상황**: 학생 성적 데이터의 형식과 범위를 검증해야 합니다.

**CSV 파일 구조**:
```csv
student_id,name,math,english,science,grade
2023001,김학생,85,92,78,A
2023002,이학생,95,88,91,A
2023003,박학생,72,85,79,B
```

**설정 파일** (`grades_config.yml`):
```yaml
file_info:
  expected_rows: 100
  encoding: "utf-8"
  delimiter: ","
  has_header: true

columns:
  - name: "student_id"
    type: "string"
    required: true
    pattern: "^2023\\d{3}$"  # 2023001 형식

  - name: "name"
    type: "string"
    required: true
    length:
      min: 2
      max: 20

  - name: "math"
    type: "integer"
    required: true
    range:
      min: 0
      max: 100

  - name: "english"
    type: "integer"
    required: true
    range:
      min: 0
      max: 100

  - name: "science"
    type: "integer"
    required: true
    range:
      min: 0
      max: 100

  - name: "grade"
    type: "string"
    required: true
    allowed_values: ["A", "B", "C", "D", "F"]
    case_sensitive: true
```

**검증 실행**:
```bash
python -m src.main validate -c grades_config.yml -i grades.csv -v
```

## 고급 사용법

### 자동 설정 생성 활용

```bash
# 1. CSV 파일 분석하여 자동 설정 생성
python -m src.main analyze -i data.csv -o auto_config.yml -v

# 2. 생성된 설정 파일 검토 및 수정
cat auto_config.yml

# 3. 수정된 설정으로 검증 실행
python -m src.main validate -c auto_config.yml -i data.csv -v
```

### 배치 처리

```bash
# 폴더 내 모든 CSV 파일 검증
python -m src.main validate -c config.yml -i /data/csv_files -o /results -v

# 특정 패턴의 파일만 검증 (스크립트 활용)
find /data -name "*.csv" -exec python -m src.main validate -c config.yml -i {} -o /results \;
```

### 로그 파일 활용

```bash
# 로그 파일에 상세 정보 저장
python -m src.main validate -c config.yml -i data.csv --log-file validation.log -v

# 로그 파일 확인
tail -f validation.log
```

## 문제 해결 예제

### 문제 1: 인코딩 오류

**오류 메시지**:
```
UnicodeDecodeError: 'utf-8' codec can't decode byte 0xc7 in position 0
```

**해결 방법**:
```bash
# 1. 인코딩 감지
python -c "
import chardet
with open('data.csv', 'rb') as f:
    result = chardet.detect(f.read(10000))
    print(f'감지된 인코딩: {result}')
"

# 2. 설정 파일에서 올바른 인코딩 지정
# config.yml
file_info:
  encoding: "cp949"  # 또는 "euc-kr"
```

### 문제 2: 구분자 인식 오류

**오류 메시지**:
```
CSV 구조 오류: Expected 3 columns, got 1
```

**해결 방법**:
```bash
# 1. 파일 내용 확인
head -5 data.csv

# 2. 구분자 수동 지정
# config.yml
file_info:
  delimiter: ";"  # 또는 "\t", "|"
```

### 문제 3: 날짜 형식 오류

**오류 메시지**:
```
값 '2023/01/15'은 날짜/시간 형식 '%Y-%m-%d'과 일치하지 않습니다
```

**해결 방법**:
```yaml
# config.yml
columns:
  - name: "date"
    type: "datetime"
    required: true
    format: "%Y/%m/%d"  # 올바른 형식 지정
```

### 문제 4: 대용량 파일 처리

**상황**: 100만 행 이상의 대용량 파일 처리

**해결 방법**:
```bash
# 스트리밍 방식으로 자동 처리 (기본 기능)
python -m src.main validate -c config.yml -i large_file.csv -v

# 메모리 사용량 모니터링
python -m src.main validate -c config.yml -i large_file.csv --log-file memory.log -v
```

## 자동화 스크립트

### 1. 일일 데이터 검증 스크립트

```bash
#!/bin/bash
# daily_validation.sh

# 설정
CONFIG_FILE="config.yml"
DATA_DIR="/data/daily"
RESULTS_DIR="/results/daily"
LOG_FILE="/logs/validation_$(date +%Y%m%d).log"

# 디렉토리 생성
mkdir -p "$RESULTS_DIR"
mkdir -p "$(dirname "$LOG_FILE")"

# 검증 실행
echo "일일 데이터 검증 시작: $(date)"
python -m src.main validate \
    -c "$CONFIG_FILE" \
    -i "$DATA_DIR" \
    -o "$RESULTS_DIR" \
    --log-file "$LOG_FILE" \
    -v

# 결과 요약
echo "검증 완료: $(date)"
echo "결과 파일: $RESULTS_DIR"
echo "로그 파일: $LOG_FILE"

# 이메일 알림 (선택적)
# mail -s "일일 데이터 검증 완료" admin@company.com < "$LOG_FILE"
```

### 2. Python 자동화 스크립트

```python
#!/usr/bin/env python3
"""
데이터 검증 자동화 스크립트
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from src.core.validator import CSVValidator
from src.utils.formatter import ReportFormatter

def main():
    # 설정
    config_file = "config.yml"
    data_dir = Path("/data/csv_files")
    results_dir = Path("/results")
    log_file = f"validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # 디렉토리 생성
    results_dir.mkdir(parents=True, exist_ok=True)
    
    # 검증기 초기화
    validator = CSVValidator(config_file, verbose=True, log_file=str(log_file))
    formatter = ReportFormatter()
    
    try:
        # CSV 파일 찾기
        csv_files = list(data_dir.glob("*.csv"))
        
        if not csv_files:
            print("검증할 CSV 파일을 찾을 수 없습니다.")
            return
        
        print(f"총 {len(csv_files)}개의 CSV 파일을 발견했습니다.")
        
        # 각 파일 검증
        all_results = []
        for csv_file in csv_files:
            print(f"검증 중: {csv_file.name}")
            
            try:
                result = validator.validate_file(str(csv_file))
                all_results.append(result)
                
                # 개별 결과 저장
                timestamp = result.timestamp.strftime("%Y%m%d_%H%M%S")
                base_name = csv_file.stem
                output_file = results_dir / f"{base_name}_{timestamp}"
                
                # Markdown 리포트 저장
                markdown_report = formatter.generate_markdown_report(result)
                formatter.save_report(markdown_report, str(output_file), "markdown")
                
                print(f"  결과: {'✅ 성공' if result.structural_valid and result.format_valid else '❌ 실패'}")
                print(f"  오류 수: {len(result.errors)}")
                
            except Exception as e:
                print(f"  오류: {e}")
                continue
        
        # 전체 결과 요약
        print("\n=== 전체 결과 요약 ===")
        total_files = len(all_results)
        successful_files = sum(1 for r in all_results if r.structural_valid and r.format_valid)
        total_errors = sum(len(r.errors) for r in all_results)
        total_time = sum(r.processing_time for r in all_results)
        
        print(f"총 파일 수: {total_files}")
        print(f"성공한 파일: {successful_files}")
        print(f"실패한 파일: {total_files - successful_files}")
        print(f"총 오류 수: {total_errors}")
        print(f"총 처리 시간: {total_time:.2f}초")
        
        if total_time > 0:
            total_rows = sum(r.total_rows for r in all_results)
            print(f"평균 처리 속도: {total_rows/total_time:.0f} 행/초")
        
    except Exception as e:
        print(f"스크립트 실행 중 오류 발생: {e}")
        sys.exit(1)
    
    finally:
        validator.close()

if __name__ == "__main__":
    main()
```

### 3. 웹 대시보드 연동 스크립트

```python
#!/usr/bin/env python3
"""
검증 결과를 웹 대시보드에 전송하는 스크립트
"""

import json
import requests
from src.core.validator import CSVValidator
from src.utils.formatter import ReportFormatter

def send_to_dashboard(result):
    """검증 결과를 웹 대시보드에 전송"""
    
    # JSON 형식으로 결과 변환
    formatter = ReportFormatter()
    json_report = formatter.generate_json_report(result)
    data = json.loads(json_report)
    
    # 대시보드 API 엔드포인트
    dashboard_url = "https://dashboard.company.com/api/validation-results"
    
    try:
        response = requests.post(dashboard_url, json=data)
        response.raise_for_status()
        print(f"✅ 대시보드 전송 성공: {result.file_name}")
        
    except requests.RequestException as e:
        print(f"❌ 대시보드 전송 실패: {e}")

def main():
    # 검증 실행
    validator = CSVValidator("config.yml")
    result = validator.validate_file("data.csv")
    
    # 대시보드에 전송
    send_to_dashboard(result)
    
    validator.close()

if __name__ == "__main__":
    main()
```

### 4. CI/CD 파이프라인 통합

```yaml
# .github/workflows/data-validation.yml
name: Data Validation

on:
  schedule:
    - cron: '0 2 * * *'  # 매일 오전 2시 실행
  workflow_dispatch:  # 수동 실행 가능

jobs:
  validate:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run data validation
      run: |
        python -m src.main validate -c config.yml -i data/ -o results/ -v
    
    - name: Upload results
      uses: actions/upload-artifact@v3
      with:
        name: validation-results
        path: results/
    
    - name: Send notification
      if: failure()
      run: |
        echo "데이터 검증 실패" | mail -s "Validation Failed" admin@company.com
```

## 성능 최적화 팁

### 1. 청크 크기 조정

```python
# 대용량 파일의 경우 청크 크기를 조정
from src.utils.file_handler import FileHandler

handler = FileHandler()
for chunk in handler.read_csv_streaming("large_file.csv", config, chunk_size=5000):
    # 더 큰 청크로 처리 속도 향상
    pass
```

### 2. 병렬 처리

```python
import concurrent.futures
from src.core.validator import CSVValidator

def validate_file_parallel(file_path):
    validator = CSVValidator("config.yml")
    return validator.validate_file(file_path)

# 여러 파일을 병렬로 검증
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(validate_file_parallel, path) for path in csv_files]
    results = [future.result() for future in futures]
```

### 3. 메모리 모니터링

```python
import psutil
import os

def monitor_memory():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    print(f"메모리 사용량: {memory_info.rss / 1024 / 1024:.2f} MB")

# 검증 전후 메모리 사용량 확인
monitor_memory()
result = validator.validate_file("large_file.csv")
monitor_memory()
```

---

이 예제들을 참조하여 다양한 상황에서 CSV 구문정확성 검증 프로그램을 효과적으로 활용할 수 있습니다. 추가 질문이나 도움이 필요하시면 이슈를 생성해 주세요.
