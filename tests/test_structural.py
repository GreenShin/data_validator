"""
구조정확성 검증 모듈 단위 테스트
"""

import pytest
import tempfile
import os
from pathlib import Path

from src.core.structural import StructuralValidator
from src.models.validation_rule import FileInfo


class TestStructuralValidator:
    """StructuralValidator 클래스 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.validator = StructuralValidator()
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """각 테스트 메서드 실행 후 정리"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def create_test_csv(self, content: str, filename: str = "test.csv") -> str:
        """테스트용 CSV 파일 생성"""
        file_path = os.path.join(self.temp_dir, filename)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return file_path
    
    def test_validate_csv_format_valid(self):
        """유효한 CSV 포맷 검증 테스트"""
        csv_content = "name,age,email\n김철수,30,test@aaa.bbb.ccc\n이영희,25,test@aaa.bbb.ccc"
        file_path = self.create_test_csv(csv_content)
        
        file_info = FileInfo(
            expected_rows=2,
            encoding="utf-8",
            delimiter=",",
            has_header=True
        )
        
        is_valid = self.validator.validate_csv_format(file_path, file_info)
        assert is_valid == True
        assert len(self.validator.errors) == 0
    
    def test_validate_csv_format_invalid_delimiter(self):
        """잘못된 구분자 검증 테스트"""
        csv_content = "name;age;email\n김철수;30;test@aaa.bbb.ccc\n이영희;25;test@aaa.bbb.ccc"
        file_path = self.create_test_csv(csv_content)
        
        file_info = FileInfo(
            expected_rows=2,
            encoding="utf-8",
            delimiter=",",  # 실제로는 세미콜론 사용
            has_header=True
        )
        
        is_valid = self.validator.validate_csv_format(file_path, file_info)
        assert is_valid == False
        assert len(self.validator.errors) > 0
    
    def test_validate_encoding_utf8(self):
        """UTF-8 인코딩 검증 테스트"""
        csv_content = "name,age\n김철수,30\n이영희,25"
        file_path = self.create_test_csv(csv_content)
        
        file_info = FileInfo(
            expected_rows=2,
            encoding="utf-8",
            delimiter=",",
            has_header=True
        )
        
        is_valid = self.validator.validate_encoding(file_path, "utf-8")
        assert is_valid == True
    
    def test_validate_encoding_invalid(self):
        """잘못된 인코딩 검증 테스트"""
        csv_content = "name,age\n김철수,30\n이영희,25"
        file_path = self.create_test_csv(csv_content)
        
        is_valid = self.validator.validate_encoding(file_path, "ascii")
        assert is_valid == False
        assert len(self.validator.errors) > 0
    
    def test_validate_row_count_correct(self):
        """정확한 행 수 검증 테스트"""
        csv_content = "name,age\n김철수,30\n이영희,25\n박민수,35"
        file_path = self.create_test_csv(csv_content)
        
        is_valid = self.validator.validate_row_count(file_path, 3)
        assert is_valid == True
        assert len(self.validator.errors) == 0
    
    def test_validate_row_count_incorrect(self):
        """잘못된 행 수 검증 테스트"""
        csv_content = "name,age\n김철수,30\n이영희,25"
        file_path = self.create_test_csv(csv_content)
        
        is_valid = self.validator.validate_row_count(file_path, 5)
        assert is_valid == False
        assert len(self.validator.errors) > 0
    
    def test_validate_delimiter_comma(self):
        """쉼표 구분자 검증 테스트"""
        csv_content = "name,age,email\n김철수,30,test@aaa.bbb.ccc"
        file_path = self.create_test_csv(csv_content)
        
        is_valid = self.validator.validate_delimiter(file_path, ",")
        assert is_valid == True
    
    def test_validate_delimiter_semicolon(self):
        """세미콜론 구분자 검증 테스트"""
        csv_content = "name;age;email\n김철수;30;test@aaa.bbb.ccc"
        file_path = self.create_test_csv(csv_content)
        
        is_valid = self.validator.validate_delimiter(file_path, ";")
        assert is_valid == True
    
    def test_validate_delimiter_tab(self):
        """탭 구분자 검증 테스트"""
        csv_content = "name\tage\temail\n김철수\t30\ttest@aaa.bbb.ccc"
        file_path = self.create_test_csv(csv_content)
        
        is_valid = self.validator.validate_delimiter(file_path, "\t")
        assert is_valid == True
    
    def test_validate_header_with_header(self):
        """헤더가 있는 경우 검증 테스트"""
        csv_content = "name,age,email\n김철수,30,test@aaa.bbb.ccc\n이영희,25,test@aaa.bbb.ccc"
        file_path = self.create_test_csv(csv_content)
        
        file_info = FileInfo(
            expected_rows=2,
            encoding="utf-8",
            delimiter=",",
            has_header=True
        )
        
        expected_columns = ["name", "age", "email"]
        is_valid = self.validator.validate_header(file_path, file_info, expected_columns)
        assert is_valid == True
    
    def test_validate_header_missing_column(self):
        """누락된 컬럼이 있는 경우 검증 테스트"""
        csv_content = "name,age\n김철수,30\n이영희,25"  # email 컬럼 누락
        file_path = self.create_test_csv(csv_content)
        
        file_info = FileInfo(
            expected_rows=2,
            encoding="utf-8",
            delimiter=",",
            has_header=True
        )
        
        expected_columns = ["name", "age", "email"]
        is_valid = self.validator.validate_header(file_path, file_info, expected_columns)
        assert is_valid == False
        assert len(self.validator.errors) > 0
    
    def test_validate_consistency_valid(self):
        """일관성 있는 CSV 파일 검증 테스트"""
        csv_content = "name,age,email\n김철수,30,test@aaa.bbb.ccc\n이영희,25,test@aaa.bbb.ccc"
        file_path = self.create_test_csv(csv_content)
        
        file_info = FileInfo(
            expected_rows=2,
            encoding="utf-8",
            delimiter=",",
            has_header=True
        )
        
        is_valid = self.validator.validate_consistency(file_path, file_info)
        assert is_valid == True
    
    def test_validate_consistency_inconsistent_columns(self):
        """컬럼 수가 일관성 없는 CSV 파일 검증 테스트"""
        csv_content = "name,age,email\n김철수,30\n이영희,25,test@aaa.bbb.ccc,extra"  # 컬럼 수 불일치
        file_path = self.create_test_csv(csv_content)
        
        file_info = FileInfo(
            expected_rows=2,
            encoding="utf-8",
            delimiter=",",
            has_header=True
        )
        
        is_valid = self.validator.validate_consistency(file_path, file_info)
        assert is_valid == False
        assert len(self.validator.errors) > 0
    
    def test_validate_all_comprehensive(self):
        """전체 구조 검증 테스트"""
        csv_content = "name,age,email\n김철수,30,test@aaa.bbb.ccc\n이영희,25,test@aaa.bbb.ccc"
        file_path = self.create_test_csv(csv_content)
        
        file_info = FileInfo(
            expected_rows=2,
            encoding="utf-8",
            delimiter=",",
            has_header=True
        )
        
        expected_columns = ["name", "age", "email"]
        is_valid, errors = self.validator.validate_all(file_path, file_info, expected_columns)
        
        assert is_valid == True
        assert len(errors) == 0
    
    def test_validate_all_with_errors(self):
        """오류가 있는 전체 구조 검증 테스트"""
        csv_content = "name,age\n김철수,30\n이영희,25"  # email 컬럼 누락, 행 수 부족
        file_path = self.create_test_csv(csv_content)
        
        file_info = FileInfo(
            expected_rows=3,  # 실제로는 2행
            encoding="utf-8",
            delimiter=",",
            has_header=True
        )
        
        expected_columns = ["name", "age", "email"]
        is_valid, errors = self.validator.validate_all(file_path, file_info, expected_columns)
        
        assert is_valid == False
        assert len(errors) > 0
    
    def test_nonexistent_file(self):
        """존재하지 않는 파일 검증 테스트"""
        file_path = os.path.join(self.temp_dir, "nonexistent.csv")
        
        file_info = FileInfo(
            expected_rows=2,
            encoding="utf-8",
            delimiter=",",
            has_header=True
        )
        
        is_valid = self.validator.validate_csv_format(file_path, file_info)
        assert is_valid == False
        assert len(self.validator.errors) > 0
    
    def test_empty_file(self):
        """빈 파일 검증 테스트"""
        file_path = self.create_test_csv("")
        
        file_info = FileInfo(
            expected_rows=0,
            encoding="utf-8",
            delimiter=",",
            has_header=False
        )
        
        is_valid = self.validator.validate_csv_format(file_path, file_info)
        assert is_valid == True  # 빈 파일도 유효한 CSV로 간주


if __name__ == "__main__":
    pytest.main([__file__])
