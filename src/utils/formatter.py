"""
Result formatting utilities for CSV validation.

이 모듈은 검증 결과를 사용자 친화적인 형태로 포맷팅하는 기능을 제공합니다.
"""

import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path

from ..models import ValidationResult, ValidationError, ErrorType


class ReportFormatter:
    """검증 결과를 포맷팅하는 클래스"""

    def __init__(self):
        """ReportFormatter 초기화"""
        self.timestamp = datetime.now()

    def generate_markdown_report(self, result: ValidationResult) -> str:
        """
        Markdown 형식의 검증 결과 리포트를 생성합니다.

        Args:
            result: 검증 결과 객체

        Returns:
            str: Markdown 형식의 리포트
        """
        try:
            # 기본 정보
            file_info = self._format_file_info(result)
            summary = self._format_summary(result)
            structural_details = self._format_structural_details(result)
            format_details = self._format_format_details(result)
            error_table = self._format_error_table(result.errors)
            statistics = self._format_statistics(result)
            recommendations = self._format_recommendations(result)
            distribution_analysis = self._format_distribution_analysis(result)

            # 전체 리포트 조합
            report = f"""# 📊 CSV 구문정확성 검증 결과

{file_info}

{summary}

## 📋 상세 결과

{structural_details}

{format_details}

{error_table}

{statistics}

{distribution_analysis}

{recommendations}

---
*리포트 생성 시간: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}*
*CSV Validator v0.1.0*"""

            return report

        except Exception as e:
            return f"# 오류 발생\n\n리포트 생성 중 오류가 발생했습니다: {e}"

    def generate_html_report(self, result: ValidationResult) -> str:
        """
        HTML 형식의 검증 결과 리포트를 생성합니다.

        Args:
            result: 검증 결과 객체

        Returns:
            str: HTML 형식의 리포트
        """
        try:
            # CSS 스타일
            css_style = """
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; margin: 40px; line-height: 1.6; }
                .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; border-radius: 10px; margin-bottom: 30px; }
                .summary { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin: 20px 0; }
                .summary-card { background: #f8f9fa; padding: 20px; border-radius: 8px; border-left: 4px solid #007bff; }
                .success { border-left-color: #28a745; }
                .error { border-left-color: #dc3545; }
                .warning { border-left-color: #ffc107; }
                table { width: 100%; border-collapse: collapse; margin: 20px 0; }
                th, td { padding: 12px; text-align: left; border-bottom: 1px solid #ddd; }
                th { background-color: #f8f9fa; font-weight: 600; }
                .error-row { background-color: #fff5f5; }
                .stats-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; margin: 20px 0; }
                .recommendations { background: #e3f2fd; padding: 20px; border-radius: 8px; border-left: 4px solid #2196f3; }
                .emoji { font-size: 1.2em; }
            </style>
            """

            # HTML 구조
            html = f"""
            <!DOCTYPE html>
            <html lang="ko">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>CSV 검증 결과 - {result.file_name}</title>
                {css_style}
            </head>
            <body>
                <div class="header">
                    <h1><span class="emoji">📊</span> CSV 구문정확성 검증 결과</h1>
                    <p>파일: {result.file_name} | 검증 일시: {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div class="summary">
                    <div class="summary-card {'success' if result.structural_valid else 'error'}">
                        <h3><span class="emoji">🔍</span> 구조정확성</h3>
                        <p>{'✅ 통과' if result.structural_valid else '❌ 실패'}</p>
                    </div>
                    <div class="summary-card {'success' if result.format_valid else 'error'}">
                        <h3><span class="emoji">📝</span> 형식정확성</h3>
                        <p>{'✅ 통과' if result.format_valid else '❌ 실패'}</p>
                    </div>
                    <div class="summary-card {'success' if result.structural_valid and result.format_valid else 'error'}">
                        <h3><span class="emoji">📈</span> 전체 결과</h3>
                        <p>{'✅ 통과' if result.structural_valid and result.format_valid else '❌ 실패'}</p>
                    </div>
                    <div class="summary-card warning">
                        <h3><span class="emoji">⚠️</span> 오류 수</h3>
                        <p>{len(result.errors)}개</p>
                    </div>
                </div>
                
                <h2><span class="emoji">📁</span> 파일 정보</h2>
                <table>
                    <tr><th>항목</th><th>값</th></tr>
                    <tr><td>파일명</td><td>{result.file_name}</td></tr>
                    <tr><td>검증 일시</td><td>{result.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</td></tr>
                    <tr><td>총 행 수</td><td>{result.total_rows:,}</td></tr>
                    <tr><td>총 컬럼 수</td><td>{result.total_columns}</td></tr>
                    <tr><td>처리 시간</td><td>{result.processing_time:.2f}초</td></tr>
                </table>
                
                <h2><span class="emoji">❌</span> 오류 상세 정보</h2>
                {self._format_error_table_html(result.errors)}
                
                <div class="stats-grid">
                    <div>
                        <h3><span class="emoji">📊</span> 오류 유형별 통계</h3>
                        {self._format_error_type_stats_html(result.errors)}
                    </div>
                    <div>
                        <h3><span class="emoji">📋</span> 컬럼별 오류 통계</h3>
                        {self._format_column_stats_html(result.errors)}
                    </div>
                </div>
                
                {self._format_distribution_analysis_html(result)}
                
                <div class="recommendations">
                    <h3><span class="emoji">💡</span> 권장사항</h3>
                    {self._format_recommendations_html(result)}
                </div>
                
                <footer style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #ddd; color: #666; text-align: center;">
                    <p>리포트 생성 시간: {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')} | CSV Validator v0.1.0</p>
                </footer>
            </body>
            </html>
            """

            return html

        except Exception as e:
            return f"<html><body><h1>오류 발생</h1><p>리포트 생성 중 오류가 발생했습니다: {e}</p></body></html>"

    def generate_json_report(self, result: ValidationResult) -> str:
        """
        JSON 형식의 검증 결과 리포트를 생성합니다.

        Args:
            result: 검증 결과 객체

        Returns:
            str: JSON 형식의 리포트
        """
        try:
            # ValidationResult를 딕셔너리로 변환
            result_dict = {
                "file_name": result.file_name,
                "timestamp": result.timestamp.isoformat(),
                "total_rows": result.total_rows,
                "total_columns": result.total_columns,
                "structural_valid": result.structural_valid,
                "format_valid": result.format_valid,
                "processing_time": result.processing_time,
                "errors": [
                    {
                        "row_number": error.row_number,
                        "column_name": error.column_name,
                        "error_type": error.error_type,
                        "actual_value": str(error.actual_value),
                        "expected_value": str(error.expected_value),
                        "message": error.message,
                    }
                    for error in result.errors
                ],
                "statistics": self._generate_statistics_dict(result),
                "summary": {
                    "total_errors": len(result.errors),
                    "success_rate": self._calculate_success_rate(result),
                    "overall_valid": result.structural_valid and result.format_valid,
                },
            }
            
            # 분포 분석 결과가 있으면 추가
            if result.distribution_analysis:
                # Pydantic 모델을 딕셔너리로 변환
                distribution_dict = {}
                for column_name, analysis_result in result.distribution_analysis.items():
                    if hasattr(analysis_result, 'dict'):
                        distribution_dict[column_name] = analysis_result.dict()
                    elif hasattr(analysis_result, 'model_dump'):
                        distribution_dict[column_name] = analysis_result.model_dump()
                    else:
                        distribution_dict[column_name] = str(analysis_result)
                result_dict["distribution_analysis"] = distribution_dict

            return json.dumps(result_dict, ensure_ascii=False, indent=2)

        except Exception as e:
            return json.dumps(
                {"error": f"리포트 생성 중 오류가 발생했습니다: {e}"},
                ensure_ascii=False,
                indent=2,
            )

    def save_report(
        self, report_content: str, output_path: str, format_type: str = "markdown"
    ) -> str:
        """
        리포트를 파일로 저장합니다.

        Args:
            report_content: 저장할 리포트 내용
            output_path: 출력 파일 경로
            format_type: 리포트 형식 (markdown, html, json)

        Returns:
            str: 저장된 파일 경로
        """
        try:
            # 출력 디렉토리 생성
            output_dir = Path(output_path).parent
            output_dir.mkdir(parents=True, exist_ok=True)

            # 파일 확장자 설정
            if format_type.lower() == "html":
                if not output_path.endswith(".html"):
                    output_path += ".html"
            elif format_type.lower() == "json":
                if not output_path.endswith(".json"):
                    output_path += ".json"
            else:  # markdown
                if not output_path.endswith(".md"):
                    output_path += ".md"

            # 파일 저장
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(report_content)

            return output_path

        except Exception as e:
            raise Exception(f"리포트 저장 오류: {e}")

    def _format_file_info(self, result: ValidationResult) -> str:
        """파일 정보를 포맷팅합니다."""
        return f"""## 📁 파일 정보

| 항목 | 값 |
|------|-----|
| 파일명 | {result.file_name} |
| 검증 일시 | {result.timestamp.strftime('%Y-%m-%d %H:%M:%S')} |
| 총 행 수 | {result.total_rows:,} |
| 총 컬럼 수 | {result.total_columns} |
| 처리 시간 | {result.processing_time:.2f}초 |"""

    def _format_summary(self, result: ValidationResult) -> str:
        """검증 요약을 포맷팅합니다."""
        success_rate = self._calculate_success_rate(result)

        return f"""## ✅ 검증 요약

- **구조정확성**: {'✅ 통과' if result.structural_valid else '❌ 실패'}
- **형식정확성**: {'✅ 통과' if result.format_valid else '❌ 실패'}
- **전체 결과**: {'✅ 통과' if result.structural_valid and result.format_valid else '❌ 실패'}
- **총 오류 수**: {len(result.errors)}개
- **성공률**: {success_rate:.1f}%"""

    def _format_structural_details(self, result: ValidationResult) -> str:
        """구조정확성 검증 상세를 포맷팅합니다."""
        return f"""### 🔍 구조정확성 검증

- [{'✅' if result.structural_valid else '❌'}] CSV 포맷 규칙 준수
- [{'✅' if result.structural_valid else '❌'}] 인코딩 형식 확인
- [{'✅' if result.structural_valid else '❌'}] 구분자 일관성 확인
- [{'✅' if result.structural_valid else '❌'}] 행 수 일치 확인
- [{'✅' if result.structural_valid else '❌'}] 컬럼 구조 일관성 확인"""

    def _format_format_details(self, result: ValidationResult) -> str:
        """형식정확성 검증 상세를 포맷팅합니다."""
        if result.format_valid:
            return f"""### 📝 형식정확성 검증

- [✅] 형식정확성 검증 통과"""
        else:
            error_summary = self._get_error_summary(result.errors)
            return f"""### 📝 형식정확성 검증

- [❌] 형식정확성 검증 실패
  {error_summary}"""

    def _format_error_table(self, errors: List[ValidationError]) -> str:
        """오류 테이블을 포맷팅합니다."""
        if not errors:
            return "## ✅ 오류 없음\n\n모든 검증을 통과했습니다!"

        table_rows = []
        for error in errors:
            table_rows.append(
                f"| {error.row_number} | {error.column_name} | {error.error_type} | {error.actual_value} | {error.expected_value} | {error.message} |"
            )

        return f"""## ❌ 오류 상세 정보

| 행 번호 | 컬럼명 | 오류 유형 | 실제 값 | 예상 값/범위 | 메시지 |
|---------|--------|-----------|---------|--------------|--------|
{chr(10).join(table_rows)}"""

    def _format_error_table_html(self, errors: List[ValidationError]) -> str:
        """HTML 형식의 오류 테이블을 포맷팅합니다."""
        if not errors:
            return "<p>모든 검증을 통과했습니다!</p>"

        table_rows = []
        for error in errors:
            table_rows.append(
                f"""
                <tr class="error-row">
                    <td>{error.row_number}</td>
                    <td>{error.column_name}</td>
                    <td>{error.error_type}</td>
                    <td>{error.actual_value}</td>
                    <td>{error.expected_value}</td>
                    <td>{error.message}</td>
                </tr>
            """
            )

        return f"""
        <table>
            <thead>
                <tr>
                    <th>행 번호</th>
                    <th>컬럼명</th>
                    <th>오류 유형</th>
                    <th>실제 값</th>
                    <th>예상 값/범위</th>
                    <th>메시지</th>
                </tr>
            </thead>
            <tbody>
                {''.join(table_rows)}
            </tbody>
        </table>
        """

    def _format_statistics(self, result: ValidationResult) -> str:
        """통계 정보를 포맷팅합니다."""
        error_type_stats = self._get_error_type_stats(result.errors)
        column_stats = self._get_column_stats(result.errors)

        return f"""## 📈 통계 정보

### 오류 유형별 통계

| 오류 유형 | 개수 | 비율 |
|-----------|------|------|
{chr(10).join([f"| {error_type} | {count} | {ratio:.1f}% |" for error_type, count, ratio in error_type_stats])}

### 컬럼별 오류 통계

| 컬럼명 | 오류 개수 | 비율 |
|--------|-----------|------|
{chr(10).join([f"| {column} | {count} | {ratio:.1f}% |" for column, count, ratio in column_stats])}

### 행별 오류 통계

| 행 번호 | 오류 개수 |
|---------|-----------|
{chr(10).join([f"| {row} | {count} |" for row, count in self._get_row_stats(result.errors)])}"""

    def _format_error_type_stats_html(self, errors: List[ValidationError]) -> str:
        """HTML 형식의 오류 유형별 통계를 포맷팅합니다."""
        stats = self._get_error_type_stats(errors)
        rows = [
            f"<tr><td>{error_type}</td><td>{count}</td><td>{ratio:.1f}%</td></tr>"
            for error_type, count, ratio in stats
        ]
        return f"<table><tr><th>오류 유형</th><th>개수</th><th>비율</th></tr>{''.join(rows)}</table>"

    def _format_column_stats_html(self, errors: List[ValidationError]) -> str:
        """HTML 형식의 컬럼별 통계를 포맷팅합니다."""
        stats = self._get_column_stats(errors)
        rows = [
            f"<tr><td>{column}</td><td>{count}</td><td>{ratio:.1f}%</td></tr>"
            for column, count, ratio in stats
        ]
        return f"<table><tr><th>컬럼명</th><th>오류 개수</th><th>비율</th></tr>{''.join(rows)}</table>"

    def _format_recommendations(self, result: ValidationResult) -> str:
        """권장사항을 포맷팅합니다."""
        if not result.errors:
            return "## 🎉 완벽한 데이터\n\n모든 검증을 통과했습니다. 데이터 품질이 우수합니다!"

        total_errors = len(result.errors)
        error_types = set(error.error_type for error in result.errors)

        recommendations = []

        if total_errors > 0:
            recommendations.append(f"⚠️ **데이터 품질 개선이 필요합니다.**")
            recommendations.append("- 데이터 형식을 표준화하세요.")
            recommendations.append("- 필수 필드의 누락을 방지하세요.")
            recommendations.append("- 데이터 범위와 형식을 검토하세요.")
            recommendations.append(f"- 총 {total_errors}개의 오류를 수정하세요.")
            recommendations.append("- 오류가 많은 컬럼부터 우선적으로 검토하세요.")

        if len(error_types) > 1:
            recommendations.append(
                f"- {len(error_types)}가지 유형의 오류가 발견되었습니다. 각 유형별로 대응 방안을 수립하세요."
            )

        return f"""## 💡 권장사항

{chr(10).join(recommendations)}"""

    def _format_recommendations_html(self, result: ValidationResult) -> str:
        """HTML 형식의 권장사항을 포맷팅합니다."""
        if not result.errors:
            return "<p>모든 검증을 통과했습니다. 데이터 품질이 우수합니다!</p>"

        total_errors = len(result.errors)
        error_types = set(error.error_type for error in result.errors)

        recommendations = []

        if total_errors > 0:
            recommendations.append(
                f"<p><strong>데이터 품질 개선이 필요합니다.</strong></p>"
            )
            recommendations.append("<ul>")
            recommendations.append("<li>데이터 형식을 표준화하세요.</li>")
            recommendations.append("<li>필수 필드의 누락을 방지하세요.</li>")
            recommendations.append("<li>데이터 범위와 형식을 검토하세요.</li>")
            recommendations.append(f"<li>총 {total_errors}개의 오류를 수정하세요.</li>")
            recommendations.append(
                "<li>오류가 많은 컬럼부터 우선적으로 검토하세요.</li>"
            )
            recommendations.append("</ul>")

        if len(error_types) > 1:
            recommendations.append(
                f"<p>{len(error_types)}가지 유형의 오류가 발견되었습니다. 각 유형별로 대응 방안을 수립하세요.</p>"
            )

        return "".join(recommendations)

    def _get_error_summary(self, errors: List[ValidationError]) -> str:
        """오류 요약을 생성합니다."""
        error_counts = {}
        for error in errors:
            error_counts[error.error_type] = error_counts.get(error.error_type, 0) + 1

        summary_lines = []
        for error_type, count in error_counts.items():
            summary_lines.append(f"  - {error_type}: {count}개")

        return "\n".join(summary_lines)

    def _get_error_type_stats(self, errors: List[ValidationError]) -> List[tuple]:
        """오류 유형별 통계를 생성합니다."""
        error_counts = {}
        for error in errors:
            error_counts[error.error_type] = error_counts.get(error.error_type, 0) + 1

        total_errors = len(errors)
        stats = []
        for error_type, count in error_counts.items():
            ratio = (count / total_errors * 100) if total_errors > 0 else 0
            stats.append((error_type, count, ratio))

        return sorted(stats, key=lambda x: x[1], reverse=True)

    def _get_column_stats(self, errors: List[ValidationError]) -> List[tuple]:
        """컬럼별 통계를 생성합니다."""
        column_counts = {}
        for error in errors:
            column_counts[error.column_name] = (
                column_counts.get(error.column_name, 0) + 1
            )

        total_errors = len(errors)
        stats = []
        for column, count in column_counts.items():
            ratio = (count / total_errors * 100) if total_errors > 0 else 0
            stats.append((column, count, ratio))

        return sorted(stats, key=lambda x: x[1], reverse=True)

    def _get_row_stats(self, errors: List[ValidationError]) -> List[tuple]:
        """행별 통계를 생성합니다."""
        row_counts = {}
        for error in errors:
            row_counts[error.row_number] = row_counts.get(error.row_number, 0) + 1

        return sorted(row_counts.items(), key=lambda x: x[0])

    def _calculate_success_rate(self, result: ValidationResult) -> float:
        """성공률을 계산합니다."""
        if result.total_rows == 0:
            return 100.0

        error_count = len(result.errors)
        success_rate = ((result.total_rows - error_count) / result.total_rows) * 100
        return max(0.0, success_rate)

    def _generate_statistics_dict(self, result: ValidationResult) -> Dict[str, Any]:
        """통계 정보를 딕셔너리로 생성합니다."""
        return {
            "error_type_stats": [
                {"error_type": error_type, "count": count, "ratio": ratio}
                for error_type, count, ratio in self._get_error_type_stats(
                    result.errors
                )
            ],
            "column_stats": [
                {"column": column, "count": count, "ratio": ratio}
                for column, count, ratio in self._get_column_stats(result.errors)
            ],
            "row_stats": [
                {"row": row, "count": count}
                for row, count in self._get_row_stats(result.errors)
            ],
            "success_rate": self._calculate_success_rate(result),
        }
    
    def _format_distribution_analysis(self, result: ValidationResult) -> str:
        """분포 분석 결과를 포맷팅합니다."""
        if not result.distribution_analysis:
            return ""
        
        sections = ["## 📈 컬럼 분포 분석\n"]
        
        for column_name, analysis_result in result.distribution_analysis.items():
            sections.append(f"### {column_name}")
            sections.append(f"- **데이터 타입**: {analysis_result.data_type}")
            sections.append(f"- **전체 행 수**: {analysis_result.total_count:,}")
            sections.append(f"- **null 값 수**: {analysis_result.null_count:,}")
            sections.append(f"- **null 비율**: {analysis_result.null_percentage:.2f}%")
            sections.append(f"- **처리 시간**: {analysis_result.processing_time:.4f}초")
            
            # 범주형 분포
            if hasattr(analysis_result.distribution, 'categories'):
                sections.append("\n**범주별 분포:**")
                for category in analysis_result.distribution.categories:
                    sections.append(f"- {category.value}: {category.count:,}개 ({category.percentage:.2f}%)")
                
                if analysis_result.distribution.other_count > 0:
                    sections.append(f"- 기타: {analysis_result.distribution.other_count:,}개 ({analysis_result.distribution.other_percentage:.2f}%)")
                
                sections.append(f"- **고유값 총 개수**: {analysis_result.distribution.unique_count:,}")
            
            # 숫자형 분포
            elif hasattr(analysis_result.distribution, 'stats') and analysis_result.distribution.stats:
                stats = analysis_result.distribution.stats
                sections.append("\n**통계 정보:**")
                sections.append(f"- 평균: {stats.mean:.2f}")
                sections.append(f"- 중앙값: {stats.median:.2f}")
                sections.append(f"- 표준편차: {stats.std:.2f}")
                sections.append(f"- 최솟값: {stats.min:.2f}")
                sections.append(f"- 최댓값: {stats.max:.2f}")
                sections.append(f"- 25% 분위수: {stats.q25:.2f}")
                sections.append(f"- 75% 분위수: {stats.q75:.2f}")
                
                sections.append("\n**구간별 분포:**")
                for bin_info in analysis_result.distribution.bins:
                    sections.append(f"- {bin_info.range[0]:.1f} - {bin_info.range[1]:.1f}: {bin_info.count:,}개 ({bin_info.percentage:.2f}%)")
                
                sections.append(f"- **자동 생성된 구간**: {'예' if analysis_result.distribution.auto_generated else '아니오'}")
            
            sections.append("")  # 빈 줄 추가
        
        return "\n".join(sections)

    def _format_distribution_analysis_html(self, result: ValidationResult) -> str:
        """
        분포 분석 결과를 HTML 형식으로 포맷팅합니다.
        
        Args:
            result: 검증 결과 객체
            
        Returns:
            str: HTML 형식의 분포 분석 결과
        """
        if not result.distribution_analysis:
            return ""
        
        sections = []
        sections.append('<h2><span class="emoji">📊</span> 컬럼 분포 분석</h2>')
        
        for column_name, analysis_result in result.distribution_analysis.items():
            sections.append(f'<div style="margin: 20px 0; padding: 20px; background: #f8f9fa; border-radius: 8px; border-left: 4px solid #007bff;">')
            sections.append(f'<h3><span class="emoji">📈</span> {column_name} 컬럼</h3>')
            
            # 기본 정보
            sections.append('<table style="width: 100%; margin: 10px 0;">')
            sections.append('<tr><th style="width: 30%;">항목</th><th>값</th></tr>')
            sections.append(f'<tr><td>데이터 타입</td><td>{analysis_result.data_type}</td></tr>')
            sections.append(f'<tr><td>총 개수</td><td>{analysis_result.total_count:,}</td></tr>')
            sections.append(f'<tr><td>NULL 개수</td><td>{analysis_result.null_count:,}</td></tr>')
            sections.append(f'<tr><td>NULL 비율</td><td>{analysis_result.null_percentage:.2f}%</td></tr>')
            sections.append('</table>')
            
            # 범주형 분포
            if hasattr(analysis_result.distribution, 'categories'):
                sections.append('<h4>📋 범주별 분포</h4>')
                sections.append('<table style="width: 100%; margin: 10px 0;">')
                sections.append('<tr><th>범주</th><th>개수</th><th>비율</th></tr>')
                
                for category in analysis_result.distribution.categories:
                    sections.append(f'<tr><td>{category.value}</td><td>{category.count:,}</td><td>{category.percentage:.2f}%</td></tr>')
                
                if analysis_result.distribution.other_count > 0:
                    sections.append(f'<tr><td>기타</td><td>{analysis_result.distribution.other_count:,}</td><td>{analysis_result.distribution.other_percentage:.2f}%</td></tr>')
                
                sections.append('</table>')
                sections.append(f'<p><strong>고유값 총 개수:</strong> {analysis_result.distribution.unique_count:,}</p>')
            
            # 숫자형 분포
            elif hasattr(analysis_result.distribution, 'statistics'):
                stats = analysis_result.distribution.statistics
                sections.append('<h4>📊 통계 정보</h4>')
                sections.append('<table style="width: 100%; margin: 10px 0;">')
                sections.append('<tr><th>통계</th><th>값</th></tr>')
                sections.append(f'<tr><td>평균</td><td>{stats.mean:.2f}</td></tr>')
                sections.append(f'<tr><td>중앙값</td><td>{stats.median:.2f}</td></tr>')
                sections.append(f'<tr><td>표준편차</td><td>{stats.std:.2f}</td></tr>')
                sections.append(f'<tr><td>최솟값</td><td>{stats.min:.2f}</td></tr>')
                sections.append(f'<tr><td>최댓값</td><td>{stats.max:.2f}</td></tr>')
                sections.append(f'<tr><td>25% 분위수</td><td>{stats.q25:.2f}</td></tr>')
                sections.append(f'<tr><td>75% 분위수</td><td>{stats.q75:.2f}</td></tr>')
                sections.append('</table>')
                
                sections.append('<h4>📈 구간별 분포</h4>')
                sections.append('<table style="width: 100%; margin: 10px 0;">')
                sections.append('<tr><th>구간</th><th>개수</th><th>비율</th></tr>')
                
                for bin_info in analysis_result.distribution.bins:
                    sections.append(f'<tr><td>{bin_info.range[0]:.1f} - {bin_info.range[1]:.1f}</td><td>{bin_info.count:,}</td><td>{bin_info.percentage:.2f}%</td></tr>')
                
                sections.append('</table>')
                sections.append(f'<p><strong>자동 생성된 구간:</strong> {"예" if analysis_result.distribution.auto_generated else "아니오"}</p>')
            
            sections.append('</div>')
        
        return '\n'.join(sections)