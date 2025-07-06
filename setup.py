from setuptools import setup, find_packages

setup(
    name="csv-nlp-sql",
    version="0.1.0",
    description="Natural Language to SQL Query System for CSV files",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    python_requires=">=3.13",
    install_requires=[
        "streamlit>=1.28.0",
        "pandas>=2.1.0",
        "numpy>=1.24.0",
        "openai>=1.3.0",
        "sqlparse>=0.4.4",
        "python-dotenv>=1.0.0",
        "openpyxl>=3.1.0",
        "xlrd>=2.0.1",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "black>=23.7.0",
            "flake8>=6.0.0",
            "isort>=5.12.0",
        ],
        "advanced": [
            "duckdb>=0.9.0",
            "polars>=0.19.0",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.13",
    ],
)