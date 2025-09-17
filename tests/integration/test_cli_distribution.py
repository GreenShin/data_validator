"""
Integration Tests for CLI Distribution Analysis

CLI 분포 분석 명령어의 통합 테스트
"""

import pytest
import sys
import os
import tempfile
import subprocess
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'src'))

# 구현이 완료되면 이 import들을 사용할 예정
# from cli.commands import main


class TestCLIDistributionIntegration:
    """CLI 분포 분석 통합 테스트"""
    
    def setup_method(self):
        """각 테스트 메서드 실행 전 설정"""
        # 테스트용 CSV 파일 생성
        self.test_csv_content = """category,price,quantity
Electronics,100.5,5
Books,25.3,10
Electronics,150.7,3
Clothing,75.2,8
Books,30.1,15
Electronics,200.0,2"""
        
        # 테스트용 설정 파일 생성
        self.test_config_content = """distribution_analysis:
  enabled: true
  columns:
    - name: "category"
      type: "categorical"
      max_categories: 100
    - name: "price"
      type: "numerical"
      auto_bins: true
    - name: "quantity"
      type: "numerical"
      bins: [0, 5, 10, 20]
"""
        
        # 임시 파일들 생성
        self.temp_csv = tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False)
        self.temp_csv.write(self.test_csv_content)
        self.temp_csv.close()
        
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False)
        self.temp_config.write(self.test_config_content)
        self.temp_config.close()
        
        # 출력 디렉토리 생성
        self.output_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """각 테스트 메서드 실행 후 정리"""
        if os.path.exists(self.temp_csv.name):
            os.unlink(self.temp_csv.name)
        if os.path.exists(self.temp_config.name):
            os.unlink(self.temp_config.name)
        if os.path.exists(self.output_dir):
            import shutil
            shutil.rmtree(self.output_dir)
    
    def test_cli_analyze_command_basic(self):
        """기본 CLI 분석 명령어 테스트"""
        pytest.skip("Implementation not ready - will be enabled after core implementation")
        
        # TODO: 구현 완료 후 활성화할 테스트
        # cmd = [
        #     sys.executable, "-m", "csv_validator", "validate",
        #     "--config", self.temp_config.name,
        #     "--input", self.temp_csv.name,
        #     "--output", self.output_dir,
        #     "--analyze"
        # ]
        # 
        # result = subprocess.run(cmd, capture_output=True, text=True)
        # 
        # assert result.returncode == 0
        # assert "분포 분석 완료" in result.stdout
        # assert "category" in result.stdout
        # assert "price" in result.stdout
        # assert "quantity" in result.stdout
    
    def test_cli_analyze_command_without_analyze_flag(self):
        """분석 플래그 없이 CLI 명령어 테스트"""
        pytest.skip("Implementation not ready - will be enabled after core implementation")
        
        # TODO: --analyze 플래그 없이 실행하여 분포 분석이 비활성화되는지 확인
        # cmd = [
        #     sys.executable, "-m", "csv_validator", "validate",
        #     "--config", self.temp_config.name,
        #     "--input", self.temp_csv.name,
        #     "--output", self.output_dir
        # ]
        # 
        # result = subprocess.run(cmd, capture_output=True, text=True)
        # 
        # assert result.returncode == 0
        # assert "분포 분석" not in result.stdout
    
    def test_cli_analyze_command_invalid_config(self):
        """잘못된 설정 파일로 CLI 명령어 테스트"""
        pytest.skip("Implementation not ready - will be enabled after core implementation")
        
        # TODO: 잘못된 설정 파일로 실행하여 오류 처리 확인
        # invalid_config_content = """invalid_yaml: content
        # [unclosed bracket"""
        # 
        # invalid_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False)
        # invalid_config.write(invalid_config_content)
        # invalid_config.close()
        # 
        # try:
        #     cmd = [
        #         sys.executable, "-m", "csv_validator", "validate",
        #         "--config", invalid_config.name,
        #         "--input", self.temp_csv.name,
        #         "--output", self.output_dir,
        #         "--analyze"
        #     ]
        # 
        #     result = subprocess.run(cmd, capture_output=True, text=True)
        # 
        #     assert result.returncode != 0
        #     assert "설정 파일 오류" in result.stderr or "YAML 오류" in result.stderr
        # finally:
        #     os.unlink(invalid_config.name)
    
    def test_cli_analyze_command_missing_column(self):
        """존재하지 않는 컬럼으로 CLI 명령어 테스트"""
        pytest.skip("Implementation not ready - will be enabled after core implementation")
        
        # TODO: 존재하지 않는 컬럼을 설정에 포함하여 오류 처리 확인
        # invalid_config_content = """distribution_analysis:
        #   enabled: true
        #   columns:
        #     - name: "nonexistent_column"
        #       type: "categorical"
        #       max_categories: 100
        # """
        # 
        # invalid_config = tempfile.NamedTemporaryFile(mode='w', suffix='.yml', delete=False)
        # invalid_config.write(invalid_config_content)
        # invalid_config.close()
        # 
        # try:
        #     cmd = [
        #         sys.executable, "-m", "csv_validator", "validate",
        #         "--config", invalid_config.name,
        #         "--input", self.temp_csv.name,
        #         "--output", self.output_dir,
        #         "--analyze"
        #     ]
        # 
        #     result = subprocess.run(cmd, capture_output=True, text=True)
        # 
        #     assert result.returncode != 0
        #     assert "컬럼을 찾을 수 없음" in result.stderr or "nonexistent_column" in result.stderr
        # finally:
        #     os.unlink(invalid_config.name)
    
    def test_cli_analyze_command_verbose_output(self):
        """상세 출력 모드로 CLI 명령어 테스트"""
        pytest.skip("Implementation not ready - will be enabled after core implementation")
        
        # TODO: --verbose 플래그로 상세 출력 확인
        # cmd = [
        #     sys.executable, "-m", "csv_validator", "validate",
        #     "--config", self.temp_config.name,
        #     "--input", self.temp_csv.name,
        #     "--output", self.output_dir,
        #     "--analyze",
        #     "--verbose"
        # ]
        # 
        # result = subprocess.run(cmd, capture_output=True, text=True)
        # 
        # assert result.returncode == 0
        # assert "분포 분석 시작" in result.stdout
        # assert "분포 분석 완료" in result.stdout
        # assert "처리 시간" in result.stdout
    
    def test_cli_analyze_command_output_files(self):
        """CLI 명령어 출력 파일 테스트"""
        pytest.skip("Implementation not ready - will be enabled after core implementation")
        
        # TODO: 출력 파일들이 올바르게 생성되는지 확인
        # cmd = [
        #     sys.executable, "-m", "csv_validator", "validate",
        #     "--config", self.temp_config.name,
        #     "--input", self.temp_csv.name,
        #     "--output", self.output_dir,
        #     "--analyze"
        # ]
        # 
        # result = subprocess.run(cmd, capture_output=True, text=True)
        # 
        # assert result.returncode == 0
        # 
        # # 출력 파일들 확인
        # output_files = list(Path(self.output_dir).glob("*"))
        # assert len(output_files) > 0
        # 
        # # HTML, JSON, Markdown 파일이 있는지 확인
        # html_files = list(Path(self.output_dir).glob("*.html"))
        # json_files = list(Path(self.output_dir).glob("*.json"))
        # md_files = list(Path(self.output_dir).glob("*.md"))
        # 
        # assert len(html_files) > 0
        # assert len(json_files) > 0
        # assert len(md_files) > 0
        # 
        # # HTML 파일에 분포 분석 결과가 포함되어 있는지 확인
        # with open(html_files[0], 'r', encoding='utf-8') as f:
        #     html_content = f.read()
        #     assert "분포 분석" in html_content
        #     assert "category" in html_content
        #     assert "price" in html_content


if __name__ == "__main__":
    pytest.main([__file__])