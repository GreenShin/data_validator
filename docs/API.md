# API 문서

CSV 구문정확성 검증 프로그램의 API 및 개발자 가이드입니다.

## 📚 목차

- [개요](#개요)
- [핵심 클래스](#핵심-클래스)
- [데이터 모델](#데이터-모델)
- [사용 예제](#사용-예제)
- [확장 가이드](#확장-가이드)

## 개요

이 프로그램은 모듈화된 아키텍처로 설계되어 있어, 각 컴포넌트를 독립적으로 사용하거나 확장할 수 있습니다.

### 아키텍처 구조

```
src/
├── core/           # 핵심 검증 로직
│   ├── config.py   # 설정 관리
│   ├── structural.py # 구조정확성 검증
│   ├── format.py   # 형식정확성 검증
│   └── validator.py # 검증 엔진
├── models/         # 데이터 모델
│   ├── validation_rule.py
│   ├── result.py
│   └── error.py
├── utils/          # 유틸리티
│   ├── file_handler.py
│   ├── formatter.py
│   └── logger.py
└── cli/            # 명령행 인터페이스
    └── commands.py
```

## 핵심 클래스

### CSVValidator

전체 검증 워크플로우를 관리하는 핵심 클래스입니다.

```python
from src.core.validator import CSVValidator

# 초기화
validator = CSVValidator(
    config_path="config.yml",
    verbose=True,
    log_file="validation.log"
)

# 단일 파일 검증
result = validator.validate_file("data.csv")

# 폴더 검증
results = validator.validate_folder("/path/to/csvs", "/path/to/results")

# 리소스 정리
validator.close()
```

#### 주요 메서드

| 메서드 | 설명 | 반환값 |
|--------|------|--------|
| `validate_file(file_path)` | 단일 CSV 파일 검증 | `ValidationResult` |
| `validate_folder(folder_path, output_dir)` | 폴더 내 모든 CSV 파일 검증 | `List[ValidationResult]` |
| `get_config_summary()` | 설정 요약 정보 반환 | `Dict[str, Any]` |
| `reload_config()` | 설정 파일 다시 로드 | `ValidationConfig` |
| `validate_config()` | 설정 유효성 검사 | `bool` |

### ConfigManager

YAML 설정 파일을 관리하는 클래스입니다.

```python
from src.core.config import ConfigManager

config_manager = ConfigManager()

# 설정 로드
config = config_manager.load_config("config.yml")

# 설정 검증
is_valid = config_manager.validate_config(config)

# 컬럼 규칙 조회
rule = config_manager.get_column_rule("email")

# 샘플 설정 생성
config_manager.create_sample_config("sample.yml")
```

### StructuralValidator

CSV 파일의 구조정확성을 검증하는 클래스입니다.

```python
from src.core.structural import StructuralValidator
from src.models import FileInfo

validator = StructuralValidator()

# CSV 포맷 검증
is_valid = validator.validate_csv_format("data.csv", file_info)

# 행 수 검증
is_valid = validator.validate_row_count("data.csv", 1000)

# 인코딩 검증
is_valid = validator.validate_encoding("data.csv", "utf-8")

# 전체 구조 검증
is_valid, errors = validator.validate_all("data.csv", file_info, expected_columns)
```

### FormatValidator

데이터의 형식정확성을 검증하는 클래스입니다.

```python
from src.core.format import FormatValidator
from src.models import ValidationRule

validator = FormatValidator()

# 데이터 타입 검증
is_valid = validator.validate_data_type("123", rule)

# 범위 검증
is_valid = validator.validate_range(150, rule)

# 범주형 데이터 검증
is_valid = validator.validate_categorical("A", rule)

# 전체 형식 검증
is_valid = validator.validate_all("value", rule)
```

### FileHandler

CSV 파일 처리를 담당하는 유틸리티 클래스입니다.

```python
from src.utils.file_handler import FileHandler

handler = FileHandler()

# 파일 정보 수집
info = handler.get_file_info("data.csv")

# 인코딩 감지
encoding = handler.detect_encoding("data.csv")

# 구분자 감지
delimiter = handler.detect_delimiter("data.csv")

# 스트리밍 방식으로 파일 읽기
for chunk in handler.read_csv_streaming("data.csv", config, chunk_size=1000):
    # 청크 단위로 처리
    pass

# CSV 파일 찾기
csv_files = handler.find_csv_files("/path/to/directory", recursive=True)
```

### ReportFormatter

검증 결과를 포맷팅하는 클래스입니다.

```python
from src.utils.formatter import ReportFormatter

formatter = ReportFormatter()

# Markdown 리포트 생성
markdown_report = formatter.generate_markdown_report(result)

# HTML 리포트 생성
html_report = formatter.generate_html_report(result)

# JSON 리포트 생성
json_report = formatter.generate_json_report(result)

# 리포트 파일 저장
file_path = formatter.save_report(report_content, "output", "markdown")
```

### Logger

로깅 및 진행률 표시를 담당하는 클래스입니다.

```python
from src.utils.logger import Logger

logger = Logger(verbose=True, log_file="app.log")

# 로그 출력
logger.info("정보 메시지")
logger.warning("경고 메시지")
logger.error("오류 메시지")

# 진행률 표시
logger.log_progress(current=50, total=100, message="처리 중...")

# 성공/오류 메시지
logger.log_success("작업 완료")
logger.log_error(exception, "컨텍스트")

# 검증 관련 로깅
logger.log_validation_start("data.csv", 1000)
logger.log_validation_complete("data.csv", 5, 2.5)

# 결과 요약
logger.log_summary({"총 파일": 10, "성공": 8, "실패": 2})
```

## 데이터 모델

### ValidationRule

개별 컬럼에 대한 검증 규칙을 정의하는 모델입니다.

```python
from src.models.validation_rule import ValidationRule, DataType

rule = ValidationRule(
    name="email",
    type=DataType.EMAIL,
    required=True,
    pattern=r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)

# 범위 검증이 있는 정수 규칙
rule = ValidationRule(
    name="age",
    type=DataType.INTEGER,
    required=True,
    range={"min": 0, "max": 120}
)

# 범주형 데이터 규칙
rule = ValidationRule(
    name="category",
    type=DataType.STRING,
    required=True,
    allowed_values=["A", "B", "C"],
    case_sensitive=False
)
```

### ValidationResult

검증 결과를 담는 모델입니다.

```python
from src.models.result import ValidationResult
from datetime import datetime

result = ValidationResult(
    file_name="data.csv",
    total_rows=1000,
    total_columns=5,
    structural_valid=True,
    format_valid=False,
    errors=[...],  # ValidationError 객체들의 리스트
    processing_time=2.5,
    timestamp=datetime.now()
)

# 결과 정보 접근
print(f"파일: {result.file_name}")
print(f"총 행 수: {result.total_rows}")
print(f"오류 수: {len(result.errors)}")
print(f"성공 여부: {result.structural_valid and result.format_valid}")
```

### ValidationError

개별 검증 오류를 담는 모델입니다.

```python
from src.models.error import ValidationError, ErrorType

error = ValidationError(
    row_number=15,
    column_name="email",
    error_type=ErrorType.FORMAT_INVALID_EMAIL.value,
    actual_value="invalid-email",
    expected_value="올바른 이메일 형식",
    message="잘못된 이메일 형식입니다"
)

# 오류 정보 접근
print(f"행 {error.row_number}, 컬럼 {error.column_name}: {error.message}")
```

### ValidationConfig

전체 검증 설정을 담는 모델입니다.

```python
from src.models.validation_rule import ValidationConfig, FileInfo

config = ValidationConfig(
    file_info=FileInfo(
        expected_rows=1000,
        encoding="utf-8",
        delimiter=",",
        has_header=True
    ),
    columns=[
        ValidationRule(name="id", type=DataType.INTEGER, required=True),
        ValidationRule(name="name", type=DataType.STRING, required=True),
        # ... 더 많은 규칙들
    ]
)

# 설정 정보 접근
print(f"인코딩: {config.file_info.encoding}")
print(f"컬럼 수: {len(config.columns)}")
print(f"필수 컬럼: {config.get_required_columns()}")
```

## 사용 예제

### 기본 사용법

```python
from src.core.validator import CSVValidator

# 1. 검증기 초기화
validator = CSVValidator("config.yml", verbose=True)

# 2. 파일 검증
result = validator.validate_file("data.csv")

# 3. 결과 확인
if result.structural_valid and result.format_valid:
    print("✅ 검증 통과")
else:
    print(f"❌ {len(result.errors)}개 오류 발견")
    for error in result.errors:
        print(f"  - 행 {error.row_number}: {error.message}")

# 4. 리소스 정리
validator.close()
```

### 배치 처리

```python
from src.core.validator import CSVValidator
from src.utils.formatter import ReportFormatter

validator = CSVValidator("config.yml")
formatter = ReportFormatter()

# 폴더 내 모든 CSV 파일 검증
results = validator.validate_folder("/data/csvs", "/results")

# 전체 결과 요약
total_files = len(results)
successful_files = sum(1 for r in results if r.structural_valid and r.format_valid)
total_errors = sum(len(r.errors) for r in results)

print(f"처리 완료: {successful_files}/{total_files} 파일 성공, {total_errors}개 오류")

validator.close()
```

### 커스텀 검증 로직

```python
from src.core.format import FormatValidator
from src.models.validation_rule import ValidationRule, DataType

# 커스텀 검증 규칙 생성
custom_rule = ValidationRule(
    name="phone",
    type=DataType.STRING,
    required=True,
    pattern=r"^010-\d{4}-\d{4}$"  # 한국 휴대폰 번호 형식
)

# 검증 실행
validator = FormatValidator()
is_valid = validator.validate_all("010-1234-5679", custom_rule)

if is_valid:
    print("✅ 유효한 전화번호")
else:
    for error in validator.get_errors():
        print(f"❌ {error.message}")
```

### 프로그래밍 방식으로 설정 생성

```python
from src.models.validation_rule import ValidationConfig, FileInfo, ValidationRule, DataType

# 설정 객체 생성
config = ValidationConfig(
    file_info=FileInfo(
        expected_rows=1000,
        encoding="utf-8",
        delimiter=",",
        has_header=True
    ),
    columns=[
        ValidationRule(
            name="id",
            type=DataType.INTEGER,
            required=True,
            range={"min": 1, "max": 999999}
        ),
        ValidationRule(
            name="email",
            type=DataType.EMAIL,
            required=True
        ),
        ValidationRule(
            name="age",
            type=DataType.INTEGER,
            required=False,
            range={"min": 0, "max": 120}
        )
    ]
)

# 설정을 YAML 파일로 저장
from src.core.config import ConfigManager
config_manager = ConfigManager()
config_manager.save_config(config, "custom_config.yml")
```

## 확장 가이드

### 새로운 데이터 타입 추가

1. `DataType` 열거형에 새로운 타입 추가:

```python
# src/models/validation_rule.py
class DataType(str, Enum):
    # 기존 타입들...
    CUSTOM_TYPE = "custom_type"
```

2. `FormatValidator`에 검증 로직 추가:

```python
# src/core/format.py
def _validate_custom_type(self, value: Any, rule: ValidationRule) -> bool:
    """커스텀 타입 검증 로직"""
    # 검증 로직 구현
    pass
```

### 새로운 검증 규칙 추가

```python
from src.models.validation_rule import ValidationRule, DataType

# 새로운 검증 규칙 생성
rule = ValidationRule(
    name="custom_field",
    type=DataType.STRING,
    required=True,
    pattern=r"^[A-Z]{2}\d{6}$",  # 커스텀 패턴
    length={"min": 8, "max": 8}
)
```

### 커스텀 리포트 형식 추가

```python
from src.utils.formatter import ReportFormatter

class CustomReportFormatter(ReportFormatter):
    def generate_custom_report(self, result: ValidationResult) -> str:
        """커스텀 리포트 형식 생성"""
        # 커스텀 리포트 로직 구현
        pass

# 사용
formatter = CustomReportFormatter()
custom_report = formatter.generate_custom_report(result)
```

### 플러그인 시스템 구현

```python
from abc import ABC, abstractmethod

class ValidationPlugin(ABC):
    @abstractmethod
    def validate(self, value: Any, rule: ValidationRule) -> bool:
        pass
    
    @abstractmethod
    def get_error_message(self, value: Any, rule: ValidationRule) -> str:
        pass

class CustomValidationPlugin(ValidationPlugin):
    def validate(self, value: Any, rule: ValidationRule) -> bool:
        # 커스텀 검증 로직
        return True
    
    def get_error_message(self, value: Any, rule: ValidationRule) -> str:
        return "커스텀 검증 실패"
```

## 성능 최적화

### 대용량 파일 처리

```python
# 청크 크기 조정으로 메모리 사용량 최적화
validator = CSVValidator("config.yml")
result = validator.validate_file("large_file.csv")  # 자동으로 스트리밍 처리
```

### 병렬 처리

```python
import concurrent.futures
from src.core.validator import CSVValidator

def validate_single_file(file_path):
    validator = CSVValidator("config.yml")
    return validator.validate_file(file_path)

# 여러 파일을 병렬로 검증
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
    futures = [executor.submit(validate_single_file, path) for path in csv_files]
    results = [future.result() for future in futures]
```

## 오류 처리

### 예외 처리 패턴

```python
from src.core.validator import CSVValidator
from src.core.config import ConfigManager

try:
    # 설정 로드
    config_manager = ConfigManager()
    config = config_manager.load_config("config.yml")
    
    # 검증 실행
    validator = CSVValidator("config.yml")
    result = validator.validate_file("data.csv")
    
except FileNotFoundError as e:
    print(f"파일을 찾을 수 없습니다: {e}")
except ValidationError as e:
    print(f"설정 오류: {e}")
except Exception as e:
    print(f"예상치 못한 오류: {e}")
finally:
    if 'validator' in locals():
        validator.close()
```

### 로깅 활용

```python
from src.utils.logger import Logger

logger = Logger(verbose=True, log_file="app.log")

try:
    # 작업 수행
    logger.info("검증 시작")
    result = validator.validate_file("data.csv")
    logger.log_success("검증 완료")
    
except Exception as e:
    logger.log_error(e, "검증 중 오류 발생")
    raise
```

---

이 API 문서를 참조하여 CSV 구문정확성 검증 프로그램을 확장하고 커스터마이징할 수 있습니다. 추가 질문이나 도움이 필요하시면 이슈를 생성해 주세요.
