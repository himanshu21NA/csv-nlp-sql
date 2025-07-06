import logging
import sqlparse
from typing import List, Dict, Any, Tuple
from openai import OpenAI
from config.config import Config
from .prompts import DIRECT_TRANSLATION_PROMPT, TEMPLATE_BASED_PROMPT, SEMANTIC_PARSING_PROMPT

logger = logging.getLogger(__name__)

class CHASESQLGenerator:
    """Implements CHASE SQL methodology for generating and selecting SQL queries"""
    
    def __init__(self, schema: Dict[str, Any], api_key: str = None):
        self.schema = schema
        self.client = OpenAI(api_key=api_key or Config.OPENAI_API_KEY)
        self.model = Config.OPENAI_MODEL
        self.max_candidates = Config.MAX_SQL_CANDIDATES
    
    def generate_sql_candidates(self, natural_query: str) -> List[str]:
        """
        Generate multiple SQL candidates using different strategies
        
        Args:
            natural_query: Natural language query
            
        Returns:
            List of SQL query candidates
        """
        candidates = []
        
        try:
            # Strategy 1: Direct translation
            candidates.append(self._direct_translation(natural_query))
            
            # Strategy 2: Template-based approach
            candidates.append(self._template_based_approach(natural_query))
            
            # Strategy 3: Semantic parsing
            candidates.append(self._semantic_parsing_approach(natural_query))
            
            # Filter out None values and duplicates
            candidates = [c for c in candidates if c is not None]
            candidates = list(dict.fromkeys(candidates))  # Remove duplicates
            
            logger.info(f"Generated {len(candidates)} SQL candidates")
            return candidates
            
        except Exception as e:
            logger.error(f"Error generating SQL candidates: {str(e)}")
            return []
    
    def assess_candidates(self, candidates: List[str]) -> str:
        """
        Assess SQL candidates and return the best one
        
        Args:
            candidates: List of SQL query candidates
            
        Returns:
            Best SQL query
        """
        if not candidates:
            return ""
        
        scored_candidates = []
        
        for candidate in candidates:
            score = self._score_sql_candidate(candidate)
            scored_candidates.append((candidate, score))
        
        # Sort by score (descending)
        scored_candidates.sort(key=lambda x: x[1], reverse=True)
        
        best_candidate = scored_candidates[0][0]
        logger.info(f"Selected best candidate with score: {scored_candidates[0][1]}")
        
        return best_candidate
    
    def _direct_translation(self, query: str) -> str:
        prompt = DIRECT_TRANSLATION_PROMPT.format(
            query=query,
            table_name=self.schema['table_name'],
            columns=', '.join(self.schema['columns'].keys()),
            column_details=self._format_column_details()
        )
        return self._call_openai(prompt)
    
    def _template_based_approach(self, query: str) -> str:
        prompt = TEMPLATE_BASED_PROMPT.format(
            query=query,
            table_name=self.schema['table_name'],
            columns=', '.join(self.schema['columns'].keys())
        )
        return self._call_openai(prompt)
    
    def _semantic_parsing_approach(self, query: str) -> str:
        prompt = SEMANTIC_PARSING_PROMPT.format(
            query=query,
            semantic_schema=self._format_semantic_schema()
        )
        return self._call_openai(prompt)
    
    def _call_openai(self, prompt: str) -> str:
        """Make OpenAI API call"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            return ""
    
    def  _score_sql_candidate(self, sql: str) -> float:
        """Score a SQL candidate based on various criteria"""
        score = 0.0
        
        # Check syntax validity
        try:
            parsed = sqlparse.parse(sql)
            if parsed:
                score += 40
        except:
            score -= 20
        
        # Check column references
        table_columns = set(self.schema['columns'].keys())
        sql_lower = sql.lower()
        
        for column in table_columns:
            if column.lower() in sql_lower:
                score += 10
        
        # Check for table name
        if self.schema['table_name'].lower() in sql_lower:
            score += 20
        
        # Prefer simpler queries (less complex syntax)
        complexity_penalty = sql.count('(') + sql.count('JOIN') * 2
        score -= complexity_penalty
        
        return score
    
    def _format_column_details(self) -> str:
        """Format column details for prompts"""
        details = []
        for col_name, col_info in self.schema['columns'].items():
            details.append(f"- {col_name}: {col_info['data_type']}, "
                         f"unique values: {col_info['unique_values']}, "
                         f"sample: {col_info['sample_values'][:3]}")
        return '\n'.join(details)
    
    def _format_semantic_schema(self) -> str:
        """Format schema with semantic information"""
        details = []
        for col_name, col_info in self.schema['columns'].items():
            desc = col_info.get('description', {})
            semantic_meaning = desc.get('semantic_meaning', 'No description') if isinstance(desc, dict) else str(desc)
            details.append(f"- {col_name}: {semantic_meaning}")
        return '\n'.join(details)