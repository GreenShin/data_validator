"""
Command-line interface for CSV validation.

이 모듈은 사용자 친화적인 명령행 인터페이스를 제공합니다.
"""

import os
import sys
from pathlib import Path
from typing import Optional

import click

from ..core.validator import DataValidator
from ..utils.logger import Logger


@click.group()
@click.version_option(version="0.2.0", prog_name="Data Validator")
def cli():
    """
    데이터 파일 구문정확성 검증 프로그램

    CSV, JSON, JSONL 파일의 구조정확성과 형식정확성을 검증하고 상세한 결과 리포트를 생성합니다.
    """
    pass


@cli.command()
@click.option(
    "--config",
    "-c",
    required=True,
    type=click.Path(exists=True, readable=True),
    help="YAML 설정 파일 경로",
)
@click.option(
    "--input",
    "-i",
    required=True,
    type=click.Path(exists=True),
    help="검증할 파일 또는 폴더 경로 (CSV, JSON, JSONL 지원)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="결과 파일 저장 경로 (기본값: 입력 경로와 동일)",
)
@click.option("--verbose", "-v", is_flag=True, help="상세 로그 출력")
@click.option("--log-file", type=click.Path(), help="로그 파일 경로")
@click.option(
    "--format",
    type=click.Choice(["markdown", "html", "json", "all"], case_sensitive=False),
    default="all",
    help="결과 리포트 형식 (기본값: all)",
)
@click.option(
    "--analyze",
    is_flag=True,
    help="컬럼 분포 분석을 수행합니다 (설정 파일에 distribution_analysis 섹션이 필요)",
)
def validate(config, input, output, verbose, log_file, format, analyze):
    """
    데이터 파일의 구문정확성을 검증합니다 (CSV, JSON, JSONL 지원).

    예시:
        data-validator validate -c config.yml -i data.csv
        data-validator validate -c config.yml -i data.json
        data-validator validate -c config.yml -i data.jsonl
        data-validator validate -c config.yml -i /path/to/files -o /path/to/results
    """
    try:
        # 입력 경로 확인
        input_path = Path(input)
        if not input_path.exists():
            click.echo(f"❌ 입력 경로를 찾을 수 없습니다: {input}", err=True)
            sys.exit(1)

        # 출력 경로 설정
        if output is None:
            if input_path.is_file():
                output = input_path.parent
            else:
                output = input_path
        else:
            output = Path(output)
            output.mkdir(parents=True, exist_ok=True)

        # Data Validator 초기화
        validator = DataValidator(config_path=config, verbose=verbose, log_file=log_file)
        
        # 분포 분석 옵션 처리
        if analyze:
            if verbose:
                click.echo("📊 분포 분석 모드가 활성화되었습니다.")
            validator.enable_distribution_analysis()

        # 검증 실행
        if input_path.is_file():
            # 단일 파일 검증
            supported_extensions = {".csv", ".json", ".jsonl"}
            if input_path.suffix.lower() not in supported_extensions:
                click.echo(f"❌ 지원되지 않는 파일 형식입니다: {input_path}", err=True)
                click.echo(f"지원되는 형식: {', '.join(supported_extensions)}", err=True)
                sys.exit(1)

            result = validator.validate_file(str(input_path))

            # 결과 저장
            _save_single_result(result, output, format, validator)

        elif input_path.is_dir():
            # 폴더 내 모든 지원되는 파일 검증
            results = validator.validate_folder(str(input_path), str(output))

            if not results:
                click.echo("⚠️ 검증할 파일을 찾을 수 없습니다.", err=True)
                sys.exit(1)

            # 전체 결과 요약
            _print_summary(results)

        else:
            click.echo(f"❌ 잘못된 입력 경로입니다: {input_path}", err=True)
            sys.exit(1)

        # 리소스 정리
        validator.close()

        click.echo("✅ 검증이 완료되었습니다.")

    except Exception as e:
        click.echo(f"❌ 오류가 발생했습니다: {e}", err=True)
        if verbose:
            import traceback

            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    default="sample_config.yml",
    help="생성할 샘플 설정 파일 경로 (기본값: sample_config.yml)",
)
@click.option(
    "--type",
    "-t",
    type=click.Choice(["csv", "json", "jsonl"], case_sensitive=False),
    default="csv",
    help="생성할 샘플 설정 파일 타입 (기본값: csv)",
)
@click.option("--verbose", "-v", is_flag=True, help="상세 로그 출력")
def init(output, type, verbose):
    """
    샘플 설정 파일을 생성합니다.

    예시:
        data-validator init
        data-validator init -t json -o json_config.yml
        data-validator init -t jsonl -o jsonl_config.yml
    """
    try:
        # 더미 설정 파일로 ConfigManager 초기화
        from ..core.config import ConfigManager

        config_manager = ConfigManager()

        # 파일 타입에 따라 샘플 설정 파일 생성
        if type == "csv":
            config_manager.create_sample_config(output)
        elif type == "json":
            config_manager.create_json_sample_config(output)
        elif type == "jsonl":
            config_manager.create_jsonl_sample_config(output)

        if verbose:
            click.echo(f"✅ 샘플 설정 파일이 생성되었습니다: {output}")
        else:
            click.echo(f"✅ 샘플 설정 파일 생성 완료: {output}")

        # 사용법 안내
        click.echo("\n📝 다음 단계:")
        click.echo(f"1. {output} 파일을 편집하여 검증 규칙을 설정하세요")
        click.echo(
            "2. data-validator validate -c <설정파일> -i <파일> 명령으로 검증을 실행하세요"
        )

    except Exception as e:
        click.echo(f"❌ 샘플 설정 파일 생성 중 오류가 발생했습니다: {e}", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--config",
    "-c",
    required=True,
    type=click.Path(exists=True, readable=True),
    help="검증할 YAML 설정 파일 경로",
)
@click.option("--verbose", "-v", is_flag=True, help="상세 로그 출력")
def check_config(config, verbose):
    """
    설정 파일의 유효성을 검사합니다.

    예시:
        csv-validator check-config -c config.yml
    """
    try:
        # Data Validator 초기화
        validator = DataValidator(config_path=config, verbose=verbose)

        # 설정 검증
        is_valid = validator.validate_config()

        if is_valid:
            click.echo("✅ 설정 파일이 유효합니다.")

            # 설정 요약 출력
            summary = validator.get_config_summary()
            click.echo("\n📋 설정 요약:")
            for key, value in summary.items():
                if isinstance(value, dict):
                    click.echo(f"  {key}:")
                    for sub_key, sub_value in value.items():
                        click.echo(f"    {sub_key}: {sub_value}")
                else:
                    click.echo(f"  {key}: {value}")
        else:
            click.echo("❌ 설정 파일에 오류가 있습니다.", err=True)
            sys.exit(1)

        # 리소스 정리
        validator.close()

    except Exception as e:
        click.echo(f"❌ 설정 파일 검사 중 오류가 발생했습니다: {e}", err=True)
        if verbose:
            import traceback

            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--input",
    "-i",
    required=True,
    type=click.Path(exists=True),
    help="분석할 파일 경로 (CSV, JSON, JSONL 지원)",
)
@click.option(
    "--output",
    "-o",
    type=click.Path(),
    help="분석 결과 저장 경로 (기본값: 입력 파일과 동일한 디렉토리)",
)
@click.option("--verbose", "-v", is_flag=True, help="상세 로그 출력")
def analyze(input, output, verbose):
    """
    데이터 파일을 분석하여 자동으로 설정 파일을 생성합니다 (CSV, JSON, JSONL 지원).

    예시:
        data-validator analyze -i data.csv
        data-validator analyze -i data.json
        data-validator analyze -i data.jsonl
        data-validator analyze -i data.csv -o auto_config.yml
    """
    try:
        input_path = Path(input)
        supported_extensions = {".csv", ".json", ".jsonl"}
        if not input_path.is_file() or input_path.suffix.lower() not in supported_extensions:
            click.echo(f"❌ 지원되지 않는 파일 형식입니다: {input_path}", err=True)
            click.echo(f"지원되는 형식: {', '.join(supported_extensions)}", err=True)
            sys.exit(1)

        # 출력 경로 설정
        if output is None:
            output = input_path.parent / f"{input_path.stem}_auto_config.yml"
        else:
            output = Path(output)

        # 파일 분석
        from ..utils.file_handler import FileHandler

        file_handler = FileHandler()

        # 파일 정보 수집
        file_info = file_handler.get_file_info(str(input_path))
        detected_encoding = file_info.get("encoding", "utf-8")
        file_type = file_handler.detect_file_type(str(input_path))

        # 파일 타입에 따라 데이터 읽기
        if file_type.value == "csv":
            detected_delimiter = file_info.get("delimiter", ",")
            # CSV 파일 읽기
            import pandas as pd
            df = pd.read_csv(
                str(input_path),
                encoding=detected_encoding,
                delimiter=detected_delimiter,
                nrows=1000,  # 처음 1000행만 분석
            )
            auto_config = _generate_auto_config(df, file_info, file_type)
        else:
            # JSON/JSONL 파일 읽기
            from ..models import FileInfo as FileInfoModel
            from ..models import FileType as FileTypeModel
            
            file_info_model = FileInfoModel(
                file_type=FileTypeModel(file_type.value),
                encoding=detected_encoding
            )
            
            data = file_handler.read_file_by_type(str(input_path), file_info_model)
            
            # JSON 데이터를 DataFrame으로 변환
            import pandas as pd
            if data:
                # 중첩된 객체를 평면화
                flattened_data = []
                for item in data:
                    flattened_item = file_handler.json_parser._flatten_dict(item)
                    flattened_data.append(flattened_item)
                df = pd.DataFrame(flattened_data)
            else:
                df = pd.DataFrame()
            
            auto_config = _generate_auto_config(df, file_info, file_type)

        # 설정 파일 저장
        import yaml

        with open(output, "w", encoding="utf-8") as f:
            yaml.dump(
                auto_config,
                f,
                default_flow_style=False,
                allow_unicode=True,
                sort_keys=False,
            )

        click.echo(f"✅ 자동 설정 파일이 생성되었습니다: {output}")
        click.echo("\n📝 다음 단계:")
        click.echo("1. 생성된 설정 파일을 검토하고 필요에 따라 수정하세요")
        click.echo(
            "2. data-validator validate -c <설정파일> -i <파일> 명령으로 검증을 실행하세요"
        )

        if verbose:
            click.echo(f"\n📊 분석 결과:")
            click.echo(f"  - 파일 타입: {file_type.value}")
            click.echo(f"  - 인코딩: {detected_encoding}")
            if file_type.value == "csv":
                click.echo(f"  - 구분자: {detected_delimiter}")
            click.echo(f"  - 컬럼 수: {len(df.columns)}")
            click.echo(f"  - 분석된 행 수: {len(df)}")

    except Exception as e:
        click.echo(f"❌ 파일 분석 중 오류가 발생했습니다: {e}", err=True)
        if verbose:
            import traceback

            click.echo(traceback.format_exc(), err=True)
        sys.exit(1)


def _save_single_result(result, output_dir, format, validator):
    """단일 파일 검증 결과를 저장합니다."""
    try:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # 파일명 생성
        timestamp = result.timestamp.strftime("%Y%m%d_%H%M%S")
        base_name = Path(result.file_name).stem
        output_file = output_path / f"{base_name}_{timestamp}"

        # 지정된 형식으로 결과 저장
        if format == "all":
            formats = ["markdown", "html", "json"]
        else:
            formats = [format]

        saved_files = []
        for fmt in formats:
            if fmt == "markdown":
                report = validator.formatter.generate_markdown_report(result)
                file_path = validator.formatter.save_report(
                    report, str(output_file), "markdown"
                )
            elif fmt == "html":
                report = validator.formatter.generate_html_report(result)
                file_path = validator.formatter.save_report(
                    report, str(output_file), "html"
                )
            elif fmt == "json":
                report = validator.formatter.generate_json_report(result)
                file_path = validator.formatter.save_report(
                    report, str(output_file), "json"
                )

            saved_files.append(file_path)

        # 저장된 파일 정보 출력
        click.echo(f"\n📄 결과 파일이 저장되었습니다:")
        for file_path in saved_files:
            click.echo(f"  - {file_path}")

    except Exception as e:
        click.echo(f"❌ 결과 파일 저장 중 오류가 발생했습니다: {e}", err=True)


def _print_summary(results):
    """검증 결과 요약을 출력합니다."""
    if not results:
        return

    total_files = len(results)
    total_rows = sum(result.total_rows for result in results)
    total_errors = sum(len(result.errors) for result in results)
    total_time = sum(result.processing_time for result in results)

    successful_files = sum(
        1 for result in results if result.structural_valid and result.format_valid
    )
    failed_files = total_files - successful_files

    click.echo(f"\n📊 검증 결과 요약:")
    click.echo(f"  총 파일 수: {total_files}")
    click.echo(f"  성공한 파일: {successful_files}")
    click.echo(f"  실패한 파일: {failed_files}")
    click.echo(f"  총 행 수: {total_rows:,}")
    click.echo(f"  총 오류 수: {total_errors}")
    click.echo(f"  총 처리 시간: {total_time:.2f}초")

    if total_time > 0:
        click.echo(f"  평균 처리 속도: {total_rows/total_time:.0f} 행/초")


def _generate_auto_config(df, file_info, file_type):
    """파일 분석을 바탕으로 자동 설정을 생성합니다."""
    import pandas as pd
    from datetime import datetime

    # 파일 정보 설정
    config = {
        "file_info": {
            "file_type": file_type.value,
            "expected_rows": None,  # 자동으로 설정하지 않음
            "encoding": file_info.get("encoding", "utf-8"),
            "delimiter": file_info.get("delimiter", ","),
            "has_header": True,
        },
        "columns": [],
    }
    
    # JSON/JSONL 전용 설정 추가
    if file_type.value in ["json", "jsonl"]:
        config["file_info"]["json_schema"] = None
        config["file_info"]["json_root_path"] = None
        config["file_info"]["jsonl_array_mode"] = False

    # 각 컬럼 분석
    for column in df.columns:
        column_data = df[column].dropna()

        # 데이터 타입 추론
        data_type = _infer_data_type(column_data)

        # 컬럼 규칙 생성
        column_rule = {
            "name": column,
            "type": data_type,
            "required": True,  # 기본적으로 필수로 설정
        }

        # 데이터 타입별 추가 규칙 설정
        if data_type == "integer":
            if not column_data.empty:
                try:
                    numeric_data = pd.to_numeric(column_data, errors="coerce").dropna()
                    if not numeric_data.empty:
                        column_rule["range"] = {
                            "min": int(numeric_data.min()),
                            "max": int(numeric_data.max()),
                        }
                except:
                    pass

        elif data_type == "float":
            if not column_data.empty:
                try:
                    numeric_data = pd.to_numeric(column_data, errors="coerce").dropna()
                    if not numeric_data.empty:
                        column_rule["range"] = {
                            "min": float(numeric_data.min()),
                            "max": float(numeric_data.max()),
                        }
                except:
                    pass

        elif data_type == "string":
            if not column_data.empty:
                lengths = column_data.astype(str).str.len()
                column_rule["length"] = {
                    "min": int(lengths.min()),
                    "max": int(lengths.max()),
                }

                # 범주형 데이터인지 확인 (고유값이 적은 경우)
                unique_values = column_data.nunique()
                if unique_values <= 10 and unique_values > 1:
                    column_rule["allowed_values"] = column_data.unique().tolist()
                    column_rule["case_sensitive"] = False

        elif data_type == "datetime":
            # 일반적인 날짜 형식 시도
            column_rule["format"] = "%Y-%m-%d %H:%M:%S"

        elif data_type == "email":
            # 이메일 형식은 특별한 설정 불필요
            pass

        config["columns"].append(column_rule)

    return config


def _infer_data_type(series):
    """시리즈 데이터를 분석하여 데이터 타입을 추론합니다."""
    import pandas as pd
    import re

    # 빈 데이터 처리
    if series.empty:
        return "string"

    # 이메일 형식 확인
    email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    if series.astype(str).str.match(email_pattern).any():
        return "email"

    # 날짜 형식 확인
    try:
        # 경고 메시지를 억제하고 날짜 변환 시도
        import warnings

        with warnings.catch_warnings():
            warnings.simplefilter("ignore")
            pd.to_datetime(series, errors="raise")
        return "datetime"
    except:
        pass

    # 숫자 형식 확인
    try:
        numeric_series = pd.to_numeric(series, errors="coerce")
        if not numeric_series.isna().all():
            # 정수인지 확인
            if numeric_series.dropna().apply(lambda x: x.is_integer()).all():
                return "integer"
            else:
                return "float"
    except:
        pass

    # 불린 형식 확인
    bool_values = ["true", "false", "1", "0", "yes", "no", "y", "n"]
    if series.astype(str).str.lower().isin(bool_values).all():
        return "boolean"

    # 기본값은 문자열
    return "string"


if __name__ == "__main__":
    cli()
