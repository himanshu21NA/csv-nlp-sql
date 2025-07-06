import logging
from typing import List, Dict, Any, Optional
from openai import OpenAI
from config.config import Config
from .prompts import ZERO_SHOT_PROMPT, COT_PROMPT, FEW_SHOT_PROMPT, SCHEMA_AWARE_PROMPT
from .schemas import SQLGenerationResponse
from openai.lib._parsing._completions import type_to_response_format_param
logger = logging.getLogger(__name__)

class ChaseSQL:
    def __init__(self, schema: dict, question: str, api_key: Optional[str] = None):
        self.schema = schema
        self.question = question
        self.client = OpenAI(api_key=api_key or Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
        self.candidates: List[Dict[str, str]] = []
        self.best_sql: Optional[str] = None

    def serialize_schema(self) -> str:
        lines = [f"Schema:\nTable: {self.schema['table_name']}"]
        for col in self.schema['columns']:
            desc = col.get('description', col.get('type', ''))
            lines.append(f"- {col['name']}: {desc} ({col.get('type', '')})")
        return '\n'.join(lines)

    def generate_candidates(self):
        schema_text = self.serialize_schema()
        prompts = [
            ("zero_shot", ZERO_SHOT_PROMPT.format(schema_text=schema_text, user_question=self.question)),
            ("cot", COT_PROMPT.format(schema_text=schema_text, user_question=self.question)),
            ("few_shot", FEW_SHOT_PROMPT.format(schema_text=schema_text, user_question=self.question)),
            ("schema_aware", SCHEMA_AWARE_PROMPT.format(schema_text=schema_text, user_question=self.question)),
        ]
        self.candidates = []
        for source, prompt in prompts:
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.1,
                    response_format= type_to_response_format_param(SQLGenerationResponse)
                )
                llm_content = response.choices[0].message.content
                try:
                    parsed = SQLGenerationResponse.parse_raw(llm_content)
                    sql = parsed.sql
                except Exception:
                    sql = llm_content.strip()
                self.candidates.append({"source": source, "sql": sql})
            except Exception as e:
                logger.error(f"Error generating SQL for {source}: {str(e)}")

    def rank_candidates(self, rerank_with_llm: bool = False, db_executor=None, sample_df=None) -> None:
        if rerank_with_llm and len(self.candidates) > 1:
            # LLM reranker
            queries = '\n'.join([f"SQL {i+1}: {c['sql']}" for i, c in enumerate(self.candidates)])
            rerank_prompt = f"""
Question: {self.question}

Here are {len(self.candidates)} SQL queries:
{queries}

Which query most accurately answers the question? Just give the best SQL.
"""
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[{"role": "user", "content": rerank_prompt}],
                    temperature=0.1
                )
                self.best_sql = response.choices[0].message.content.strip()
                return
            except Exception as e:
                logger.error(f"Error reranking SQL candidates: {str(e)}")
        # Rule-based: try executing on sample data if provided
        best_score = float('-inf')
        best_sql = None
        for c in self.candidates:
            score = 0
            if db_executor and sample_df is not None:
                try:
                    result = db_executor.execute_query(sample_df, c['sql'], self.schema['table_name'])
                    if result is not None and len(result) > 0:
                        score += 10
                except Exception:
                    score -= 5
            # Prefer simpler queries
            score -= c['sql'].count('(')
            if score > best_score:
                best_score = score
                best_sql = c['sql']
        self.best_sql = best_sql

    def get_best_sql(self) -> str:
        return self.best_sql

    def get_all_candidates(self) -> List[Dict[str, str]]:
        return self.candidates
