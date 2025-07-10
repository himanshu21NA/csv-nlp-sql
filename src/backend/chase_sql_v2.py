import logging
from typing import List, Dict, Any, Optional
from config.config import Config
from .prompts import ZERO_SHOT_PROMPT, COT_PROMPT, FEW_SHOT_PROMPT, SCHEMA_AWARE_PROMPT , RERANK_PROMPT
from .schemas import SQLGenerationResponse
from .llm import llm_generate_content
logger = logging.getLogger(__name__)

class ChaseSQL:
    def __init__(self, schema: dict, question: str, api_key: Optional[str] = None):
        self.schema = schema
        self.question = question
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
                response = llm_generate_content(
                    prompt=prompt,
                    pydantic_model=SQLGenerationResponse
                )
                llm_content = response
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
            rerank_prompt = RERANK_PROMPT.format(
                question=self.question,
                len=len(self.candidates),
                queries=queries,
                table_name=self.schema['table_name'],
                columns=', '.join([col['name'] for col in self.schema['columns']])
            )
            logger.info(f"Rerank prompt: {rerank_prompt}")
            try:
                response = llm_generate_content(
                    prompt=rerank_prompt,
                    pydantic_model=SQLGenerationResponse
                )
                logger.info(f"Rerank response: {response}")
                # Use the first choice as the best SQL
                self.best_sql = response
                return
            except Exception as e:
                logger.error(f"Error reranking SQL candidates: {str(e)}")
        # Rule-based: try executing on sample data if provided
    

    def get_best_sql(self) -> str:
        return self.best_sql

    def get_all_candidates(self) -> List[Dict[str, str]]:
        return self.candidates
