"""
Configuration management for CSV validation.

이 모듈은 YAML 설정 파일을 로드하고 관리하는 기능을 제공합니다.
"""

import os
import yaml
from pathlib import Path
from typing import Optional, Dict, List, Any
from pydantic import ValidationError

from ..models import (
    ValidationConfig,
    ValidationRule,
    FileInfo,
    DataType,
    ErrorType,
    ErrorRegistry,
)


class ConfigManager:
    """YAML 설정 파일을 관리하는 클래스"""

    def __init__(self):
        """ConfigManager 초기화"""
        self._config: Optional[ValidationConfig] = None
        self._config_path: Optional[str] = None
        self._raw_config: Optional[Dict[str, Any]] = None

    def load_config(self, config_path: str) -> ValidationConfig:
        """
        YAML 설정 파일을 로드하고 ValidationConfig 객체로 변환합니다.

        Args:
            config_path: YAML 설정 파일 경로

        Returns:
            ValidationConfig: 로드된 설정 객체

        Raises:
            FileNotFoundError: 설정 파일을 찾을 수 없는 경우
            yaml.YAMLError: YAML 파싱 오류
            ValidationError: 설정 검증 오류
        """
        # 파일 존재 여부 확인
        if not os.path.exists(config_path):
            raise FileNotFoundError(f"설정 파일을 찾을 수 없습니다: {config_path}")

        # 파일 읽기 권한 확인
        if not os.access(config_path, os.R_OK):
            raise PermissionError(f"설정 파일 읽기 권한이 없습니다: {config_path}")

        try:
            # YAML 파일 로드
            with open(config_path, "r", encoding="utf-8") as file:
                self._raw_config = yaml.safe_load(file)

            if self._raw_config is None:
                raise ValueError("설정 파일이 비어있습니다")

            # ValidationConfig 객체로 변환
            self._config = ValidationConfig(**self._raw_config)
            self._config_path = config_path

            return self._config

        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"YAML 파싱 오류: {e}")
        except ValidationError as e:
            # Pydantic ValidationError는 특별한 구조를 가지므로 문자열로 변환하여 새로운 예외 생성
            error_msg = f"설정 검증 오류: {str(e)}"
            raise ValueError(error_msg) from e
        except Exception as e:
            raise Exception(f"설정 로드 중 오류 발생: {e}")

    def validate_config(self, config: Optional[ValidationConfig] = None) -> bool:
        """
        설정의 유효성을 검사합니다.

        Args:
            config: 검증할 설정 객체 (None이면 현재 로드된 설정 사용)

        Returns:
            bool: 설정이 유효한지 여부
        """
        if config is None:
            config = self._config

        if config is None:
            return False

        try:
            # 기본 검증 (Pydantic이 자동으로 수행)
            # 추가적인 비즈니스 로직 검증
            self._validate_business_rules(config)
            return True

        except Exception:
            return False

    def get_column_rule(self, column_name: str) -> Optional[ValidationRule]:
        """
        컬럼 이름으로 검증 규칙을 조회합니다.

        Args:
            column_name: 조회할 컬럼 이름

        Returns:
            Optional[ValidationRule]: 해당 컬럼의 검증 규칙 (없으면 None)
        """
        if self._config is None:
            return None

        return self._config.get_column_rule(column_name)

    def get_required_columns(self) -> List[str]:
        """
        필수 컬럼 목록을 반환합니다.

        Returns:
            List[str]: 필수 컬럼 이름 목록
        """
        if self._config is None:
            return []

        return self._config.get_required_columns()

    def get_optional_columns(self) -> List[str]:
        """
        선택적 컬럼 목록을 반환합니다.

        Returns:
            List[str]: 선택적 컬럼 이름 목록
        """
        if self._config is None:
            return []

        return self._config.get_optional_columns()

    def get_all_column_names(self) -> List[str]:
        """
        모든 컬럼 이름 목록을 반환합니다.

        Returns:
            List[str]: 모든 컬럼 이름 목록
        """
        if self._config is None:
            return []

        return [rule.name for rule in self._config.columns]

    def get_file_info(self) -> Optional[FileInfo]:
        """
        파일 정보를 반환합니다.

        Returns:
            Optional[FileInfo]: 파일 정보 객체
        """
        if self._config is None:
            return None

        return self._config.file_info

    def get_config(self) -> Optional[ValidationConfig]:
        """
        현재 로드된 설정을 반환합니다.

        Returns:
            Optional[ValidationConfig]: 현재 설정 객체
        """
        return self._config

    def get_config_path(self) -> Optional[str]:
        """
        현재 로드된 설정 파일 경로를 반환합니다.

        Returns:
            Optional[str]: 설정 파일 경로
        """
        return self._config_path

    def reload_config(self) -> ValidationConfig:
        """
        현재 설정 파일을 다시 로드합니다.

        Returns:
            ValidationConfig: 다시 로드된 설정 객체

        Raises:
            ValueError: 설정 파일이 로드되지 않은 경우
        """
        if self._config_path is None:
            raise ValueError("로드된 설정 파일이 없습니다")

        return self.load_config(self._config_path)

    def save_config(self, config: ValidationConfig, output_path: str) -> None:
        """
        설정을 YAML 파일로 저장합니다.

        Args:
            config: 저장할 설정 객체
            output_path: 출력 파일 경로
        """
        try:
            # ValidationConfig를 딕셔너리로 변환
            config_dict = self._config_to_dict(config)

            # YAML 파일로 저장
            with open(output_path, "w", encoding="utf-8") as file:
                yaml.dump(
                    config_dict,
                    file,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )

        except Exception as e:
            raise Exception(f"설정 저장 중 오류 발생: {e}")

    def create_sample_config(self, output_path: str) -> None:
        """
        샘플 설정 파일을 생성합니다.

        Args:
            output_path: 출력 파일 경로
        """
        sample_config = {
            "file_info": {
                "file_type": "csv",
                "expected_rows": 1000,
                "encoding": "utf-8",
                "delimiter": ",",
                "has_header": True,
                "json_schema": None,
                "json_root_path": None,
                "jsonl_array_mode": False,
            },
            "columns": [
                {
                    "name": "id",
                    "type": "integer",
                    "required": True,
                    "range": {"min": 1, "max": 999999},
                },
                {
                    "name": "name",
                    "type": "string",
                    "required": True,
                    "length": {"min": 1, "max": 100},
                },
                {"name": "email", "type": "email", "required": True},
                {
                    "name": "age",
                    "type": "integer",
                    "required": False,
                    "range": {"min": 0, "max": 120},
                },
                {
                    "name": "category",
                    "type": "string",
                    "required": True,
                    "allowed_values": ["A", "B", "C"],
                    "case_sensitive": False,
                },
                {
                    "name": "created_date",
                    "type": "datetime",
                    "required": True,
                    "format": "%Y-%m-%d %H:%M:%S",
                },
            ],
        }

        try:
            with open(output_path, "w", encoding="utf-8") as file:
                yaml.dump(
                    sample_config,
                    file,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
        except Exception as e:
            raise Exception(f"샘플 설정 파일 생성 중 오류 발생: {e}")

    def create_json_sample_config(self, output_path: str) -> None:
        """
        JSON 파일용 샘플 설정 파일을 생성합니다.

        Args:
            output_path: 출력 파일 경로
        """
        sample_config = {
            "file_info": {
                "file_type": "json",
                "expected_rows": None,
                "encoding": "utf-8",
                "delimiter": ",",
                "has_header": True,
                "json_schema": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "name": {"type": "string"},
                        "email": {"type": "string", "format": "email"}
                    },
                    "required": ["id", "name", "email"]
                },
                "json_root_path": None,
                "jsonl_array_mode": False,
            },
            "columns": [
                {
                    "name": "id",
                    "type": "integer",
                    "required": True,
                    "range": {"min": 1, "max": 999999},
                },
                {
                    "name": "name",
                    "type": "string",
                    "required": True,
                    "length": {"min": 1, "max": 100},
                },
                {"name": "email", "type": "email", "required": True},
                {
                    "name": "age",
                    "type": "integer",
                    "required": False,
                    "range": {"min": 0, "max": 120},
                },
                {
                    "name": "address",
                    "type": "object",
                    "required": False,
                },
                {
                    "name": "tags",
                    "type": "array",
                    "required": False,
                },
            ],
        }

        try:
            with open(output_path, "w", encoding="utf-8") as file:
                yaml.dump(
                    sample_config,
                    file,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
        except Exception as e:
            raise Exception(f"JSON 샘플 설정 파일 생성 중 오류 발생: {e}")

    def create_jsonl_sample_config(self, output_path: str) -> None:
        """
        JSONL 파일용 샘플 설정 파일을 생성합니다.

        Args:
            output_path: 출력 파일 경로
        """
        sample_config = {
            "file_info": {
                "file_type": "jsonl",
                "expected_rows": None,
                "encoding": "utf-8",
                "delimiter": ",",
                "has_header": True,
                "json_schema": None,
                "json_root_path": None,
                "jsonl_array_mode": False,
            },
            "columns": [
                {
                    "name": "id",
                    "type": "integer",
                    "required": True,
                    "range": {"min": 1, "max": 999999},
                },
                {
                    "name": "name",
                    "type": "string",
                    "required": True,
                    "length": {"min": 1, "max": 100},
                },
                {"name": "email", "type": "email", "required": True},
                {
                    "name": "age",
                    "type": "integer",
                    "required": False,
                    "range": {"min": 0, "max": 120},
                },
                {
                    "name": "created_at",
                    "type": "datetime",
                    "required": True,
                    "format": "%Y-%m-%d %H:%M:%S",
                },
            ],
        }

        try:
            with open(output_path, "w", encoding="utf-8") as file:
                yaml.dump(
                    sample_config,
                    file,
                    default_flow_style=False,
                    allow_unicode=True,
                    sort_keys=False,
                )
        except Exception as e:
            raise Exception(f"JSONL 샘플 설정 파일 생성 중 오류 발생: {e}")

    def _validate_business_rules(self, config: ValidationConfig) -> None:
        """
        비즈니스 로직에 따른 추가 검증을 수행합니다.

        Args:
            config: 검증할 설정 객체

        Raises:
            ValueError: 비즈니스 규칙 위반 시
        """
        # 1. 컬럼 이름 중복 검사 (이미 ValidationConfig에서 처리됨)

        # 2. 데이터 타입별 필수 속성 검사
        for rule in config.columns:
            if rule.type == DataType.INTEGER or rule.type == DataType.FLOAT:
                # 숫자 타입의 경우 range 검증 권장
                pass
            elif rule.type == DataType.STRING:
                # 문자열 타입의 경우 length 검증 권장
                pass
            elif rule.type == DataType.DATETIME:
                # 날짜/시간 타입의 경우 format 필수
                if rule.format is None:
                    raise ValueError(
                        f"컬럼 '{rule.name}': datetime 타입은 format이 필요합니다"
                    )
            elif rule.type == DataType.EMAIL:
                # 이메일 타입은 특별한 검증 불필요
                pass
            elif rule.type == DataType.PHONE:
                # 전화번호 타입은 특별한 검증 불필요
                pass

        # 3. 파일 정보 검증
        if (
            config.file_info.expected_rows is not None
            and config.file_info.expected_rows <= 0
        ):
            raise ValueError("expected_rows는 0보다 커야 합니다")

    def _config_to_dict(self, config: ValidationConfig) -> Dict[str, Any]:
        """
        ValidationConfig 객체를 딕셔너리로 변환합니다.

        Args:
            config: 변환할 설정 객체

        Returns:
            Dict[str, Any]: 변환된 딕셔너리
        """
        return config.dict()

    def get_config_summary(self) -> Dict[str, Any]:
        """
        설정 요약 정보를 반환합니다.

        Returns:
            Dict[str, Any]: 설정 요약 정보
        """
        if self._config is None:
            return {"status": "not_loaded"}

        return {
            "status": "loaded",
            "config_path": self._config_path,
            "file_info": {
                "encoding": self._config.file_info.encoding,
                "delimiter": self._config.file_info.delimiter,
                "has_header": self._config.file_info.has_header,
                "expected_rows": self._config.file_info.expected_rows,
            },
            "columns": {
                "total": len(self._config.columns),
                "required": len(self.get_required_columns()),
                "optional": len(self.get_optional_columns()),
                "types": list(set(rule.type for rule in self._config.columns)),
            },
        }
