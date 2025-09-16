"""
Format validation for CSV data.

이 모듈은 CSV 데이터의 형식정확성을 검증하는 기능을 제공합니다.
"""

import re
import email_validator
import phonenumbers
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from decimal import Decimal, InvalidOperation

from ..models import ValidationRule, ValidationError, DataType, ErrorType, ErrorRegistry


class FormatValidator:
    """CSV 데이터의 형식정확성을 검증하는 클래스"""

    def __init__(self):
        """FormatValidator 초기화"""
        self.errors: List[ValidationError] = []
        # 검증 결과 캐시 (메모리 효율성을 위해 제한적 사용)
        self._validation_cache = {}

    def validate_data_type(self, value: Any, rule: ValidationRule) -> bool:
        """
        데이터 타입을 검증합니다.

        Args:
            value: 검증할 값
            rule: 검증 규칙

        Returns:
            bool: 데이터 타입이 유효한지 여부
        """
        if value is None or value == "":
            if rule.required:
                error = ValidationError(
                    row_number=1,  # 실제 사용 시 올바른 행 번호로 설정
                    column_name=rule.name,
                    error_type=ErrorType.FORMAT_MISSING_REQUIRED.value,
                    actual_value=value,
                    expected_value="필수 값",
                    message=f"컬럼 '{rule.name}'은 필수 필드입니다",
                )
                self.errors.append(error)
                return False
            return True  # 선택적 필드이고 값이 비어있으면 통과

        try:
            if rule.type == DataType.INTEGER:
                return self._validate_integer(value, rule)
            elif rule.type == DataType.FLOAT:
                return self._validate_float(value, rule)
            elif rule.type == DataType.STRING:
                return self._validate_string(value, rule)
            elif rule.type == DataType.DATETIME:
                return self._validate_datetime(value, rule)
            elif rule.type == DataType.BOOLEAN:
                return self._validate_boolean(value, rule)
            elif rule.type == DataType.EMAIL:
                return self._validate_email(value, rule)
            elif rule.type == DataType.PHONE:
                return self._validate_phone(value, rule)
            else:
                return True

        except Exception as e:
            error = ValidationError(
                row_number=1,
                column_name=rule.name,
                error_type=ErrorType.FORMAT_INVALID_TYPE.value,
                actual_value=value,
                expected_value=rule.type.value,
                message=f"데이터 타입 검증 중 오류 발생: {e}",
            )
            self.errors.append(error)
            return False

    def validate_range(self, value: Any, rule: ValidationRule) -> bool:
        """
        데이터 범위를 검증합니다.

        Args:
            value: 검증할 값
            rule: 검증 규칙

        Returns:
            bool: 데이터 범위가 유효한지 여부
        """
        if value is None or value == "":
            return True  # 빈 값은 타입 검증에서 처리

        if rule.range is None:
            return True  # 범위 검증이 설정되지 않음

        try:
            if rule.type == DataType.INTEGER:
                int_value = int(value)
                min_val = rule.range.get("min")
                max_val = rule.range.get("max")

                if min_val is not None and int_value < min_val:
                    error = ValidationError(
                        row_number=1,
                        column_name=rule.name,
                        error_type=ErrorType.FORMAT_OUT_OF_RANGE.value,
                        actual_value=int_value,
                        expected_value=f">= {min_val}",
                        message=f"값 {int_value}은 최소값 {min_val}보다 작습니다",
                    )
                    self.errors.append(error)
                    return False

                if max_val is not None and int_value > max_val:
                    error = ValidationError(
                        row_number=1,
                        column_name=rule.name,
                        error_type=ErrorType.FORMAT_OUT_OF_RANGE.value,
                        actual_value=int_value,
                        expected_value=f"<= {max_val}",
                        message=f"값 {int_value}은 최대값 {max_val}보다 큽니다",
                    )
                    self.errors.append(error)
                    return False

            elif rule.type == DataType.FLOAT:
                float_value = float(value)
                min_val = rule.range.get("min")
                max_val = rule.range.get("max")

                if min_val is not None and float_value < min_val:
                    error = ValidationError(
                        row_number=1,
                        column_name=rule.name,
                        error_type=ErrorType.FORMAT_OUT_OF_RANGE.value,
                        actual_value=float_value,
                        expected_value=f">= {min_val}",
                        message=f"값 {float_value}은 최소값 {min_val}보다 작습니다",
                    )
                    self.errors.append(error)
                    return False

                if max_val is not None and float_value > max_val:
                    error = ValidationError(
                        row_number=1,
                        column_name=rule.name,
                        error_type=ErrorType.FORMAT_OUT_OF_RANGE.value,
                        actual_value=float_value,
                        expected_value=f"<= {max_val}",
                        message=f"값 {float_value}은 최대값 {max_val}보다 큽니다",
                    )
                    self.errors.append(error)
                    return False

            return True

        except (ValueError, TypeError) as e:
            error = ValidationError(
                row_number=1,
                column_name=rule.name,
                error_type=ErrorType.FORMAT_INVALID_TYPE.value,
                actual_value=value,
                expected_value="숫자 형식",
                message=f"범위 검증을 위한 숫자 변환 실패: {e}",
            )
            self.errors.append(error)
            return False

    def validate_categorical(self, value: Any, rule: ValidationRule) -> bool:
        """
        범주형 데이터를 검증합니다.

        Args:
            value: 검증할 값
            rule: 검증 규칙

        Returns:
            bool: 범주형 데이터가 유효한지 여부
        """
        if value is None or value == "":
            if rule.required:
                error = ValidationError(
                    row_number=1,
                    column_name=rule.name,
                    error_type=ErrorType.FORMAT_MISSING_REQUIRED.value,
                    actual_value=value,
                    expected_value="필수 값",
                    message=f"컬럼 '{rule.name}'은 필수 필드입니다",
                )
                self.errors.append(error)
                return False
            return True

        if rule.allowed_values is None:
            return True  # 허용 값 목록이 설정되지 않음

        str_value = str(value).strip()

        # 대소문자 구분 여부에 따른 비교
        if rule.case_sensitive:
            if str_value not in rule.allowed_values:
                error = ValidationError(
                    row_number=1,
                    column_name=rule.name,
                    error_type=ErrorType.FORMAT_INVALID_CATEGORY.value,
                    actual_value=str_value,
                    expected_value=rule.allowed_values,
                    message=f"값 '{str_value}'은 허용된 범주에 속하지 않습니다. 허용된 값: {rule.allowed_values}",
                )
                self.errors.append(error)
                return False
        else:
            # 대소문자 무시 비교
            allowed_values_lower = [v.lower() for v in rule.allowed_values]
            if str_value.lower() not in allowed_values_lower:
                error = ValidationError(
                    row_number=1,
                    column_name=rule.name,
                    error_type=ErrorType.FORMAT_INVALID_CATEGORY.value,
                    actual_value=str_value,
                    expected_value=rule.allowed_values,
                    message=f"값 '{str_value}'은 허용된 범주에 속하지 않습니다. 허용된 값: {rule.allowed_values}",
                )
                self.errors.append(error)
                return False

        return True

    def validate_pattern(self, value: Any, rule: ValidationRule) -> bool:
        """
        정규표현식 패턴을 검증합니다.

        Args:
            value: 검증할 값
            rule: 검증 규칙

        Returns:
            bool: 패턴이 일치하는지 여부
        """
        if value is None or value == "":
            return True  # 빈 값은 타입 검증에서 처리

        if rule.pattern is None:
            return True  # 패턴 검증이 설정되지 않음

        try:
            str_value = str(value)
            if not re.match(rule.pattern, str_value):
                error = ValidationError(
                    row_number=1,
                    column_name=rule.name,
                    error_type=ErrorType.FORMAT_INVALID_PATTERN.value,
                    actual_value=str_value,
                    expected_value=f"패턴: {rule.pattern}",
                    message=f"값 '{str_value}'이 지정된 패턴과 일치하지 않습니다",
                )
                self.errors.append(error)
                return False

            return True

        except re.error as e:
            error = ValidationError(
                row_number=1,
                column_name=rule.name,
                error_type=ErrorType.SYSTEM_CONFIG_ERROR.value,
                actual_value=rule.pattern,
                expected_value="올바른 정규표현식",
                message=f"잘못된 정규표현식 패턴: {e}",
            )
            self.errors.append(error)
            return False

    def validate_all(self, value: Any, rule: ValidationRule) -> bool:
        """
        모든 형식정확성 검증을 수행합니다.

        Args:
            value: 검증할 값
            rule: 검증 규칙

        Returns:
            bool: 모든 검증을 통과했는지 여부
        """
        # 1. 데이터 타입 검증
        type_valid = self.validate_data_type(value, rule)

        # 2. 범위 검증 (숫자 타입인 경우)
        range_valid = True
        if rule.type in [DataType.INTEGER, DataType.FLOAT] and rule.range is not None:
            range_valid = self.validate_range(value, rule)

        # 3. 범주형 데이터 검증
        categorical_valid = True
        if rule.allowed_values is not None:
            categorical_valid = self.validate_categorical(value, rule)

        # 4. 패턴 검증
        pattern_valid = True
        if rule.pattern is not None:
            pattern_valid = self.validate_pattern(value, rule)

        return type_valid and range_valid and categorical_valid and pattern_valid

    def _validate_integer(self, value: Any, rule: ValidationRule) -> bool:
        """정수 타입을 검증합니다."""
        try:
            int(value)
            return True
        except (ValueError, TypeError):
            error = ValidationError(
                row_number=1,
                column_name=rule.name,
                error_type=ErrorType.FORMAT_INVALID_TYPE.value,
                actual_value=value,
                expected_value="정수",
                message=f"값 '{value}'은 정수 형식이 아닙니다",
            )
            self.errors.append(error)
            return False

    def _validate_float(self, value: Any, rule: ValidationRule) -> bool:
        """실수 타입을 검증합니다."""
        try:
            float(value)
            return True
        except (ValueError, TypeError):
            error = ValidationError(
                row_number=1,
                column_name=rule.name,
                error_type=ErrorType.FORMAT_INVALID_TYPE.value,
                actual_value=value,
                expected_value="실수",
                message=f"값 '{value}'은 실수 형식이 아닙니다",
            )
            self.errors.append(error)
            return False

    def _validate_string(self, value: Any, rule: ValidationRule) -> bool:
        """문자열 타입을 검증합니다."""
        str_value = str(value)

        # 길이 검증
        if rule.length is not None:
            min_length = rule.length.get("min", 0)
            max_length = rule.length.get("max", float("inf"))

            if len(str_value) < min_length:
                error = ValidationError(
                    row_number=1,
                    column_name=rule.name,
                    error_type=ErrorType.FORMAT_INVALID_LENGTH.value,
                    actual_value=f"{len(str_value)}자",
                    expected_value=f">= {min_length}자",
                    message=f"문자열 길이 {len(str_value)}는 최소 길이 {min_length}보다 작습니다",
                )
                self.errors.append(error)
                return False

            if len(str_value) > max_length:
                error = ValidationError(
                    row_number=1,
                    column_name=rule.name,
                    error_type=ErrorType.FORMAT_INVALID_LENGTH.value,
                    actual_value=f"{len(str_value)}자",
                    expected_value=f"<= {max_length}자",
                    message=f"문자열 길이 {len(str_value)}는 최대 길이 {max_length}보다 큽니다",
                )
                self.errors.append(error)
                return False

        return True

    def _validate_datetime(self, value: Any, rule: ValidationRule) -> bool:
        """날짜/시간 타입을 검증합니다."""
        if rule.format is None:
            error = ValidationError(
                row_number=1,
                column_name=rule.name,
                error_type=ErrorType.SYSTEM_CONFIG_ERROR.value,
                actual_value="format 없음",
                expected_value="날짜 형식 지정",
                message=f"컬럼 '{rule.name}': datetime 타입은 format이 필요합니다",
            )
            self.errors.append(error)
            return False

        try:
            datetime.strptime(str(value), rule.format)
            return True
        except ValueError:
            error = ValidationError(
                row_number=1,
                column_name=rule.name,
                error_type=ErrorType.FORMAT_INVALID_DATETIME.value,
                actual_value=value,
                expected_value=f"형식: {rule.format}",
                message=f"값 '{value}'은 날짜/시간 형식 '{rule.format}'과 일치하지 않습니다",
            )
            self.errors.append(error)
            return False

    def _validate_boolean(self, value: Any, rule: ValidationRule) -> bool:
        """불린 타입을 검증합니다."""
        str_value = str(value).lower().strip()
        boolean_values = ["true", "false", "1", "0", "yes", "no", "y", "n"]

        if str_value not in boolean_values:
            error = ValidationError(
                row_number=1,
                column_name=rule.name,
                error_type=ErrorType.FORMAT_INVALID_TYPE.value,
                actual_value=value,
                expected_value="불린 값 (true/false, 1/0, yes/no)",
                message=f"값 '{value}'은 불린 형식이 아닙니다",
            )
            self.errors.append(error)
            return False

        return True

    def _validate_email(self, value: Any, rule: ValidationRule) -> bool:
        """이메일 타입을 검증합니다."""
        try:
            # DNS 검증을 비활성화하여 형식만 검증 (테스트 환경에서 example.com 등이 실패하지 않도록)
            email_validator.validate_email(str(value), check_deliverability=False)
            return True
        except email_validator.EmailNotValidError:
            error = ValidationError(
                row_number=1,
                column_name=rule.name,
                error_type=ErrorType.FORMAT_INVALID_EMAIL.value,
                actual_value=value,
                expected_value="올바른 이메일 형식",
                message=f"값 '{value}'은 올바른 이메일 형식이 아닙니다",
            )
            self.errors.append(error)
            return False

    def _validate_phone(self, value: Any, rule: ValidationRule) -> bool:
        """전화번호 타입을 검증합니다."""
        try:
            # 기본적으로 한국 번호로 파싱 시도
            phone_number = phonenumbers.parse(str(value), "KR")
            if phonenumbers.is_valid_number(phone_number):
                return True
            else:
                error = ValidationError(
                    row_number=1,
                    column_name=rule.name,
                    error_type=ErrorType.FORMAT_INVALID_PHONE.value,
                    actual_value=value,
                    expected_value="올바른 전화번호 형식",
                    message=f"값 '{value}'은 올바른 전화번호 형식이 아닙니다",
                )
                self.errors.append(error)
                return False
        except phonenumbers.NumberParseException:
            error = ValidationError(
                row_number=1,
                column_name=rule.name,
                error_type=ErrorType.FORMAT_INVALID_PHONE.value,
                actual_value=value,
                expected_value="올바른 전화번호 형식",
                message=f"값 '{value}'은 올바른 전화번호 형식이 아닙니다",
            )
            self.errors.append(error)
            return False

    def get_errors(self) -> List[ValidationError]:
        """발견된 오류 목록을 반환합니다."""
        return self.errors.copy()

    def clear_errors(self) -> None:
        """오류 목록을 초기화합니다."""
        self.errors.clear()
