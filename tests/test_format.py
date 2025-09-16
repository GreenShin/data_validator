"""
형식정확성 검증 모듈 단위 테스트
"""

import pytest
from datetime import datetime

from src.core.format import FormatValidator
from src.models.validation_rule import ValidationRule, DataType
from src.models.error import ErrorType


class TestFormatValidator:
    """FormatValidator 클래스 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        self.validator = FormatValidator()
    
    def teardown_method(self):
        """각 테스트 메서드 실행 후 정리"""
        self.validator.errors.clear()
    
    def test_validate_integer_valid(self):
        """유효한 정수 검증 테스트"""
        rule = ValidationRule(
            name="age",
            type=DataType.INTEGER,
            required=True
        )
        
        is_valid = self.validator._validate_integer("30", rule)
        assert is_valid == True
        assert len(self.validator.errors) == 0
    
    def test_validate_integer_invalid(self):
        """잘못된 정수 검증 테스트"""
        rule = ValidationRule(
            name="age",
            type=DataType.INTEGER,
            required=True
        )
        
        is_valid = self.validator._validate_integer("abc", rule)
        assert is_valid == False
        assert len(self.validator.errors) > 0
        assert self.validator.errors[0].error_type == ErrorType.FORMAT_INVALID_INTEGER.value
    
    def test_validate_integer_with_range(self):
        """범위가 있는 정수 검증 테스트"""
        rule = ValidationRule(
            name="age",
            type=DataType.INTEGER,
            required=True,
            range={"min": 18, "max": 65}
        )
        
        # 유효한 범위
        is_valid = self.validator._validate_integer("30", rule)
        assert is_valid == True
        
        # 범위 초과
        is_valid = self.validator._validate_integer("70", rule)
        assert is_valid == False
        assert len(self.validator.errors) > 0
    
    def test_validate_float_valid(self):
        """유효한 실수 검증 테스트"""
        rule = ValidationRule(
            name="price",
            type=DataType.FLOAT,
            required=True
        )
        
        is_valid = self.validator._validate_float("99.99", rule)
        assert is_valid == True
        assert len(self.validator.errors) == 0
    
    def test_validate_float_invalid(self):
        """잘못된 실수 검증 테스트"""
        rule = ValidationRule(
            name="price",
            type=DataType.FLOAT,
            required=True
        )
        
        is_valid = self.validator._validate_float("abc", rule)
        assert is_valid == False
        assert len(self.validator.errors) > 0
        assert self.validator.errors[0].error_type == ErrorType.FORMAT_INVALID_FLOAT.value
    
    def test_validate_string_valid(self):
        """유효한 문자열 검증 테스트"""
        rule = ValidationRule(
            name="name",
            type=DataType.STRING,
            required=True
        )
        
        is_valid = self.validator._validate_string("김철수", rule)
        assert is_valid == True
        assert len(self.validator.errors) == 0
    
    def test_validate_string_with_length(self):
        """길이 제한이 있는 문자열 검증 테스트"""
        rule = ValidationRule(
            name="name",
            type=DataType.STRING,
            required=True,
            length={"min": 2, "max": 10}
        )
        
        # 유효한 길이
        is_valid = self.validator._validate_string("김철수", rule)
        assert is_valid == True
        
        # 너무 짧음
        is_valid = self.validator._validate_string("김", rule)
        assert is_valid == False
        assert len(self.validator.errors) > 0
        
        # 너무 김
        is_valid = self.validator._validate_string("김철수이영희박민수", rule)
        assert is_valid == False
        assert len(self.validator.errors) > 0
    
    def test_validate_email_valid(self):
        """유효한 이메일 검증 테스트"""
        rule = ValidationRule(
            name="email",
            type=DataType.EMAIL,
            required=True
        )
        
        is_valid = self.validator._validate_email("test@example.com", rule)
        assert is_valid == True
        assert len(self.validator.errors) == 0
    
    def test_validate_email_invalid(self):
        """잘못된 이메일 검증 테스트"""
        rule = ValidationRule(
            name="email",
            type=DataType.EMAIL,
            required=True
        )
        
        is_valid = self.validator._validate_email("invalid-email", rule)
        assert is_valid == False
        assert len(self.validator.errors) > 0
        assert self.validator.errors[0].error_type == ErrorType.FORMAT_INVALID_EMAIL.value
    
    def test_validate_phone_valid(self):
        """유효한 전화번호 검증 테스트"""
        rule = ValidationRule(
            name="phone",
            type=DataType.PHONE,
            required=True
        )
        
        is_valid = self.validator._validate_phone("010-1234-5678", rule)
        assert is_valid == True
        assert len(self.validator.errors) == 0
    
    def test_validate_phone_invalid(self):
        """잘못된 전화번호 검증 테스트"""
        rule = ValidationRule(
            name="phone",
            type=DataType.PHONE,
            required=True
        )
        
        is_valid = self.validator._validate_phone("123-456", rule)
        assert is_valid == False
        assert len(self.validator.errors) > 0
        assert self.validator.errors[0].error_type == ErrorType.FORMAT_INVALID_PHONE.value
    
    def test_validate_datetime_valid(self):
        """유효한 날짜/시간 검증 테스트"""
        rule = ValidationRule(
            name="created_at",
            type=DataType.DATETIME,
            required=True,
            format="%Y-%m-%d %H:%M:%S"
        )
        
        is_valid = self.validator._validate_datetime("2023-12-01 10:30:00", rule)
        assert is_valid == True
        assert len(self.validator.errors) == 0
    
    def test_validate_datetime_invalid(self):
        """잘못된 날짜/시간 검증 테스트"""
        rule = ValidationRule(
            name="created_at",
            type=DataType.DATETIME,
            required=True,
            format="%Y-%m-%d %H:%M:%S"
        )
        
        is_valid = self.validator._validate_datetime("2023-13-01 10:30:00", rule)  # 잘못된 월
        assert is_valid == False
        assert len(self.validator.errors) > 0
        assert self.validator.errors[0].error_type == ErrorType.FORMAT_INVALID_DATETIME.value
    
    def test_validate_boolean_valid(self):
        """유효한 불린 검증 테스트"""
        rule = ValidationRule(
            name="is_active",
            type=DataType.BOOLEAN,
            required=True
        )
        
        # 다양한 불린 값 테스트
        for value in ["true", "false", "1", "0", "yes", "no", "y", "n"]:
            is_valid = self.validator._validate_boolean(value, rule)
            assert is_valid == True
    
    def test_validate_boolean_invalid(self):
        """잘못된 불린 검증 테스트"""
        rule = ValidationRule(
            name="is_active",
            type=DataType.BOOLEAN,
            required=True
        )
        
        is_valid = self.validator._validate_boolean("maybe", rule)
        assert is_valid == False
        assert len(self.validator.errors) > 0
        assert self.validator.errors[0].error_type == ErrorType.FORMAT_INVALID_BOOLEAN.value
    
    def test_validate_categorical_valid(self):
        """유효한 범주형 데이터 검증 테스트"""
        rule = ValidationRule(
            name="category",
            type=DataType.STRING,
            required=True,
            allowed_values=["A", "B", "C"],
            case_sensitive=True
        )
        
        is_valid = self.validator.validate_categorical("A", rule)
        assert is_valid == True
        assert len(self.validator.errors) == 0
    
    def test_validate_categorical_invalid(self):
        """잘못된 범주형 데이터 검증 테스트"""
        rule = ValidationRule(
            name="category",
            type=DataType.STRING,
            required=True,
            allowed_values=["A", "B", "C"],
            case_sensitive=True
        )
        
        is_valid = self.validator.validate_categorical("D", rule)
        assert is_valid == False
        assert len(self.validator.errors) > 0
        assert self.validator.errors[0].error_type == ErrorType.FORMAT_INVALID_CATEGORY.value
    
    def test_validate_categorical_case_insensitive(self):
        """대소문자 구분 없는 범주형 데이터 검증 테스트"""
        rule = ValidationRule(
            name="category",
            type=DataType.STRING,
            required=True,
            allowed_values=["A", "B", "C"],
            case_sensitive=False
        )
        
        # 소문자로 입력해도 통과해야 함
        is_valid = self.validator.validate_categorical("a", rule)
        assert is_valid == True
        assert len(self.validator.errors) == 0
    
    def test_validate_pattern_valid(self):
        """유효한 정규표현식 패턴 검증 테스트"""
        rule = ValidationRule(
            name="product_code",
            type=DataType.STRING,
            required=True,
            pattern="^[A-Z]{2}\\d{4}$"  # 2글자 + 4숫자
        )
        
        is_valid = self.validator.validate_pattern("AB1234", rule)
        assert is_valid == True
        assert len(self.validator.errors) == 0
    
    def test_validate_pattern_invalid(self):
        """잘못된 정규표현식 패턴 검증 테스트"""
        rule = ValidationRule(
            name="product_code",
            type=DataType.STRING,
            required=True,
            pattern="^[A-Z]{2}\\d{4}$"  # 2글자 + 4숫자
        )
        
        is_valid = self.validator.validate_pattern("ABC123", rule)  # 3글자
        assert is_valid == False
        assert len(self.validator.errors) > 0
        assert self.validator.errors[0].error_type == ErrorType.FORMAT_INVALID_PATTERN.value
    
    def test_validate_range_integer(self):
        """정수 범위 검증 테스트"""
        rule = ValidationRule(
            name="score",
            type=DataType.INTEGER,
            required=True,
            range={"min": 0, "max": 100}
        )
        
        # 유효한 범위
        is_valid = self.validator.validate_range(50, rule)
        assert is_valid == True
        
        # 범위 초과
        is_valid = self.validator.validate_range(150, rule)
        assert is_valid == False
        assert len(self.validator.errors) > 0
    
    def test_validate_range_float(self):
        """실수 범위 검증 테스트"""
        rule = ValidationRule(
            name="rate",
            type=DataType.FLOAT,
            required=True,
            range={"min": 0.0, "max": 1.0}
        )
        
        # 유효한 범위
        is_valid = self.validator.validate_range(0.5, rule)
        assert is_valid == True
        
        # 범위 초과
        is_valid = self.validator.validate_range(1.5, rule)
        assert is_valid == False
        assert len(self.validator.errors) > 0
    
    def test_validate_all_comprehensive(self):
        """전체 형식 검증 테스트"""
        rule = ValidationRule(
            name="age",
            type=DataType.INTEGER,
            required=True,
            range={"min": 18, "max": 65}
        )
        
        is_valid = self.validator.validate_all(30, rule)
        assert is_valid == True
        assert len(self.validator.errors) == 0
    
    def test_validate_all_with_multiple_errors(self):
        """여러 오류가 있는 전체 형식 검증 테스트"""
        rule = ValidationRule(
            name="age",
            type=DataType.INTEGER,
            required=True,
            range={"min": 18, "max": 65}
        )
        
        is_valid = self.validator.validate_all(70, rule)  # 범위 초과
        assert is_valid == False
        assert len(self.validator.errors) > 0
    
    def test_required_field_validation(self):
        """필수 필드 검증 테스트"""
        rule = ValidationRule(
            name="name",
            type=DataType.STRING,
            required=True
        )
        
        # 빈 값
        is_valid = self.validator.validate_data_type("", rule)
        assert is_valid == False
        assert len(self.validator.errors) > 0
        assert self.validator.errors[0].error_type == ErrorType.FORMAT_MISSING_REQUIRED.value
        
        # None 값
        is_valid = self.validator.validate_data_type(None, rule)
        assert is_valid == False
        assert len(self.validator.errors) > 0
    
    def test_optional_field_validation(self):
        """선택적 필드 검증 테스트"""
        rule = ValidationRule(
            name="description",
            type=DataType.STRING,
            required=False
        )
        
        # 빈 값도 통과해야 함
        is_valid = self.validator.validate_data_type("", rule)
        assert is_valid == True
        
        # None 값도 통과해야 함
        is_valid = self.validator.validate_data_type(None, rule)
        assert is_valid == True


if __name__ == "__main__":
    pytest.main([__file__])
