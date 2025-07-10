import json
import logging
from typing import Dict, Any
from openai import OpenAI
from config.config import Config
from .prompts import SCHEMA_DESCRIPTION_PROMPT
from .schemas import ColumnDescription
from .llm import llm_generate_content
import numpy as np
import asyncio
logger = logging.getLogger(__name__)

class SchemaDescriptor:
    """Generates semantic descriptions for CSV schemas using OpenAI"""
    
    
    def generate_descriptions(self, schema: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate semantic descriptions for the schema using OpenAI
        
        Args:
            schema: Dictionary containing schema information
            
        Returns:
            Enhanced schema with descriptions
        """
        try:
            descriptions =  {}
            for k, v in schema["columns"].items():
                # Convert all numpy types to native Python types for JSON serialization
                def convert_types(obj):
                    if isinstance(obj, dict):
                        return {kk: convert_types(vv) for kk, vv in obj.items()}
                    elif isinstance(obj, list):
                        return [convert_types(i) for i in obj]
                    elif isinstance(obj, (np.integer, np.floating, np.bool_)):
                        return obj.item()
                    else:
                        return obj
                v_native = convert_types(v)
                prompt = SCHEMA_DESCRIPTION_PROMPT.format(
                    table_name=schema['table_name'],
                    table_schema=schema,
                    columns_json=k + " : " + json.dumps(v_native, indent=2)
                )
                asyncio.sleep(0.5)  # Small delay to avoid rate limiting
                response = llm_generate_content(
                    prompt=prompt,
                    pydantic_model=ColumnDescription)
                description = response
                print(f"Description for {k}: {description}")
                
                parsed = json.loads(description)
                descriptions[k] = parsed["description"] if "description" in parsed else description
            # Parse and enhance schema
            enhanced_schema = self._enhance_schema_with_descriptions(schema, json.dumps(descriptions))
            
            logger.info(f"Generated descriptions for table: {schema['table_name']}")
            return enhanced_schema
            
        except Exception as e:
            logger.error(f"Error generating descriptions: {str(e)}")
            # Return original schema if description generation fails
            return schema
    
    # def _build_description_prompt(self, schema: Dict[str, Any]) -> str:
    #     """Build prompt for generating schema descriptions"""
    #     return SCHEMA_DESCRIPTION_PROMPT.format(
    #         table_name=schema['table_name'],
    #         columns_json=json.dumps(schema['columns'], indent=2)
    #     )
    
    def _enhance_schema_with_descriptions(self, schema: Dict[str, Any], description: str) -> Dict[str, Any]:
        """Enhance schema with generated descriptions"""
        enhanced_schema = schema.copy()
        
        try:
            # Try to parse the description as JSON
            descriptions_dict = json.loads(description)
            print("Descriptions:", descriptions_dict)
            for column_name, column_info in enhanced_schema["columns"].items():
                if column_name in descriptions_dict:
                    column_info["description"] = descriptions_dict[column_name]
                    
        except json.JSONDecodeError:
            # If parsing fails, add the raw description
            enhanced_schema["raw_description"] = description
        
        return enhanced_schema