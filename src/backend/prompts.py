"""
Prompts for SQL generation, schema description, and related tasks.
"""

# Prompt for direct translation
DIRECT_TRANSLATION_PROMPT = """
Convert this natural language query to SQL using the provided schema.

Query: {query}

Schema Information:
Table: {table_name}
Columns: {columns}

Column Details:
{column_details}

Return only the SQL query, no explanations. Do not use table or alias prefixes in column names unless required by SQL syntax.
"""

# Prompt for template-based SQL generation
TEMPLATE_BASED_PROMPT = """

You are an expert SQL generator. Convert this natural language query to SQL.

<Instructions>
- Read the query carefully and identify the main action (e.g., SELECT, COUNT, AVG).
- Read the available columns and their meanings.
- Do not use the column names apart from the available columns. 
</Instructions>
Query: {query}
Table: {table_name}
Available columns: {columns}

Return only the SQL query.
"""

# Prompt for semantic parsing SQL generation
SEMANTIC_PARSING_PROMPT = """
Parse the semantic meaning of this query and convert to SQL:

Query: {query}

Schema with semantic information:
{semantic_schema}

Consider the semantic meaning of each column when generating SQL.
Return only the SQL query.
"""

# Prompt for schema description
SCHEMA_DESCRIPTION_PROMPT = """
Analyze this CSV schema and provide semantic descriptions in JSON format:
Table Name: {table_name}
Table Schema: {table_schema}
Column Details: {columns_json}

- By Using Column Details , Table Name and Table Schema, provide:
1. semantic_meaning: What this column represents
2. business_purpose: Likely business use case
3. relationships: How it might relate to other columns
- Description should be concise and focused on the column's role in the dataset.
- This description will be used for creating SQL queries using Natural Language.
- Provide description in paragraph format by using above points in 50 words or less.

Return a JSON object "description" as key and description value as value.

"""

ZERO_SHOT_PROMPT = """
You are an expert SQL developer. Generate ONLY valid, executable SQL queries.

CRITICAL REQUIREMENTS:
- Use :parameter_name syntax for any dynamic values
- Validate all table and column names exist in the provided schema
- Return only the SQL query without explanations
- Ensure query is compatible with SQLAlchemy execution

Schema: {schema_text}

Question: {user_question}

Write a valid SQL query using this schema (use parameterized queries for safety):
"""

FEW_SHOT_PROMPT = """
Schema: 
Table: students
- name: name of the student
- grade: grade level  
- subject: subject name
- marks: test score

Q: What is the average marks per subject?
SQL: SELECT subject, AVG(marks) FROM students GROUP BY subject;

Q: What is the average marks for a specific grade?
SQL: SELECT AVG(marks) FROM students WHERE grade = :grade_level;

Now use this schema:

{schema_text}

REQUIREMENTS:
- Generate only valid SQL queries
- Use :parameter_name syntax for dynamic values
- Verify all table/column names exist in schema
- Ensure query is SQLAlchemy compatible

Q: {user_question}
SQL: 
"""

SCHEMA_AWARE_PROMPT = """
You are a data assistant. Use the following schema to write a SQL query that answers the user's question.

MANDATORY RULES:
1. Generate ONLY executable SQL queries
2. Use :parameter_name syntax for any user inputs or dynamic values
3. Validate all table and column names against the provided schema
4. Include proper error handling considerations (NULL checks, data type validation)
5. Optimize for performance where possible
6. Ensure compatibility with SQLAlchemy execution

Schema Information:
{schema_text}

Question: {user_question}

Validation Checklist:
□ All referenced tables exist in schema
□ All column names are correct and properly typed
□ Parameters use :param_name syntax
□ Query handles potential NULL values appropriately
□ Query structure is optimized for performance

SQL Query:
"""
COT_PROMPT = """
You are an expert SQL analyst. Think step-by-step to solve the user's question using SQL.

Schema: {schema_text}

Question: {user_question}

Step-by-step reasoning:
1. Carefully read and understand the user's question
2. Identify the relevant tables and columns from the schema that are needed to answer the question
3. Verify all referenced tables and columns exist in the provided schema
4. Determine any necessary filtering, grouping, or aggregation required
5. Plan the SQL query structure (SELECT, FROM, WHERE, GROUP BY, etc.)
6. Consider performance implications and data types
7. Use :parameter_name syntax for any dynamic values to prevent SQL injection
8. Write the final SQL query that answers the question

SQL Query (executable with SQLAlchemy):
"""
NATURAL_LANGUAGE_ANSWER_PROMPT = """
You are a helpful data assistant.

The user asked: "{question}"

The following SQL query was generated and executed:
{sql}

The result of the query is:
{result_preview}

Based on the above, provide a clear and concise natural language answer to the user's question. If the result is a table, summarize the key findings. Always use the table as the citation for your answer.
"""
RERANK_PROMPT= """
Question: {question}

Here are {len} SQL queries and table information {table_schema}:

{queries}

Which query most accurately answers the question? Just give the best SQL.
"""