"""
Setup script for CSV Validator package.
"""

from setuptools import setup, find_packages

# Read the README file for long description
try:
    with open("README.md", "r", encoding="utf-8") as fh:
        long_description = fh.read()
except FileNotFoundError:
    long_description = "CSV 파일의 구문정확성을 검증하는 Python 도구"

# Read requirements from requirements.txt
try:
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]
except FileNotFoundError:
    requirements = [
        "pandas>=1.5.0",
        "PyYAML>=6.0", 
        "pydantic>=2.0",
        "click>=8.0",
        "rich>=13.0",
        "python-dateutil>=2.8",
        "email-validator>=2.0",
        "phonenumbers>=8.13",
    ]

setup(
    name="csv-validator",
    version="0.1.0",
    author="CSV Validator Team",
    author_email="greenshin.kr@gmail.com",
    description="CSV 파일의 구문정확성을 검증하는 Python 도구",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/GreenShin/data_validator",
    project_urls={
        "Bug Tracker": "https://github.com/GreenShin/data_validator/issues",
        "Documentation": "https://csv-validator.readthedocs.io",
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Text Processing :: Markup",
    ],
    package_dir={"": "."},
    packages=find_packages(where="."),
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0",
            "pytest-cov>=4.0",
            "black>=23.0",
            "flake8>=6.0",
            "mypy>=1.0",
            "pre-commit>=3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "csv-validator=src.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
