# 데이터 파일 구문정확성 검증 프로그램

[![Python Version](https://img.shields.io/badge/python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](LICENSE)
[![Status](https://img.shields.io/badge/status-stable-brightgreen.svg)]()

CSV, JSON, JSONL 파일의 구문정확성을 자동으로 검증하고 상세한 결과 리포트를 생성하는 Python 프로그램입니다.

## ✨ 주요 기능

### 🔍 구조정확성 검증
- **CSV**: 포맷 규칙 준수 여부, 구분자 일관성, 헤더 행 검증
- **JSON**: JSON 스키마 검증, 중첩 구조 일관성 확인
- **JSONL**: 각 라인의 JSON 형식 검증, 구조 일관성 확인
- **인코딩 호환성 검증**: UTF-8/ASCII, CP949/EUC-KR 등 호환 인코딩 지원
- 행 수 및 컬럼 구조 일관성 검증

### 📝 형식정확성 검증
- **데이터 타입 검증**: 정수, 실수, 문자열, 날짜/시간, 불린, 이메일, 전화번호, 객체, 배열, null
- **범위 검증**: 숫자 범위, 문자열 길이, 날짜 범위
- **범주형 데이터 검증**: 허용된 값 목록 확인
- **정규표현식 패턴 검증**: 사용자 정의 패턴 매칭
- **JSON 특화 검증**: 중첩 객체/배열 구조, JSON 스키마 준수

### 📊 상세한 결과 리포트
- **Markdown**: 읽기 쉬운 텍스트 리포트
- **HTML**: 웹 브라우저용 아름다운 리포트
- **JSON**: 프로그래밍 처리용 구조화된 데이터
- 오류 상세 정보, 통계, 권장사항 제공

### 🚀 사용자 친화적 인터페이스
- 직관적인 명령행 인터페이스
- 실시간 진행률 표시
- 상세한 로깅 및 오류 메시지
- 자동 설정 파일 생성

## 🛠️ 설치 방법

### 요구사항
- Python 3.8 이상
- pip (Python 패키지 관리자)

### 설치
```bash
# 저장소 클론
git clone <repository-url>
cd csv_validator

# 의존성 설치
pip install -r requirements.txt

# 또는 개발 모드로 설치
pip install -e .
```

### 의존성
```
pandas>=1.5.0
PyYAML>=6.0
pydantic>=2.0
click>=8.0
rich>=13.0
python-dateutil>=2.8
email-validator>=2.0
phonenumbers>=8.13
chardet>=5.0
```

## 🚀 빠른 시작

### 1. 샘플 설정 파일 생성
```bash
# CSV용 설정 파일
python -m src.main init -t csv -o csv_config.yml

# JSON용 설정 파일
python -m src.main init -t json -o json_config.yml

# JSONL용 설정 파일
python -m src.main init -t jsonl -o jsonl_config.yml
```

### 2. 파일 검증
```bash
# CSV 파일 검증
python -m src.main validate -c csv_config.yml -i data.csv

# JSON 파일 검증
python -m src.main validate -c json_config.yml -i data.json

# JSONL 파일 검증
python -m src.main validate -c jsonl_config.yml -i data.jsonl

# 폴더 내 모든 파일 검증
python -m src.main validate -c config.yml -i /path/to/files
```

### 3. 결과 확인
검증 결과가 Markdown, HTML, JSON 형식으로 자동 생성됩니다.

## 📖 사용법

### 기본 명령어

#### `validate` - 파일 검증 (CSV, JSON, JSONL 지원)
```bash
# 단일 파일 검증
python -m src.main validate -c config.yml -i data.csv
python -m src.main validate -c config.yml -i data.json
python -m src.main validate -c config.yml -i data.jsonl

# 폴더 내 모든 지원되는 파일 검증
python -m src.main validate -c config.yml -i /path/to/files -o /path/to/results

# 상세 로그와 함께 검증
python -m src.main validate -c config.yml -i data.json -v

# 특정 형식으로 결과 저장
python -m src.main validate -c config.yml -i data.jsonl --format html
```

#### `init` - 샘플 설정 파일 생성
```bash
# 기본 CSV 샘플 설정 생성
python -m src.main init

# 파일 타입별 샘플 설정 생성
python -m src.main init -t csv -o csv_config.yml
python -m src.main init -t json -o json_config.yml
python -m src.main init -t jsonl -o jsonl_config.yml

# 사용자 정의 경로에 생성
python -m src.main init -o my_config.yml
```

#### `check-config` - 설정 파일 유효성 검사
```bash
python -m src.main check-config -c config.yml
```

#### `analyze` - 파일 자동 분석 (CSV, JSON, JSONL 지원)
```bash
# 파일 분석하여 자동 설정 생성
python -m src.main analyze -i data.csv -o auto_csv_config.yml
python -m src.main analyze -i data.json -o auto_json_config.yml
python -m src.main analyze -i data.jsonl -o auto_jsonl_config.yml
```

### 명령행 옵션

| 옵션 | 설명 | 기본값 |
|------|------|--------|
| `-c, --config` | YAML 설정 파일 경로 | 필수 |
| `-i, --input` | 검증할 파일 또는 폴더 경로 (CSV, JSON, JSONL 지원) | 필수 |
| `-o, --output` | 결과 파일 저장 경로 | 입력 경로와 동일 |
| `-t, --type` | 샘플 설정 파일 타입 (csv/json/jsonl) | csv |
| `-v, --verbose` | 상세 로그 출력 | False |
| `--log-file` | 로그 파일 경로 | None |
| `--format` | 결과 리포트 형식 (markdown/html/json/all) | all |

## ⚙️ 설정 파일 (YAML)

### 기본 구조
```yaml
file_info:
  file_type: "csv"           # 파일 타입 (csv/json/jsonl)
  expected_rows: 1000        # 예상 행 수 (선택적)
  encoding: "utf-8"          # 파일 인코딩
  delimiter: ","             # CSV 구분자
  has_header: true           # 헤더 행 포함 여부
  
  # JSON/JSONL 전용 설정
  json_schema: null          # JSON 스키마 (JSON 파일용)
  json_root_path: null       # JSON 루트 경로 (중첩된 JSON에서 데이터 위치 지정)
  jsonl_array_mode: false    # JSONL을 배열로 처리할지 여부

columns:
  - name: "id"               # 컬럼 이름
    type: "integer"          # 데이터 타입
    required: true           # 필수 필드 여부
    range:                   # 범위 검증 (숫자 타입)
      min: 1
      max: 999999
  
  - name: "name"
    type: "string"
    required: true
    length:                  # 길이 검증 (문자열 타입)
      min: 1
      max: 100
  
  - name: "email"
    type: "email"
    required: true
  
  - name: "category"
    type: "string"
    required: true
    allowed_values: ["A", "B", "C"]  # 허용된 값 목록
    case_sensitive: false            # 대소문자 구분 여부
  
  - name: "created_date"
    type: "datetime"
    required: true
    format: "%Y-%m-%d %H:%M:%S"      # 날짜 형식
```

### 지원되는 데이터 타입
- `integer`: 정수
- `float`: 실수
- `string`: 문자열
- `datetime`: 날짜/시간
- `boolean`: 불린
- `email`: 이메일 주소
- `phone`: 전화번호
- `object`: JSON 객체
- `array`: JSON 배열
- `null`: null 값

### JSON/JSONL 특화 설정

#### JSON 스키마 예시
```yaml
file_info:
  file_type: "json"
  json_schema:
    type: "object"
    properties:
      id:
        type: "integer"
      name:
        type: "string"
      address:
        type: "object"
        properties:
          street:
            type: "string"
          zipcode:
            type: "string"
    required: ["id", "name"]
```

#### JSON 루트 경로 설정
```yaml
file_info:
  file_type: "json"
  json_root_path: "data.items"  # data.items 배열에서 데이터 추출
```

#### JSONL 배열 모드
```yaml
file_info:
  file_type: "jsonl"
  jsonl_array_mode: true  # JSONL을 배열로 처리
```

## 📊 검증 결과 예시

### 콘솔 출력
```
🚀 검증 시작: data.csv (1,000행)
🏁 검증 완료: data.csv - ⚠️ 3개 오류 발견 (2.5초)

📊 검증 결과 요약:
  총 파일 수: 1
  성공한 파일: 0
  실패한 파일: 1
  총 행 수: 1,000
  총 오류 수: 3
  총 처리 시간: 2.5초
  평균 처리 속도: 400 행/초
```

### 리포트 내용
- **파일 정보**: 파일명, 검증 일시, 행 수, 컬럼 수, 처리 시간
- **검증 요약**: 구조정확성, 형식정확성, 전체 결과, 성공률
- **오류 상세 정보**: 행 번호, 컬럼명, 오류 유형, 실제 값, 예상 값
- **통계 정보**: 오류 유형별, 컬럼별, 행별 통계
- **권장사항**: 데이터 품질 개선을 위한 구체적인 가이드

## 🔧 고급 사용법

### 대용량 파일 처리
프로그램은 스트리밍 방식으로 대용량 CSV 파일을 효율적으로 처리합니다.

```bash
# 100만 행 이상의 파일도 처리 가능
python -m src.main validate -c config.yml -i large_data.csv -v
```

### 배치 처리
```bash
# 폴더 내 모든 지원되는 파일을 일괄 검증
python -m src.main validate -c config.yml -i /data/files -o /results
```

### 자동화 스크립트
```bash
#!/bin/bash
# 자동화 예제

# 1. 파일 타입별 설정 파일 생성
python -m src.main init -t csv -o csv_config.yml
python -m src.main init -t json -o json_config.yml
python -m src.main init -t jsonl -o jsonl_config.yml

# 2. 파일 분석하여 설정 업데이트
python -m src.main analyze -i data.csv -o analyzed_csv_config.yml
python -m src.main analyze -i data.json -o analyzed_json_config.yml
python -m src.main analyze -i data.jsonl -o analyzed_jsonl_config.yml

# 3. 검증 실행
python -m src.main validate -c analyzed_csv_config.yml -i data.csv -o results/
python -m src.main validate -c analyzed_json_config.yml -i data.json -o results/
python -m src.main validate -c analyzed_jsonl_config.yml -i data.jsonl -o results/

# 4. 폴더 내 모든 파일 일괄 검증
python -m src.main validate -c analyzed_csv_config.yml -i /data/files -o results/

# 5. 결과 확인
echo "검증 완료. 결과 파일을 확인하세요: results/"
```

## 📁 프로젝트 구조

```
csv_validator/
├── src/                    # 소스 코드
│   ├── main.py            # 메인 진입점
│   ├── cli/               # 명령행 인터페이스
│   │   └── commands.py    # CLI 명령어 정의
│   ├── core/              # 핵심 검증 로직
│   │   ├── config.py      # 설정 관리
│   │   ├── structural.py  # 구조정확성 검증
│   │   ├── format.py      # 형식정확성 검증
│   │   ├── json_parser.py # JSON/JSONL 파싱
│   │   └── validator.py   # 검증 엔진
│   ├── models/            # 데이터 모델
│   │   ├── validation_rule.py # 검증 규칙 모델
│   │   ├── result.py      # 검증 결과 모델
│   │   └── error.py       # 오류 모델
│   └── utils/             # 유틸리티
│       ├── file_handler.py # 파일 처리
│       ├── formatter.py   # 결과 포맷팅
│       └── logger.py      # 로깅
├── examples/              # 예제 파일들
│   ├── csv/              # CSV 예제 데이터
│   ├── json/             # JSON 예제 데이터
│   ├── jsonl/            # JSONL 예제 데이터
│   └── configs/          # 설정 파일 예제
├── docs/                 # 문서
│   ├── API.md           # API 문서
│   └── examples.md      # 사용 예제
├── tests/               # 테스트
├── requirements.txt     # 의존성
└── README.md           # 이 파일
```

## 🎯 실제 사용 예제

### 예제 1: 직원 데이터 검증
```bash
# 1. 직원 데이터용 설정 파일 생성
python -m src.main init -t csv -o employee_config.yml

# 2. 설정 파일 수정 (examples/employee_config.yml 참조)
# 3. 직원 데이터 검증
python -m src.main validate -c employee_config.yml -i examples/csv/employees.csv -v
```

### 예제 2: JSON 데이터 검증
```bash
# 1. JSON 데이터 분석
python -m src.main analyze -i examples/json/users.json -o auto_users_config.yml

# 2. 분석된 설정으로 검증
python -m src.main validate -c auto_users_config.yml -i examples/json/users.json -v
```

### 예제 3: JSONL 로그 데이터 검증
```bash
# 1. JSONL 로그 데이터 분석
python -m src.main analyze -i examples/jsonl/log_entries.jsonl -o auto_logs_config.yml

# 2. 로그 데이터 검증
python -m src.main validate -c auto_logs_config.yml -i examples/jsonl/log_entries.jsonl -v
```

## 🐛 문제 해결

### 자주 발생하는 문제들

#### 1. 인코딩 오류
```
UnicodeDecodeError: 'utf-8' codec can't decode byte
```
**해결방법**: 설정 파일에서 올바른 인코딩을 지정하세요.
```yaml
file_info:
  encoding: "cp949"  # 또는 "euc-kr"
```

**참고**: 프로그램은 인코딩 호환성을 자동으로 검사합니다:
- UTF-8 ↔ ASCII (호환)
- CP949 ↔ EUC-KR (호환)
- Latin-1 ↔ ISO-8859-1 (호환)

#### 2. 구분자 인식 오류
**해결방법**: 설정 파일에서 올바른 구분자를 지정하세요.
```yaml
file_info:
  delimiter: ";"  # 또는 "\t"
```

#### 3. 메모리 부족
**해결방법**: 프로그램은 스트리밍 방식으로 처리하므로 일반적으로 메모리 문제가 없습니다. 만약 발생한다면 파일을 분할하여 처리하세요.

### 로그 확인
```bash
# 상세 로그와 함께 실행
python -m src.main validate -c config.yml -i data.csv -v

# 로그 파일에 저장
python -m src.main validate -c config.yml -i data.csv --log-file validation.log
```

## 🧪 테스트

### 테스트 실행
```bash
# 모든 테스트 실행
python -m pytest tests/

# 특정 테스트 실행
python -m pytest tests/test_structural.py

# 커버리지와 함께 실행
python -m pytest tests/ --cov=src
```

### 테스트 데이터
`tests/fixtures/` 디렉토리에 다양한 테스트 시나리오를 위한 샘플 데이터가 포함되어 있습니다.

## 🤝 기여하기

1. 이 저장소를 포크합니다
2. 새로운 기능 브랜치를 생성합니다 (`git checkout -b feature/amazing-feature`)
3. 변경사항을 커밋합니다 (`git commit -m 'Add amazing feature'`)
4. 브랜치에 푸시합니다 (`git push origin feature/amazing-feature`)
5. Pull Request를 생성합니다

## 📄 라이선스

이 프로젝트는 Apache 2.0 라이선스 하에 배포됩니다. 자세한 내용은 [LICENSE](LICENSE) 파일을 참조하세요.

## 📞 지원

- **이슈 리포트**: [GitHub Issues](https://github.com/your-repo/issues)
- **문서**: [API 문서](docs/API.md), [사용 예제](docs/examples.md)
- **이메일**: support@example.com

## 🏆 성능 지표

| 항목 | 성능 |
|------|------|
| **처리 속도** | 25-100 행/초 |
| **메모리 사용량** | 효율적 (스트리밍 처리) |
| **지원 파일 크기** | 100만 행 이상 |
| **지원 인코딩** | UTF-8, CP949, EUC-KR, ASCII |
| **지원 구분자** | 쉼표, 세미콜론, 탭, 파이프 |
| **지원 파일 형식** | CSV, JSON, JSONL |

## 🔄 버전 히스토리

### v0.2.0 (현재)
- JSON, JSONL 파일 지원 추가
- 자동 파일 분석 기능 추가
- 향상된 오류 메시지 및 로깅
- 성능 최적화

### v0.1.0
- 기본 CSV 검증 기능
- YAML 설정 파일 지원
- Markdown, HTML, JSON 리포트 생성

---

**데이터 파일 구문정확성 검증 프로그램**으로 데이터 품질을 보장하고 검증 과정을 자동화하세요! 🚀