"""
File handling utilities for CSV validation.

이 모듈은 CSV 파일 읽기, 인코딩 감지, 파일 정보 수집 등의 기능을 제공합니다.
"""

import os
import csv
import chardet
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any, Optional, Iterator, Tuple
from datetime import datetime

from ..models import FileInfo, FileType
from ..core.json_parser import JSONParser


class FileHandler:
    """파일 처리를 담당하는 클래스 (CSV, JSON, JSONL 지원)"""

    def __init__(self):
        """FileHandler 초기화"""
        self.supported_encodings = [
            "utf-8",
            "utf-8-sig",
            "cp949",
            "euc-kr",
            "latin-1",
            "ascii",
        ]
        self.supported_delimiters = [",", ";", "\t", "|", " "]
        self.supported_extensions = {".csv", ".json", ".jsonl"}
        self.json_parser = JSONParser()

    def validate_file_exists(self, file_path: str) -> bool:
        """
        파일 존재 여부를 확인합니다.

        Args:
            file_path: 확인할 파일 경로

        Returns:
            bool: 파일이 존재하는지 여부
        """
        return os.path.exists(file_path) and os.path.isfile(file_path)

    def validate_file_readable(self, file_path: str) -> bool:
        """
        파일 읽기 권한을 확인합니다.

        Args:
            file_path: 확인할 파일 경로

        Returns:
            bool: 파일을 읽을 수 있는지 여부
        """
        return os.access(file_path, os.R_OK)

    def detect_encoding(self, file_path: str) -> str:
        """
        파일의 인코딩을 자동으로 감지합니다.

        Args:
            file_path: 감지할 파일 경로

        Returns:
            str: 감지된 인코딩
        """
        try:
            # 파일의 일부분을 읽어서 인코딩 감지
            with open(file_path, "rb") as f:
                raw_data = f.read(10000)  # 처음 10KB만 읽기

            # chardet을 사용한 인코딩 감지
            result = chardet.detect(raw_data)
            detected_encoding = result.get("encoding", "utf-8")
            confidence = result.get("confidence", 0)

            # 신뢰도가 낮으면 기본값 사용
            if confidence < 0.7:
                detected_encoding = "utf-8"

            # 지원되는 인코딩으로 정규화
            if detected_encoding.lower() in ["utf-8", "utf8"]:
                return "utf-8"
            elif detected_encoding.lower() in ["cp949", "euc-kr"]:
                return "cp949"
            elif detected_encoding.lower() in ["latin-1", "iso-8859-1"]:
                return "latin-1"
            elif detected_encoding.lower() in ["ascii"]:
                return "ascii"
            else:
                return "utf-8"  # 기본값

        except Exception:
            return "utf-8"  # 오류 시 기본값

    def detect_delimiter(self, file_path: str, encoding: str = "utf-8") -> str:
        """
        CSV 파일의 구분자를 자동으로 감지합니다.

        Args:
            file_path: 감지할 파일 경로
            encoding: 파일 인코딩

        Returns:
            str: 감지된 구분자
        """
        try:
            with open(file_path, "r", encoding=encoding) as f:
                # 첫 번째 행 읽기
                first_line = f.readline()

                # 각 구분자별로 컬럼 수 계산
                delimiter_counts = {}
                for delimiter in self.supported_delimiters:
                    count = first_line.count(delimiter)
                    if count > 0:
                        delimiter_counts[delimiter] = count

                # 가장 많은 컬럼을 만드는 구분자 선택
                if delimiter_counts:
                    return max(delimiter_counts, key=delimiter_counts.get)
                else:
                    return ","  # 기본값

        except Exception:
            return ","  # 오류 시 기본값

    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """
        파일의 기본 정보를 수집합니다.

        Args:
            file_path: 정보를 수집할 파일 경로

        Returns:
            Dict[str, Any]: 파일 정보 딕셔너리
        """
        try:
            file_stat = os.stat(file_path)
            detected_encoding = self.detect_encoding(file_path)
            detected_delimiter = self.detect_delimiter(file_path, detected_encoding)

            # 대략적인 행 수 추정
            estimated_rows = self._estimate_row_count(file_path, detected_encoding)

            return {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "file_size": file_stat.st_size,
                "created_time": datetime.fromtimestamp(file_stat.st_ctime),
                "modified_time": datetime.fromtimestamp(file_stat.st_mtime),
                "encoding": detected_encoding,
                "delimiter": detected_delimiter,
                "estimated_rows": estimated_rows,
                "is_readable": self.validate_file_readable(file_path),
            }

        except Exception as e:
            return {
                "file_path": file_path,
                "file_name": os.path.basename(file_path),
                "error": str(e),
                "is_readable": False,
            }

    def read_csv_streaming(
        self, file_path: str, config: FileInfo, chunk_size: int = 1000
    ) -> Iterator[pd.DataFrame]:
        """
        스트리밍 방식으로 CSV 파일을 읽습니다.

        Args:
            file_path: 읽을 CSV 파일 경로
            config: 파일 정보 설정
            chunk_size: 청크 크기

        Yields:
            pd.DataFrame: 데이터 청크
        """
        try:
            for chunk in pd.read_csv(
                file_path,
                encoding=config.encoding,
                delimiter=config.delimiter,
                header=0 if config.has_header else None,
                chunksize=chunk_size,
                dtype=str,  # 모든 데이터를 문자열로 읽어서 검증
                na_filter=False,  # 빈 값도 문자열로 처리
            ):
                yield chunk

        except Exception as e:
            raise Exception(f"CSV 파일 읽기 오류: {e}")

    def read_csv_full(self, file_path: str, config: FileInfo) -> pd.DataFrame:
        """
        전체 CSV 파일을 한 번에 읽습니다.

        Args:
            file_path: 읽을 CSV 파일 경로
            config: 파일 정보 설정

        Returns:
            pd.DataFrame: 전체 데이터
        """
        try:
            return pd.read_csv(
                file_path,
                encoding=config.encoding,
                delimiter=config.delimiter,
                header=0 if config.has_header else None,
                dtype=str,  # 모든 데이터를 문자열로 읽어서 검증
                na_filter=False,  # 빈 값도 문자열로 처리
            )

        except Exception as e:
            raise Exception(f"CSV 파일 읽기 오류: {e}")

    def get_csv_headers(self, file_path: str, config: FileInfo) -> List[str]:
        """
        CSV 파일의 헤더를 가져옵니다.

        Args:
            file_path: 헤더를 가져올 CSV 파일 경로
            config: 파일 정보 설정

        Returns:
            List[str]: 헤더 목록
        """
        try:
            with open(file_path, "r", encoding=config.encoding) as f:
                reader = csv.reader(f, delimiter=config.delimiter)
                if config.has_header:
                    header_row = next(reader)
                    return [col.strip() for col in header_row]
                else:
                    # 헤더가 없으면 첫 번째 행의 컬럼 수만큼 컬럼명 생성
                    first_row = next(reader)
                    return [f"column_{i+1}" for i in range(len(first_row))]

        except Exception as e:
            raise Exception(f"헤더 읽기 오류: {e}")

    def count_rows(self, file_path: str, config: FileInfo) -> int:
        """
        CSV 파일의 행 수를 정확히 계산합니다.

        Args:
            file_path: 행 수를 계산할 CSV 파일 경로
            config: 파일 정보 설정

        Returns:
            int: 행 수
        """
        try:
            with open(file_path, "r", encoding=config.encoding) as f:
                reader = csv.reader(f, delimiter=config.delimiter)
                return sum(1 for _ in reader)

        except Exception as e:
            raise Exception(f"행 수 계산 오류: {e}")

    def validate_csv_structure(
        self, file_path: str, config: FileInfo
    ) -> Tuple[bool, List[str]]:
        """
        CSV 파일의 기본 구조를 검증합니다.

        Args:
            file_path: 검증할 CSV 파일 경로
            config: 파일 정보 설정

        Returns:
            Tuple[bool, List[str]]: 검증 결과와 오류 메시지 목록
        """
        errors = []

        try:
            # 파일 존재 여부 확인
            if not self.validate_file_exists(file_path):
                errors.append(f"파일을 찾을 수 없습니다: {file_path}")
                return False, errors

            # 파일 읽기 권한 확인
            if not self.validate_file_readable(file_path):
                errors.append(f"파일 읽기 권한이 없습니다: {file_path}")
                return False, errors

            # 파일이 비어있는지 확인
            if os.path.getsize(file_path) == 0:
                errors.append("파일이 비어있습니다")
                return False, errors

            # CSV 구조 확인
            with open(file_path, "r", encoding=config.encoding) as f:
                reader = csv.reader(f, delimiter=config.delimiter)

                # 최소한 하나의 행이 있는지 확인
                try:
                    first_row = next(reader)
                    if not first_row:
                        errors.append("첫 번째 행이 비어있습니다")
                        return False, errors
                except StopIteration:
                    errors.append("파일이 비어있습니다")
                    return False, errors

                # 모든 행의 컬럼 수가 일치하는지 확인
                expected_columns = len(first_row)
                row_number = 2

                for row in reader:
                    if len(row) != expected_columns:
                        errors.append(
                            f"행 {row_number}: 컬럼 수가 일치하지 않습니다 (예상: {expected_columns}, 실제: {len(row)})"
                        )
                        return False, errors
                    row_number += 1

            return True, errors

        except UnicodeDecodeError as e:
            errors.append(f"인코딩 오류: {e}")
            return False, errors
        except Exception as e:
            errors.append(f"파일 구조 검증 오류: {e}")
            return False, errors

    def find_csv_files(self, directory_path: str, recursive: bool = True) -> List[str]:
        """
        디렉토리에서 CSV 파일을 찾습니다.

        Args:
            directory_path: 검색할 디렉토리 경로
            recursive: 하위 디렉토리까지 재귀적으로 검색할지 여부

        Returns:
            List[str]: 찾은 CSV 파일 경로 목록
        """
        csv_files = []
        directory = Path(directory_path)

        if not directory.exists() or not directory.is_dir():
            return csv_files

        try:
            if recursive:
                # 재귀적으로 검색
                pattern = "**/*.csv"
            else:
                # 현재 디렉토리만 검색
                pattern = "*.csv"

            for file_path in directory.glob(pattern):
                if file_path.is_file():
                    csv_files.append(str(file_path))

            # 파일명으로 정렬
            csv_files.sort()

        except Exception as e:
            print(f"CSV 파일 검색 오류: {e}")

        return csv_files

    def create_backup(self, file_path: str, backup_suffix: str = ".backup") -> str:
        """
        파일의 백업을 생성합니다.

        Args:
            file_path: 백업할 파일 경로
            backup_suffix: 백업 파일 접미사

        Returns:
            str: 백업 파일 경로
        """
        try:
            backup_path = file_path + backup_suffix
            import shutil

            shutil.copy2(file_path, backup_path)
            return backup_path

        except Exception as e:
            raise Exception(f"백업 생성 오류: {e}")

    def _estimate_row_count(self, file_path: str, encoding: str) -> int:
        """
        파일의 대략적인 행 수를 추정합니다.

        Args:
            file_path: 추정할 파일 경로
            encoding: 파일 인코딩

        Returns:
            int: 추정된 행 수
        """
        try:
            file_size = os.path.getsize(file_path)

            # 파일의 일부분을 읽어서 평균 행 길이 계산
            with open(file_path, "r", encoding=encoding) as f:
                sample_lines = []
                for i, line in enumerate(f):
                    if i >= 100:  # 처음 100행만 샘플링
                        break
                    sample_lines.append(line)

            if sample_lines:
                avg_line_length = sum(len(line) for line in sample_lines) / len(
                    sample_lines
                )
                estimated_rows = int(file_size / avg_line_length)
                return max(1, estimated_rows)  # 최소 1행
            else:
                return 1

        except Exception:
            return 1  # 오류 시 기본값

    def get_file_extension(self, file_path: str) -> str:
        """
        파일의 확장자를 가져옵니다.

        Args:
            file_path: 확장자를 가져올 파일 경로

        Returns:
            str: 파일 확장자 (소문자)
        """
        return Path(file_path).suffix.lower()

    def detect_file_type(self, file_path: str) -> FileType:
        """
        파일 확장자를 기반으로 파일 타입을 감지합니다.

        Args:
            file_path: 파일 경로

        Returns:
            FileType: 감지된 파일 타입
        """
        extension = self.get_file_extension(file_path)
        
        if extension == ".csv":
            return FileType.CSV
        elif extension == ".json":
            return FileType.JSON
        elif extension == ".jsonl":
            return FileType.JSONL
        else:
            raise ValueError(f"지원되지 않는 파일 확장자: {extension}")

    def is_supported_file(self, file_path: str) -> bool:
        """
        파일이 지원되는 형식인지 확인합니다.

        Args:
            file_path: 확인할 파일 경로

        Returns:
            bool: 지원되는 파일인지 여부
        """
        extension = self.get_file_extension(file_path)
        return extension in self.supported_extensions

    def is_csv_file(self, file_path: str) -> bool:
        """
        파일이 CSV 파일인지 확인합니다.

        Args:
            file_path: 확인할 파일 경로

        Returns:
            bool: CSV 파일인지 여부
        """
        return self.get_file_extension(file_path) == ".csv"

    def is_json_file(self, file_path: str) -> bool:
        """
        파일이 JSON 파일인지 확인합니다.

        Args:
            file_path: 확인할 파일 경로

        Returns:
            bool: JSON 파일인지 여부
        """
        return self.get_file_extension(file_path) == ".json"

    def is_jsonl_file(self, file_path: str) -> bool:
        """
        파일이 JSONL 파일인지 확인합니다.

        Args:
            file_path: 확인할 파일 경로

        Returns:
            bool: JSONL 파일인지 여부
        """
        return self.get_file_extension(file_path) == ".jsonl"

    def get_supported_encodings(self) -> List[str]:
        """
        지원되는 인코딩 목록을 반환합니다.

        Returns:
            List[str]: 지원되는 인코딩 목록
        """
        return self.supported_encodings.copy()

    def get_supported_delimiters(self) -> List[str]:
        """
        지원되는 구분자 목록을 반환합니다.

        Returns:
            List[str]: 지원되는 구분자 목록
        """
        return self.supported_delimiters.copy()

    def read_json_file(self, file_path: str, file_info: FileInfo) -> List[Dict[str, Any]]:
        """
        JSON 파일을 읽습니다.

        Args:
            file_path: 읽을 JSON 파일 경로
            file_info: 파일 정보 설정

        Returns:
            List[Dict[str, Any]]: 파싱된 JSON 데이터
        """
        return self.json_parser.parse_json_file(file_path, file_info)

    def read_jsonl_file(self, file_path: str, file_info: FileInfo) -> List[Dict[str, Any]]:
        """
        JSONL 파일을 읽습니다.

        Args:
            file_path: 읽을 JSONL 파일 경로
            file_info: 파일 정보 설정

        Returns:
            List[Dict[str, Any]]: 파싱된 JSONL 데이터
        """
        return self.json_parser.parse_jsonl_file(file_path, file_info)

    def read_file_by_type(self, file_path: str, file_info: FileInfo) -> List[Dict[str, Any]]:
        """
        파일 타입에 따라 적절한 방법으로 파일을 읽습니다.

        Args:
            file_path: 읽을 파일 경로
            file_info: 파일 정보 설정

        Returns:
            List[Dict[str, Any]]: 파싱된 데이터
        """
        file_type = self.detect_file_type(file_path)
        
        if file_type == FileType.CSV:
            # CSV 파일의 경우 DataFrame으로 읽은 후 딕셔너리 리스트로 변환
            df = self.read_csv_full(file_path, file_info)
            return df.to_dict('records')
        elif file_type == FileType.JSON:
            return self.read_json_file(file_path, file_info)
        elif file_type == FileType.JSONL:
            return self.read_jsonl_file(file_path, file_info)
        else:
            raise ValueError(f"지원되지 않는 파일 타입: {file_type}")

    def count_rows_by_type(self, file_path: str, file_info: FileInfo) -> int:
        """
        파일 타입에 따라 행 수를 계산합니다.

        Args:
            file_path: 행 수를 계산할 파일 경로
            file_info: 파일 정보 설정

        Returns:
            int: 행 수
        """
        file_type = self.detect_file_type(file_path)
        
        if file_type == FileType.CSV:
            return self.count_rows(file_path, file_info)
        elif file_type in [FileType.JSON, FileType.JSONL]:
            return self.json_parser.count_rows(file_path, file_info)
        else:
            raise ValueError(f"지원되지 않는 파일 타입: {file_type}")

    def find_supported_files(self, directory_path: str, recursive: bool = True) -> List[str]:
        """
        디렉토리에서 지원되는 모든 파일을 찾습니다.

        Args:
            directory_path: 검색할 디렉토리 경로
            recursive: 하위 디렉토리까지 재귀적으로 검색할지 여부

        Returns:
            List[str]: 찾은 파일 경로 목록
        """
        files = []
        directory = Path(directory_path)

        if not directory.exists() or not directory.is_dir():
            return files

        try:
            if recursive:
                # 재귀적으로 검색
                for extension in self.supported_extensions:
                    pattern = f"**/*{extension}"
                    for file_path in directory.glob(pattern):
                        if file_path.is_file():
                            files.append(str(file_path))
            else:
                # 현재 디렉토리만 검색
                for extension in self.supported_extensions:
                    pattern = f"*{extension}"
                    for file_path in directory.glob(pattern):
                        if file_path.is_file():
                            files.append(str(file_path))

            # 파일명으로 정렬
            files.sort()

        except Exception as e:
            print(f"파일 검색 오류: {e}")

        return files

    def find_csv_files(self, directory_path: str, recursive: bool = True) -> List[str]:
        """
        디렉토리에서 CSV 파일을 찾습니다.

        Args:
            directory_path: 검색할 디렉토리 경로
            recursive: 하위 디렉토리까지 재귀적으로 검색할지 여부

        Returns:
            List[str]: 찾은 CSV 파일 경로 목록
        """
        all_files = self.find_supported_files(directory_path, recursive)
        return [f for f in all_files if self.is_csv_file(f)]

    def find_json_files(self, directory_path: str, recursive: bool = True) -> List[str]:
        """
        디렉토리에서 JSON 파일을 찾습니다.

        Args:
            directory_path: 검색할 디렉토리 경로
            recursive: 하위 디렉토리까지 재귀적으로 검색할지 여부

        Returns:
            List[str]: 찾은 JSON 파일 경로 목록
        """
        all_files = self.find_supported_files(directory_path, recursive)
        return [f for f in all_files if self.is_json_file(f)]

    def find_jsonl_files(self, directory_path: str, recursive: bool = True) -> List[str]:
        """
        디렉토리에서 JSONL 파일을 찾습니다.

        Args:
            directory_path: 검색할 디렉토리 경로
            recursive: 하위 디렉토리까지 재귀적으로 검색할지 여부

        Returns:
            List[str]: 찾은 JSONL 파일 경로 목록
        """
        all_files = self.find_supported_files(directory_path, recursive)
        return [f for f in all_files if self.is_jsonl_file(f)]
