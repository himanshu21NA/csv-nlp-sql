# Technical Design Document: CSV-NLP-SQL

## Overview
CSV-NLP-SQL is an AI-powered analytics platform enabling users to query CSV data using natural language. The system translates user queries into SQL, executes them on uploaded CSV files, and provides both SQL and natural language answers with full data citation. This empowers non-technical users to extract insights from tabular data without writing SQL, while ensuring transparency and trust.

## Key Features
- **Natural Language to SQL**: Users ask questions in plain English; the app generates robust, explainable SQL queries.
- **Schema Understanding & Cleaning**: The app analyzes and cleans the structure of uploaded CSVs, ensuring SQL compatibility and generating human-readable descriptions for each column.
- **Multiple SQL Generation Strategies**: The backend generates several candidate SQL queries using advanced prompt engineering and selects the best one via ranking.
- **Conversational Analytics**: Users can view all candidate SQL queries, iterate on questions, and understand how the app interprets their intent.
- **Natural Language Answer Generation**: The system summarizes SQL results in plain English, always citing the DataFrame as evidence.
- **Enterprise-Ready UI**: Built with Streamlit for rapid adoption by business and technical users.
- **Error-Resilient Execution**: Smart error handling and feedback for seamless user experience.

## Architecture
- **Frontend**: Streamlit app for user interaction (upload, query, results display, NL answer).
- **Backend**: Python modules for schema analysis, SQL generation, query execution, and NL answer generation.
- **AI Integration**: Uses OpenAI's GPT models for SQL, schema description, and NL answer generation.
- **Utilities**: Helper functions for data cleaning, formatting, and prompt management.
- **Testing**: Pytest-based tests for backend logic.

## Detailed Flow
1. **Upload CSV**: User uploads a CSV file via the web interface.
2. **Schema Analysis & Cleaning**: The backend infers and cleans the table schema, generating semantic descriptions for each column using OpenAI.
3. **Ask a Question**: User enters a natural language question about the data.
4. **SQL Generation**: The app generates multiple SQL candidates using different prompt strategies and selects the best one.
5. **Query Execution**: The selected SQL is executed on the cleaned DataFrame using SQLite or DuckDB.
6. **Natural Language Answer**: The result is summarized in plain English, with the DataFrame as the citation.
7. **Results Display**: Results and NL answer are shown in the app, with options to download or view all candidate queries.

## Extensibility
- **Add More Data Sources**: Support for Excel, Parquet, or database connections can be added.
- **Custom Prompting**: Prompts for SQL, schema, and NL answer generation are modular and customizable in `prompts.py`.
- **Advanced Analytics**: Aggregate, join, and filter operations can be enhanced.
- **User Authentication**: Can be integrated for multi-user environments.

## Security & Privacy
- Data is processed in-memory and not stored permanently.
- API keys and sensitive configs are managed via environment variables.

## Usage Scenarios
- Business analysts querying sales or operations data.
- Data exploration for non-technical users.
- Rapid prototyping and ad-hoc reporting.

## File Structure (Key Files)
- `src/frontend/app.py`: Main web app.
- `src/backend/chase_sql_v2.py`: SQL generation logic.
- `src/backend/schema_descriptor.py`: Schema analysis and description.
- `src/backend/sql_executor.py`: SQL execution engine.
- `src/backend/nl_answer.py`: Natural language answer generation.
- `src/backend/prompts.py`: Centralized prompt templates.
- `tests/`: Automated tests.

## Getting Started
1. Install dependencies: `pip install -r requirements.txt`
2. Set your OpenAI API key in `.env`
3. Run the app: `streamlit run src/frontend/app.py`

---
For more details, see the README or contact the development team.
