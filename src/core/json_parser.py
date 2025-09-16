"""
JSON/JSONL 파일 파싱 및 검증을 위한 모듈.

이 모듈은 JSON과 JSONL 파일을 파싱하고 검증하는 기능을 제공합니다.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator, Tuple, Union
import pandas as pd
from datetime import datetime

from ..models import FileInfo, ValidationRule, ValidationError, DataType


class JSONParser:
    """JSON/JSONL 파일을 파싱하는 클래스"""

    def __init__(self):
        """JSONParser 초기화"""
        self.supported_extensions = {'.json', '.jsonl'}

    def detect_file_type(self, file_path: str) -> str:
        """
        파일 확장자를 기반으로 파일 타입을 감지합니다.
        
        Args:
            file_path: 파일 경로
            
        Returns:
            str: 파일 타입 ('json' 또는 'jsonl')
        """
        extension = Path(file_path).suffix.lower()
        
        if extension == '.json':
            return 'json'
        elif extension == '.jsonl':
            return 'jsonl'
        else:
            raise ValueError(f"지원되지 않는 파일 확장자: {extension}")

    def parse_json_file(self, file_path: str, file_info: FileInfo) -> List[Dict[str, Any]]:
        """
        JSON 파일을 파싱합니다.
        
        Args:
            file_path: JSON 파일 경로
            file_info: 파일 정보
            
        Returns:
            List[Dict[str, Any]]: 파싱된 데이터 목록
        """
        try:
            with open(file_path, 'r', encoding=file_info.encoding) as f:
                data = json.load(f)
            
            # JSON 스키마 검증 (제공된 경우)
            if file_info.json_schema:
                self._validate_json_schema(data, file_info.json_schema)
            
            # 루트 경로가 지정된 경우 해당 경로의 데이터 추출
            if file_info.json_root_path:
                data = self._extract_data_by_path(data, file_info.json_root_path)
            
            # 데이터가 배열이 아닌 경우 배열로 변환
            if not isinstance(data, list):
                data = [data]
            
            return data
            
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 오류: {e}")
        except Exception as e:
            raise ValueError(f"JSON 파일 읽기 오류: {e}")

    def parse_jsonl_file(self, file_path: str, file_info: FileInfo) -> List[Dict[str, Any]]:
        """
        JSONL 파일을 파싱합니다.
        
        Args:
            file_path: JSONL 파일 경로
            file_info: 파일 정보
            
        Returns:
            List[Dict[str, Any]]: 파싱된 데이터 목록
        """
        data = []
        
        try:
            with open(file_path, 'r', encoding=file_info.encoding) as f:
                for line_num, line in enumerate(f, 1):
                    line = line.strip()
                    if not line:  # 빈 라인 건너뛰기
                        continue
                    
                    try:
                        json_obj = json.loads(line)
                        data.append(json_obj)
                    except json.JSONDecodeError as e:
                        raise ValueError(f"라인 {line_num}에서 JSON 파싱 오류: {e}")
            
            return data
            
        except Exception as e:
            raise ValueError(f"JSONL 파일 읽기 오류: {e}")

    def parse_file(self, file_path: str, file_info: FileInfo) -> List[Dict[str, Any]]:
        """
        파일 타입에 따라 적절한 파서를 사용하여 파일을 파싱합니다.
        
        Args:
            file_path: 파일 경로
            file_info: 파일 정보
            
        Returns:
            List[Dict[str, Any]]: 파싱된 데이터 목록
        """
        file_type = self.detect_file_type(file_path)
        
        if file_type == 'json':
            return self.parse_json_file(file_path, file_info)
        elif file_type == 'jsonl':
            return self.parse_jsonl_file(file_path, file_info)
        else:
            raise ValueError(f"지원되지 않는 파일 타입: {file_type}")

    def convert_to_dataframe(self, data: List[Dict[str, Any]], file_info: FileInfo) -> pd.DataFrame:
        """
        JSON/JSONL 데이터를 pandas DataFrame으로 변환합니다.
        
        Args:
            data: 파싱된 데이터
            file_info: 파일 정보
            
        Returns:
            pd.DataFrame: 변환된 DataFrame
        """
        if not data:
            return pd.DataFrame()
        
        # 중첩된 객체를 평면화
        flattened_data = []
        for item in data:
            flattened_item = self._flatten_dict(item)
            flattened_data.append(flattened_item)
        
        return pd.DataFrame(flattened_data)

    def validate_json_structure(self, data: List[Dict[str, Any]], columns: List[ValidationRule]) -> Tuple[bool, List[ValidationError]]:
        """
        JSON 데이터의 구조를 검증합니다.
        
        Args:
            data: 검증할 데이터
            columns: 컬럼 검증 규칙
            
        Returns:
            Tuple[bool, List[ValidationError]]: 검증 결과와 오류 목록
        """
        errors = []
        
        if not data:
            return True, errors
        
        # 첫 번째 객체를 기준으로 구조 검증
        first_item = data[0]
        flattened_first = self._flatten_dict(first_item)
        
        # 필수 컬럼 확인
        required_columns = [rule.name for rule in columns if rule.required]
        missing_columns = [col for col in required_columns if col not in flattened_first]
        
        if missing_columns:
            errors.append(ValidationError(
                row_number=1,
                column_name="structure",
                error_type="MISSING_REQUIRED_FIELD",
                actual_value="",
                expected_value=missing_columns,
                message=f"필수 필드가 누락되었습니다: {missing_columns}"
            ))
        
        # 모든 객체의 구조 일관성 확인
        for i, item in enumerate(data, 1):
            flattened_item = self._flatten_dict(item)
            
            # 필수 필드 존재 여부 확인
            for col in required_columns:
                if col not in flattened_item:
                    errors.append(ValidationError(
                        row_number=i,
                        column_name=col,
                        error_type="MISSING_REQUIRED_FIELD",
                        actual_value="",
                        expected_value=col,
                        message=f"필수 필드 '{col}'가 누락되었습니다"
                    ))
        
        return len(errors) == 0, errors

    def validate_json_format(self, data: List[Dict[str, Any]], columns: List[ValidationRule]) -> Tuple[bool, List[ValidationError]]:
        """
        JSON 데이터의 형식을 검증합니다.
        
        Args:
            data: 검증할 데이터
            columns: 컬럼 검증 규칙
            
        Returns:
            Tuple[bool, List[ValidationError]]: 검증 결과와 오류 목록
        """
        errors = []
        
        for i, item in enumerate(data, 1):
            flattened_item = self._flatten_dict(item)
            
            for rule in columns:
                field_name = rule.name
                value = flattened_item.get(field_name)
                
                # 필수 필드 검증
                if rule.required and (value is None or value == ""):
                    errors.append(ValidationError(
                        row_number=i,
                        column_name=field_name,
                        error_type="REQUIRED_FIELD_MISSING",
                        actual_value=value,
                        expected_value="non-empty value",
                        message=f"필수 필드 '{field_name}'가 비어있습니다"
                    ))
                    continue
                
                # 선택적 필드가 비어있는 경우 건너뛰기
                if not rule.required and (value is None or value == ""):
                    continue
                
                # 데이터 타입 검증
                type_error = self._validate_data_type(value, rule, i, field_name)
                if type_error:
                    errors.append(type_error)
        
        return len(errors) == 0, errors

    def _validate_json_schema(self, data: Any, schema: Dict[str, Any]) -> None:
        """
        JSON 스키마를 사용하여 데이터를 검증합니다.
        
        Args:
            data: 검증할 데이터
            schema: JSON 스키마
        """
        # 간단한 JSON 스키마 검증 구현
        # 실제 프로덕션에서는 jsonschema 라이브러리 사용 권장
        if "type" in schema:
            expected_type = schema["type"]
            if expected_type == "array" and not isinstance(data, list):
                raise ValueError(f"예상 타입: {expected_type}, 실제 타입: {type(data).__name__}")
            elif expected_type == "object" and not isinstance(data, dict):
                # 배열의 경우 각 요소가 객체인지 확인
                if isinstance(data, list) and data and isinstance(data[0], dict):
                    # 배열의 첫 번째 요소가 객체이면 통과
                    pass
                else:
                    raise ValueError(f"예상 타입: {expected_type}, 실제 타입: {type(data).__name__}")

    def _extract_data_by_path(self, data: Any, path: str) -> Any:
        """
        지정된 경로에서 데이터를 추출합니다.
        
        Args:
            data: 원본 데이터
            path: 데이터 경로 (예: "data.items", "results[0]")
            
        Returns:
            Any: 추출된 데이터
        """
        current = data
        
        for part in path.split('.'):
            if '[' in part and ']' in part:
                # 배열 인덱스 처리 (예: "items[0]")
                key = part[:part.index('[')]
                index = int(part[part.index('[')+1:part.index(']')])
                current = current[key][index]
            else:
                # 일반 키 처리
                current = current[part]
        
        return current

    def _flatten_dict(self, data: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, Any]:
        """
        중첩된 딕셔너리를 평면화합니다.
        
        Args:
            data: 평면화할 딕셔너리
            parent_key: 부모 키
            sep: 구분자
            
        Returns:
            Dict[str, Any]: 평면화된 딕셔너리
        """
        items = []
        
        for key, value in data.items():
            new_key = f"{parent_key}{sep}{key}" if parent_key else key
            
            if isinstance(value, dict):
                items.extend(self._flatten_dict(value, new_key, sep=sep).items())
            elif isinstance(value, list):
                # 배열의 경우 인덱스를 키로 사용
                for i, item in enumerate(value):
                    if isinstance(item, dict):
                        items.extend(self._flatten_dict(item, f"{new_key}[{i}]", sep=sep).items())
                    else:
                        items.append((f"{new_key}[{i}]", item))
            else:
                items.append((new_key, value))
        
        return dict(items)

    def _validate_data_type(self, value: Any, rule: ValidationRule, row_number: int, field_name: str) -> Optional[ValidationError]:
        """
        데이터 타입을 검증합니다.
        
        Args:
            value: 검증할 값
            rule: 검증 규칙
            row_number: 행 번호
            field_name: 필드 이름
            
        Returns:
            Optional[ValidationError]: 오류가 있으면 ValidationError, 없으면 None
        """
        try:
            if rule.type == DataType.INTEGER:
                if not isinstance(value, int):
                    try:
                        int(value)
                    except (ValueError, TypeError):
                        return ValidationError(
                            row_number=row_number,
                            column_name=field_name,
                            error_type="INVALID_INTEGER",
                            actual_value=value,
                            expected_value="integer",
                            message=f"정수 값이 아닙니다: {value}"
                        )
                
                # 범위 검증
                if rule.range:
                    if value < rule.range["min"] or value > rule.range["max"]:
                        return ValidationError(
                            row_number=row_number,
                            column_name=field_name,
                            error_type="VALUE_OUT_OF_RANGE",
                            actual_value=value,
                            expected_value=f"{rule.range['min']} ~ {rule.range['max']}",
                            message=f"값이 범위를 벗어났습니다: {value}"
                        )
            
            elif rule.type == DataType.FLOAT:
                if not isinstance(value, (int, float)):
                    try:
                        float(value)
                    except (ValueError, TypeError):
                        return ValidationError(
                            row_number=row_number,
                            column_name=field_name,
                            error_type="INVALID_FLOAT",
                            actual_value=value,
                            expected_value="float",
                            message=f"실수 값이 아닙니다: {value}"
                        )
                
                # 범위 검증
                if rule.range:
                    float_value = float(value)
                    if float_value < rule.range["min"] or float_value > rule.range["max"]:
                        return ValidationError(
                            row_number=row_number,
                            column_name=field_name,
                            error_type="VALUE_OUT_OF_RANGE",
                            actual_value=value,
                            expected_value=f"{rule.range['min']} ~ {rule.range['max']}",
                            message=f"값이 범위를 벗어났습니다: {value}"
                        )
            
            elif rule.type == DataType.STRING:
                if not isinstance(value, str):
                    value = str(value)
                
                # 길이 검증
                if rule.length:
                    if len(value) < rule.length["min"] or len(value) > rule.length["max"]:
                        return ValidationError(
                            row_number=row_number,
                            column_name=field_name,
                            error_type="INVALID_LENGTH",
                            actual_value=len(value),
                            expected_value=f"{rule.length['min']} ~ {rule.length['max']}",
                            message=f"문자열 길이가 범위를 벗어났습니다: {len(value)}"
                        )
                
                # 허용 값 검증
                if rule.allowed_values:
                    if rule.case_sensitive:
                        if value not in rule.allowed_values:
                            return ValidationError(
                                row_number=row_number,
                                column_name=field_name,
                                error_type="INVALID_VALUE",
                                actual_value=value,
                                expected_value=rule.allowed_values,
                                message=f"허용되지 않는 값입니다: {value}"
                            )
                    else:
                        if value.lower() not in [v.lower() for v in rule.allowed_values]:
                            return ValidationError(
                                row_number=row_number,
                                column_name=field_name,
                                error_type="INVALID_VALUE",
                                actual_value=value,
                                expected_value=rule.allowed_values,
                                message=f"허용되지 않는 값입니다: {value}"
                            )
                
                # 정규표현식 검증
                if rule.pattern:
                    import re
                    if not re.match(rule.pattern, value):
                        return ValidationError(
                            row_number=row_number,
                            column_name=field_name,
                            error_type="PATTERN_MISMATCH",
                            actual_value=value,
                            expected_value=rule.pattern,
                            message=f"패턴과 일치하지 않습니다: {value}"
                        )
            
            elif rule.type == DataType.BOOLEAN:
                if not isinstance(value, bool):
                    if str(value).lower() not in ['true', 'false', '1', '0', 'yes', 'no']:
                        return ValidationError(
                            row_number=row_number,
                            column_name=field_name,
                            error_type="INVALID_BOOLEAN",
                            actual_value=value,
                            expected_value="boolean",
                            message=f"불린 값이 아닙니다: {value}"
                        )
            
            elif rule.type == DataType.EMAIL:
                if not isinstance(value, str):
                    value = str(value)
                
                import re
                email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
                if not re.match(email_pattern, value):
                    return ValidationError(
                        row_number=row_number,
                        column_name=field_name,
                        error_type="INVALID_EMAIL",
                        actual_value=value,
                        expected_value="valid email",
                        message=f"유효하지 않은 이메일 형식입니다: {value}"
                    )
            
            elif rule.type == DataType.DATETIME:
                if not isinstance(value, str):
                    value = str(value)
                
                try:
                    datetime.strptime(value, rule.format)
                except ValueError:
                    return ValidationError(
                        row_number=row_number,
                        column_name=field_name,
                        error_type="INVALID_DATETIME",
                        actual_value=value,
                        expected_value=rule.format,
                        message=f"유효하지 않은 날짜/시간 형식입니다: {value}"
                    )
            
            elif rule.type == DataType.OBJECT:
                if not isinstance(value, dict):
                    return ValidationError(
                        row_number=row_number,
                        column_name=field_name,
                        error_type="INVALID_OBJECT",
                        actual_value=type(value).__name__,
                        expected_value="object",
                        message=f"객체가 아닙니다: {type(value).__name__}"
                    )
            
            elif rule.type == DataType.ARRAY:
                if not isinstance(value, list):
                    return ValidationError(
                        row_number=row_number,
                        column_name=field_name,
                        error_type="INVALID_ARRAY",
                        actual_value=type(value).__name__,
                        expected_value="array",
                        message=f"배열이 아닙니다: {type(value).__name__}"
                    )
            
            elif rule.type == DataType.NULL:
                if value is not None:
                    return ValidationError(
                        row_number=row_number,
                        column_name=field_name,
                        error_type="INVALID_NULL",
                        actual_value=value,
                        expected_value="null",
                        message=f"null 값이 아닙니다: {value}"
                    )
            
        except Exception as e:
            return ValidationError(
                row_number=row_number,
                column_name=field_name,
                error_type="VALIDATION_ERROR",
                actual_value=value,
                expected_value="valid value",
                message=f"검증 중 오류 발생: {e}"
            )
        
        return None

    def count_rows(self, file_path: str, file_info: FileInfo) -> int:
        """
        파일의 행 수를 계산합니다.
        
        Args:
            file_path: 파일 경로
            file_info: 파일 정보
            
        Returns:
            int: 행 수
        """
        try:
            data = self.parse_file(file_path, file_info)
            return len(data)
        except Exception:
            # 파싱 실패 시 파일을 직접 읽어서 행 수 계산
            try:
                with open(file_path, 'r', encoding=file_info.encoding) as f:
                    if file_info.file_type == FileType.JSONL:
                        return sum(1 for line in f if line.strip())
                    else:  # JSON
                        content = f.read().strip()
                        if content:
                            return 1  # JSON 파일은 보통 하나의 객체
                        return 0
            except Exception:
                return 0
