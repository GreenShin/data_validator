"""
통합 테스트 - 전체 워크플로우 테스트
"""

import pytest
import tempfile
import os
import time
from pathlib import Path

from src.core.validator import DataValidator
from src.models.validation_rule import ValidationConfig, FileInfo, ValidationRule, DataType


class TestDataValidatorIntegration:
    """DataValidator 통합 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.temp_dir = tempfile.mkdtemp()
        self.validator = None
    
    def teardown_method(self):
        """각 테스트 메서드 실행 후 정리"""
        if self.validator:
            self.validator.close()
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_csv(self, content: str, filename: str = "test.csv") -> str:
        """테스트용 CSV 파일 생성"""
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    def create_test_config(self, config_data: dict, filename: str = "test_config.yml") -> str:
        """테스트용 설정 파일 생성"""
        file_path = os.path.join(self.temp_dir, filename)
        import yaml
        with open(file_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
        return file_path
    
    def test_complete_validation_workflow_valid(self):
        """완전한 검증 워크플로우 - 유효한 데이터"""
        # 테스트 데이터 생성
        csv_content = "id,name,email,age\n1,김철수,test@aaa.bbb.ccc,30\n2,이영희,test@aaa.bbb.ccc,25"
        csv_path = self.create_test_csv(csv_content)
        
        # 설정 파일 생성
        config_data = {
            "file_info": {
                "expected_rows": 2,
                "encoding": "utf-8",
                "delimiter": ",",
                "has_header": True
            },
            "columns": [
                {
                    "name": "id",
                    "type": "integer",
                    "required": True,
                    "range": {"min": 1, "max": 100}
                },
                {
                    "name": "name",
                    "type": "string",
                    "required": True,
                    "length": {"min": 2, "max": 20}
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
                }
            ]
        }
        config_path = self.create_test_config(config_data)
        
        # 검증 실행
        self.validator = DataValidator(config_path, verbose=False)
        result = self.validator.validate_file(csv_path)
        
        # 결과 검증
        assert result is not None
        assert result.file_name == "test.csv"
        assert result.total_rows == 2
        assert result.total_columns == 4
        assert result.structural_valid == True
        assert result.format_valid == True
        assert len(result.errors) == 0
        assert result.processing_time > 0
    
    def test_complete_validation_workflow_with_errors(self):
        """완전한 검증 워크플로우 - 오류가 있는 데이터"""
        # 테스트 데이터 생성 (오류 포함)
        csv_content = "id,name,email,age\n1,김,test@aaa.bbb.ccc,15\n2,이영희,test@aaa.bbb.ccc,25"
        csv_path = self.create_test_csv(csv_content)
        
        # 설정 파일 생성
        config_data = {
            "file_info": {
                "expected_rows": 2,
                "encoding": "utf-8",
                "delimiter": ",",
                "has_header": True
            },
            "columns": [
                {
                    "name": "id",
                    "type": "integer",
                    "required": True,
                    "range": {"min": 1, "max": 100}
                },
                {
                    "name": "name",
                    "type": "string",
                    "required": True,
                    "length": {"min": 2, "max": 20}  # "김"은 너무 짧음
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
                    "range": {"min": 18, "max": 100}  # 15는 범위 초과
                }
            ]
        }
        config_path = self.create_test_config(config_data)
        
        # 검증 실행
        self.validator = DataValidator(config_path, verbose=False)
        result = self.validator.validate_file(csv_path)
        
        # 결과 검증
        assert result is not None
        assert result.file_name == "test.csv"
        assert result.total_rows == 2
        assert result.total_columns == 4
        assert result.structural_valid == True
        assert result.format_valid == False  # 형식 오류가 있음
        assert len(result.errors) > 0  # 오류가 있어야 함
        
        # 오류 유형 확인
        error_types = [error.error_type for error in result.errors]
        assert any("length" in error_type for error_type in error_types)  # 길이 오류
        assert any("range" in error_type for error_type in error_types)  # 범위 오류 (age < 18)
    
    def test_structural_validation_errors(self):
        """구조적 검증 오류 테스트"""
        # 잘못된 구조의 CSV 파일 생성
        csv_content = "id,name\n1,김철수\n2,이영희,extra_column"  # 컬럼 수 불일치
        csv_path = self.create_test_csv(csv_content)
        
        # 설정 파일 생성
        config_data = {
            "file_info": {
                "expected_rows": 2,
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
        config_path = self.create_test_config(config_data)
        
        # 검증 실행
        self.validator = DataValidator(config_path, verbose=False)
        result = self.validator.validate_file(csv_path)
        
        # 결과 검증
        assert result is not None
        assert result.structural_valid == False  # 구조적 오류가 있어야 함
        assert len(result.errors) > 0
        
        # 구조적 오류 확인
        error_types = [error.error_type for error in result.errors]
        assert any("structural" in error_type for error_type in error_types)
    
    def test_folder_validation(self):
        """폴더 내 여러 파일 검증 테스트"""
        # 여러 CSV 파일 생성
        csv1_content = "id,name\n1,김철수\n2,이영희"
        csv2_content = "id,email\n1,test@aaa.bbb.ccc\n2,test@aaa.bbb.ccc"
        
        csv1_path = self.create_test_csv(csv1_content, "file1.csv")
        csv2_path = self.create_test_csv(csv2_content, "file2.csv")
        
        # 설정 파일 생성
        config_data = {
            "file_info": {
                "expected_rows": None,
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
                    "required": False
                },
                {
                    "name": "email",
                    "type": "email",
                    "required": False
                }
            ]
        }
        config_path = self.create_test_config(config_data)
        
        # 폴더 검증 실행
        self.validator = DataValidator(config_path, verbose=False)
        results = self.validator.validate_folder(self.temp_dir, self.temp_dir)
        
        # 결과 검증
        assert len(results) == 2
        assert all(result is not None for result in results)
        
        # 각 파일의 결과 확인
        file_names = [result.file_name for result in results]
        assert "file1.csv" in file_names
        assert "file2.csv" in file_names
    
    def test_large_file_performance(self):
        """대용량 파일 성능 테스트"""
        # 대용량 CSV 파일 생성 (1000행)
        csv_content = "id,name,email,age\n"
        for i in range(1000):
            csv_content += f"{i+1},사용자{i+1},test@aaa.bbb.ccc,{20 + (i % 50)}\n"
        
        csv_path = self.create_test_csv(csv_content, "large_file.csv")
        
        # 설정 파일 생성
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
                    "required": True
                },
                {
                    "name": "age",
                    "type": "integer",
                    "required": True,
                    "range": {"min": 18, "max": 100}
                }
            ]
        }
        config_path = self.create_test_config(config_data)
        
        # 성능 측정
        start_time = time.time()
        self.validator = DataValidator(config_path, verbose=False)
        result = self.validator.validate_file(csv_path)
        end_time = time.time()
        
        # 결과 검증
        assert result is not None
        assert result.total_rows == 1000
        assert result.structural_valid == True
        assert result.format_valid == True
        assert len(result.errors) == 0
        
        # 성능 검증 (1000행을 5초 이내에 처리해야 함)
        processing_time = end_time - start_time
        assert processing_time < 5.0
        
        # 처리 속도 계산
        rows_per_second = result.total_rows / processing_time
        assert rows_per_second > 200  # 초당 200행 이상 처리해야 함
    
    def test_memory_efficiency(self):
        """메모리 효율성 테스트"""
        import psutil
        import os
        
        # 대용량 파일 생성 (5000행)
        csv_content = "id,name,email,age\n"
        for i in range(5000):
            csv_content += f"{i+1},사용자{i+1},test@aaa.bbb.ccc,{20 + (i % 50)}\n"
        
        csv_path = self.create_test_csv(csv_content, "memory_test.csv")
        
        # 설정 파일 생성
        config_data = {
            "file_info": {
                "expected_rows": 5000,
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
                    "required": True
                },
                {
                    "name": "age",
                    "type": "integer",
                    "required": True
                }
            ]
        }
        config_path = self.create_test_config(config_data)
        
        # 메모리 사용량 측정
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        self.validator = DataValidator(config_path, verbose=False)
        result = self.validator.validate_file(csv_path)
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before
        
        # 결과 검증
        assert result is not None
        assert result.total_rows == 5000
        
        # 메모리 사용량이 100MB 이하로 증가해야 함 (스트리밍 처리)
        assert memory_increase < 100
    
    def test_error_handling_robustness(self):
        """오류 처리 견고성 테스트"""
        # 잘못된 설정 파일
        config_data = {
            "file_info": {
                "expected_rows": "invalid",  # 잘못된 타입
                "encoding": "utf-8",
                "delimiter": ",",
                "has_header": True
            },
            "columns": [
                {
                    "name": "id",
                    "type": "invalid_type",  # 잘못된 타입
                    "required": True
                }
            ]
        }
        config_path = self.create_test_config(config_data)
        
        # 잘못된 설정으로 검증기 생성 시도
        with pytest.raises(Exception):  # 설정 로드 오류
            self.validator = DataValidator(config_path, verbose=False)
    
    def test_config_reload_functionality(self):
        """설정 다시 로드 기능 테스트"""
        # 초기 설정
        csv_content = "id,name\n1,김철수\n2,이영희"
        csv_path = self.create_test_csv(csv_content)
        
        config_data = {
            "file_info": {
                "expected_rows": 2,
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
        config_path = self.create_test_config(config_data)
        
        # 검증기 생성
        self.validator = DataValidator(config_path, verbose=False)
        
        # 설정 수정
        config_data["columns"].append({
            "name": "email",
            "type": "email",
            "required": True
        })
        
        import yaml
        with open(config_path, 'w', encoding='utf-8') as f:
            yaml.dump(config_data, f, default_flow_style=False, allow_unicode=True)
        
        # 설정 다시 로드
        new_config = self.validator.reload_config()
        
        # 새로운 컬럼 규칙 확인
        email_rule = self.validator.config_manager.get_column_rule("email")
        assert email_rule is not None
        assert email_rule.type == DataType.EMAIL
    
    def test_result_file_generation(self):
        """결과 파일 생성 테스트"""
        # 테스트 데이터 생성
        csv_content = "id,name,email\n1,김철수,test@aaa.bbb.ccc\n2,이영희,test@aaa.bbb.ccc"
        csv_path = self.create_test_csv(csv_content)
        
        # 설정 파일 생성
        config_data = {
            "file_info": {
                "expected_rows": 2,
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
                    "required": True
                }
            ]
        }
        config_path = self.create_test_config(config_data)
        
        # 검증 실행
        self.validator = DataValidator(config_path, verbose=False)
        result = self.validator.validate_file(csv_path)
        
        # 결과 파일 생성
        from src.cli.commands import _save_single_result
        _save_single_result(result, self.temp_dir, "all", self.validator)
        
        # 결과 파일 생성 확인
        result_files = list(Path(self.temp_dir).glob("test_*.md"))
        result_files.extend(Path(self.temp_dir).glob("test_*.html"))
        result_files.extend(Path(self.temp_dir).glob("test_*.json"))
        
        assert len(result_files) >= 3  # 최소 3개 파일 (md, html, json)
        
        # 각 파일이 비어있지 않은지 확인
        for file_path in result_files:
            assert file_path.stat().st_size > 0


if __name__ == "__main__":
    pytest.main([__file__])
