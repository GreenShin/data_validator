"""
설정 관리 모듈 단위 테스트
"""

import pytest
import tempfile
import os
import yaml

from src.core.config import ConfigManager
from src.models.validation_rule import ValidationConfig, FileInfo, ValidationRule, DataType


class TestConfigManager:
    """ConfigManager 클래스 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.config_manager = ConfigManager()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """각 테스트 메서드 실행 후 정리"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_config_file(self, config_data: dict, filename: str = "test_config.yml") -> str:
        """테스트용 설정 파일 생성"""
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
        return file_path
    
    def test_load_config_valid(self):
        """유효한 설정 파일 로드 테스트"""
        config_data = {
            "file_info": {
                "expected_rows": 100,
                "encoding": "utf-8",
                "delimiter": ",",
                "has_header": True
            },
            "columns": [
                {
                    "name": "id",
                    "type": "integer",
                    "required": True
                },
                {
                    "name": "name",
                    "type": "string",
                    "required": True
                }
            ]
        }
        
        config_path = self.create_test_config_file(config_data)
        config = self.config_manager.load_config(config_path)
        
        assert isinstance(config, ValidationConfig)
        assert config.file_info.expected_rows == 100
        assert config.file_info.encoding == "utf-8"
        assert config.file_info.delimiter == ","
        assert config.file_info.has_header == True
        assert len(config.columns) == 2
        assert config.columns[0].name == "id"
        assert config.columns[0].type == DataType.INTEGER
        assert config.columns[1].name == "name"
        assert config.columns[1].type == DataType.STRING
    
    def test_load_config_nonexistent_file(self):
        """존재하지 않는 설정 파일 로드 테스트"""
        config_path = os.path.join(self.temp_dir, "nonexistent.yml")
        
        with pytest.raises(FileNotFoundError):
            self.config_manager.load_config(config_path)
    
    def test_load_config_invalid_yaml(self):
        """잘못된 YAML 형식 파일 로드 테스트"""
        config_path = os.path.join(self.temp_dir, "invalid.yml")
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write("invalid: yaml: content: [")
        
        with pytest.raises(yaml.YAMLError):
            self.config_manager.load_config(config_path)
    
    def test_load_config_empty_file(self):
        """빈 설정 파일 로드 테스트"""
        config_path = os.path.join(self.temp_dir, "empty.yml")
        with open(config_path, 'w', encoding='utf-8') as f:
            f.write("")
        
        with pytest.raises(ValueError, match="설정 파일이 비어있습니다"):
            self.config_manager.load_config(config_path)
    
    def test_load_config_invalid_schema(self):
        """잘못된 스키마 설정 파일 로드 테스트"""
        config_data = {
            "file_info": {
                "expected_rows": "invalid",  # 정수가 아닌 값
                "encoding": "utf-8",
                "delimiter": ",",
                "has_header": True
            },
            "columns": [
                {
                    "name": "id",
                    "type": "invalid_type",  # 잘못된 데이터 타입
                    "required": True
                }
            ]
        }
        
        config_path = self.create_test_config_file(config_data)
        
        with pytest.raises(ValueError, match="설정 검증 오류"):
            self.config_manager.load_config(config_path)
    
    def test_validate_config_valid(self):
        """유효한 설정 검증 테스트"""
        config_data = {
            "file_info": {
                "expected_rows": 100,
                "encoding": "utf-8",
                "delimiter": ",",
                "has_header": True
            },
            "columns": [
                {
                    "name": "id",
                    "type": "integer",
                    "required": True
                }
            ]
        }
        
        config_path = self.create_test_config_file(config_data)
        config = self.config_manager.load_config(config_path)
        
        is_valid = self.config_manager.validate_config(config)
        assert is_valid == True
    
    def test_validate_config_invalid(self):
        """잘못된 설정 검증 테스트"""
        # 잘못된 설정 객체 생성
        invalid_config = ValidationConfig(
            file_info=FileInfo(
                expected_rows=100,
                encoding="utf-8",
                delimiter=",",
                has_header=True
            ),
            columns=[
                ValidationRule(
                    name="id",
                    type=DataType.INTEGER,
                    required=True,
                    range={"min": 100, "max": 50}  # 잘못된 범위 (min > max)
                )
            ]
        )
        
        is_valid = self.config_manager.validate_config(invalid_config)
        assert is_valid == False
    
    def test_get_column_rule_existing(self):
        """존재하는 컬럼 규칙 조회 테스트"""
        config_data = {
            "file_info": {
                "expected_rows": 100,
                "encoding": "utf-8",
                "delimiter": ",",
                "has_header": True
            },
            "columns": [
                {
                    "name": "id",
                    "type": "integer",
                    "required": True
                },
                {
                    "name": "name",
                    "type": "string",
                    "required": True
                }
            ]
        }
        
        config_path = self.create_test_config_file(config_data)
        config = self.config_manager.load_config(config_path)
        
        rule = self.config_manager.get_column_rule("id")
        assert rule is not None
        assert rule.name == "id"
        assert rule.type == DataType.INTEGER
        assert rule.required == True
        
        rule = self.config_manager.get_column_rule("name")
        assert rule is not None
        assert rule.name == "name"
        assert rule.type == DataType.STRING
    
    def test_get_column_rule_nonexistent(self):
        """존재하지 않는 컬럼 규칙 조회 테스트"""
        config_data = {
            "file_info": {
                "expected_rows": 100,
                "encoding": "utf-8",
                "delimiter": ",",
                "has_header": True
            },
            "columns": [
                {
                    "name": "id",
                    "type": "integer",
                    "required": True
                }
            ]
        }
        
        config_path = self.create_test_config_file(config_data)
        config = self.config_manager.load_config(config_path)
        
        rule = self.config_manager.get_column_rule("nonexistent")
        assert rule is None
    
    def test_create_sample_config(self):
        """샘플 설정 파일 생성 테스트"""
        sample_path = os.path.join(self.temp_dir, "sample.yml")
        self.config_manager.create_sample_config(sample_path)
        
        assert os.path.exists(sample_path)
        
        # 생성된 파일이 유효한 YAML인지 확인
        config = self.config_manager.load_config(sample_path)
        assert isinstance(config, ValidationConfig)
        assert len(config.columns) > 0
    
    def test_get_config_summary(self):
        """설정 요약 정보 조회 테스트"""
        config_data = {
            "file_info": {
                "expected_rows": 100,
                "encoding": "utf-8",
                "delimiter": ",",
                "has_header": True
            },
            "columns": [
                {
                    "name": "id",
                    "type": "integer",
                    "required": True
                },
                {
                    "name": "name",
                    "type": "string",
                    "required": True
                },
                {
                    "name": "email",
                    "type": "email",
                    "required": False
                }
            ]
        }
        
        config_path = self.create_test_config_file(config_data)
        config = self.config_manager.load_config(config_path)
        
        summary = self.config_manager.get_config_summary()
        assert "file_info" in summary
        assert "columns" in summary
        assert summary["file_info"]["encoding"] == "utf-8"
        assert summary["file_info"]["delimiter"] == ","
        assert summary["columns"]["total_count"] == 3
        assert summary["columns"]["required_count"] == 2
    
    def test_complex_validation_rules(self):
        """복잡한 검증 규칙 테스트"""
        config_data = {
            "file_info": {
                "expected_rows": 1000,
                "encoding": "utf-8",
                "delimiter": ",",
                "has_header": True
            },
            "columns": [
                {
                    "name": "id",
                    "type": "integer",
                    "required": True,
                    "range": {"min": 1, "max": 999999}
                },
                {
                    "name": "email",
                    "type": "email",
                    "required": True
                },
                {
                    "name": "age",
                    "type": "integer",
                    "required": True,
                    "range": {"min": 18, "max": 100}
                },
                {
                    "name": "category",
                    "type": "string",
                    "required": True,
                    "allowed_values": ["A", "B", "C"],
                    "case_sensitive": False
                },
                {
                    "name": "phone",
                    "type": "string",
                    "required": True,
                    "pattern": "^010-\\d{4}-\\d{4}$"
                },
                {
                    "name": "created_at",
                    "type": "datetime",
                    "required": True,
                    "format": "%Y-%m-%d %H:%M:%S"
                }
            ]
        }
        
        config_path = self.create_test_config_file(config_data)
        config = self.config_manager.load_config(config_path)
        
        assert len(config.columns) == 6
        
        # ID 컬럼 검증
        id_rule = self.config_manager.get_column_rule("id")
        assert id_rule.range == {"min": 1, "max": 999999}
        
        # 이메일 컬럼 검증
        email_rule = self.config_manager.get_column_rule("email")
        assert email_rule.type == DataType.EMAIL
        
        # 나이 컬럼 검증
        age_rule = self.config_manager.get_column_rule("age")
        assert age_rule.range == {"min": 18, "max": 100}
        
        # 카테고리 컬럼 검증
        category_rule = self.config_manager.get_column_rule("category")
        assert category_rule.allowed_values == ["A", "B", "C"]
        assert category_rule.case_sensitive == False
        
        # 전화번호 컬럼 검증
        phone_rule = self.config_manager.get_column_rule("phone")
        assert phone_rule.pattern == "^010-\\d{4}-\\d{4}$"
        
        # 날짜 컬럼 검증
        date_rule = self.config_manager.get_column_rule("created_at")
        assert date_rule.format == "%Y-%m-%d %H:%M:%S"
    
    def test_reload_config(self):
        """설정 파일 다시 로드 테스트"""
        # 초기 설정
        config_data = {
            "file_info": {
                "expected_rows": 100,
                "encoding": "utf-8",
                "delimiter": ",",
                "has_header": True
            },
            "columns": [
                {
                    "name": "id",
                    "type": "integer",
                    "required": True
                }
            ]
        }
        
        config_path = self.create_test_config_file(config_data)
        config1 = self.config_manager.load_config(config_path)
        
        # 설정 파일 수정
        config_data["columns"].append({
            "name": "name",
            "type": "string",
            "required": True
        })
        
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
        
        # 다시 로드
        config2 = self.config_manager.reload_config()
        
        assert len(config2.columns) == 2
        assert config2.columns[1].name == "name"
    
    def test_file_info_validation(self):
        """파일 정보 검증 테스트"""
        config_data = {
            "file_info": {
                "expected_rows": None,  # 행 수 제한 없음
                "encoding": "cp949",    # 다른 인코딩
                "delimiter": ";",       # 세미콜론 구분자
                "has_header": False     # 헤더 없음
            },
            "columns": [
                {
                    "name": "data",
                    "type": "string",
                    "required": True
                }
            ]
        }
        
        config_path = self.create_test_config_file(config_data)
        config = self.config_manager.load_config(config_path)
        
        assert config.file_info.expected_rows is None
        assert config.file_info.encoding == "cp949"
        assert config.file_info.delimiter == ";"
        assert config.file_info.has_header == False


if __name__ == "__main__":
    pytest.main([__file__])
