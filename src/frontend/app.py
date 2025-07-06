import streamlit as st
import pandas as pd
import logging
from pathlib import Path
import sys
import os
import re
import json
import openai
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from src.utils.helpers import clean_column_names
from src.backend.csv_analyzer import CSVAnalyzer
from src.backend.schema_descriptor import SchemaDescriptor
from src.backend.chase_sql_v2 import ChaseSQL
from src.backend.sql_executor import SQLExecutor
from src.backend.nl_answer import generate_natural_language_answer
from config.config import Config


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def clean_sql(sql: str, table_name: str = None, columns: list = None) -> str:
    # Extract SQL from markdown code block if present
    code_block = re.search(r"```sql(.*?)```", sql, re.DOTALL | re.IGNORECASE)
    if code_block:
        sql = code_block.group(1).strip()
    # Fallback: extract first SQL-like statement
    lines = sql.splitlines()
    sql_lines = []
    in_sql = False
    for line in lines:
        if re.match(r"^\s*select|^\s*with|^\s*insert|^\s*update|^\s*delete", line, re.IGNORECASE):
            in_sql = True
        if in_sql:
            sql_lines.append(line)
            if line.strip().endswith(';'):
                break
    if sql_lines:
        sql = '\n'.join(sql_lines).strip()
    # Remove markdown and explanations
    sql = re.sub(r'^```sql[\s\n]*', '', sql.strip(), flags=re.IGNORECASE)
    sql = re.sub(r'^```[\s\n]*', '', sql.strip())
    sql = re.sub(r'```$', '', sql.strip())
    sql = re.sub(r'^sql\s+', '', sql.strip(), flags=re.IGNORECASE)
    # Remove table or alias prefixes from column names if columns are provided
    if columns:
        for col in columns:
            sql = re.sub(rf'\b\w+\.{col}\b', col, sql)
    return sql.strip()

def main():
    st.set_page_config(
        page_title="CSV Natural Language Query System",
        page_icon="📊",
        layout="wide"
    )
    
    st.title("📊 CSV Natural Language Query System")
    st.markdown("Upload a CSV file and ask questions about your data in natural language!")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Check API key
        if not Config.OPENAI_API_KEY:
            st.error("⚠️ OpenAI API key not found. Please set OPENAI_API_KEY in your environment variables.")
            st.stop()
        else:
            st.success("✅ OpenAI API key configured")
        
        st.info(f"Model: {Config.OPENAI_MODEL}")
        st.info(f"Max file size: {Config.MAX_FILE_SIZE}MB")
    
    # File upload
    uploaded_file = st.file_uploader(
        "Upload CSV file",
        type=['csv'],
        help=f"Maximum file size: {Config.MAX_FILE_SIZE}MB"
    )
    
    if uploaded_file is not None:
        try:
            # Load and display data
            df = pd.read_csv(uploaded_file)
            df = clean_column_names(df)  # Clean column names
            # Check file size
            if len(df) > Config.MAX_ROWS:
                st.warning(f"File has {len(df)} rows. Only first {Config.MAX_ROWS} rows will be processed.")
                df = df.head(Config.MAX_ROWS)

            # Display data preview
            st.subheader("📋 Data Preview")
            st.dataframe(df.head(), use_container_width=True)
            
            # Display basic info
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Rows", len(df))
            with col2:
                st.metric("Columns", len(df.columns))
            with col3:
                st.metric("Size", f"{uploaded_file.size / 1024:.1f} KB")
            
            # Generate schema
            with st.spinner("Analyzing CSV structure..."):
                analyzer = CSVAnalyzer(max_rows=Config.MAX_ROWS)
                # Save uploaded file temporarily
                temp_path = f"temp_{uploaded_file.name}"
                df.to_csv(temp_path, index=False)
                
                try:
                    schema = analyzer.analyze_csv(temp_path)
                finally:
                    # Clean up temp file
                    if os.path.exists(temp_path):
                        os.remove(temp_path)
            
            # Generate semantic descriptions (only once per file)
            schema_key = f"enhanced_schema_{uploaded_file.name}_{uploaded_file.size}"
            if schema_key not in st.session_state:
                with st.spinner("Generating semantic descriptions..."):
                    descriptor = SchemaDescriptor()
                    enhanced_schema = descriptor.generate_descriptions(schema)
                    st.session_state[schema_key] = enhanced_schema
            else:
                enhanced_schema = st.session_state[schema_key]
            # Display schema information
            with st.expander("🔍 Schema Information"):
                st.json(enhanced_schema)
            
            # Query interface
            st.subheader("💬 Ask Questions About Your Data")
            
            # Example queries
            st.markdown("**Example queries:**")
            examples = [
                "Show me the first 10 rows",
                "What are the unique values in the first column?",
                "Count the number of rows for each category",
                "Show me the average of numeric columns",
                "Find the maximum value in each numeric column"
            ]
            
            example_cols = st.columns(len(examples))
            for i, example in enumerate(examples):
                if example_cols[i].button(example, key=f"example_{i}"):
                    st.session_state.query_input = example
            
            # Chatbot memory: store last 5 conversations (question, best_sql, summary)
            if 'chat_history' not in st.session_state:
                st.session_state['chat_history'] = []
            
            # Query input
            query = st.text_input(
                "Enter your question:",
                value=st.session_state.get('query_input', ''),
                placeholder="e.g., What is the average age by department?"
            )
            
            if query:
                st.subheader("🔄 Processing Query")
                # Ensure columns is a list of dicts for ChaseSQL
                schema_for_chase = enhanced_schema.copy()
                if isinstance(schema_for_chase['columns'], dict):
                    schema_for_chase['columns'] = [
                        {'name': k, **v} for k, v in schema_for_chase['columns'].items()
                    ]
                # Generate SQL candidates using new ChaseSQL class
                with st.spinner("Generating SQL queries..."):
                    chase = ChaseSQL(schema_for_chase, query)
                    chase.generate_candidates()
                candidates = chase.get_all_candidates()
                if candidates:
                    # Display candidates
                    with st.expander("🎯 SQL Candidates"):
                        for i, candidate in enumerate(candidates, 1):
                            st.markdown(f"**{candidate['source'].replace('_', ' ').title()} Candidate {i}:**")
                            st.code(candidate['sql'], language='sql')
                    # Select best candidate
                    chase.rank_candidates(db_executor=SQLExecutor(), sample_df=df)
                    best_sql = chase.get_best_sql()
                    st.subheader("✅ Selected SQL Query")
                    st.code(best_sql, language='sql')
                    # Execute query
                    try:
                        with st.spinner("Executing query..."):
                            executor = SQLExecutor()
                            # Remove table/alias prefixes from column names
                            columns = [col['name'] for col in schema_for_chase['columns']]
                            cleaned_sql = clean_sql(best_sql, table_name=enhanced_schema['table_name'], columns=columns)
                            print(f"Executing cleaned SQL: {cleaned_sql}")
                            # Execute the SQL query
                            result = executor.execute_query(df, cleaned_sql, enhanced_schema['table_name'])
                            print(f"Result DataFrame: {result.to_markdown()}")
                        st.subheader("📊 Query Results")
                        if len(result) > 0:
                            st.dataframe(result, use_container_width=True)
                            # Download results
                            csv_result = result.to_csv(index=False)
                            st.download_button(
                                label="📥 Download Results",
                                data=csv_result,
                                file_name=f"query_results_{uploaded_file.name}",
                                mime="text/csv"
                            )
                            # Generate and display natural language answer
                            with st.spinner("Generating natural language answer..."):
                                nl_answer = generate_natural_language_answer(query, cleaned_sql, result)
                            st.subheader("📝 Natural Language Answer")
                            st.markdown(nl_answer)
                            st.caption("The above answer is based on the query results shown as the citation.")
                        else:
                            st.info("Query returned no results.")
                        # Add to chat history (with summary)
                        summary = f"Q: {query}\nSQL: {best_sql}\nRows: {len(result) if result is not None else 0}"
                        st.session_state['chat_history'].append({
                            'question': query,
                            'sql': best_sql,
                            'summary': summary
                        })
                        # Keep only last 5
                        st.session_state['chat_history'] = st.session_state['chat_history'][-5:]
                    except Exception as e:
                        st.error(f"Error executing query: {str(e)}")
                        st.code(best_sql, language='sql')
                else:
                    st.error("Could not generate SQL queries. Please try rephrasing your question.")
            # Display chat history (last 5)
            if st.session_state['chat_history']:
                st.sidebar.markdown("### 🧠 Conversation Memory (Last 5)")
                for i, chat in enumerate(reversed(st.session_state['chat_history']), 1):
                    st.sidebar.markdown(f"**{i}.** {chat['summary']}")
        
        except Exception as e:
            st.error(f"Error processing file: {str(e)}")
            logger.error(f"Error in main app: {str(e)}")

if __name__ == "__main__":
    main()