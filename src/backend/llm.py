from typing import Any, Dict
import logging
from openai import OpenAI
from config.config import Config
import logging
from openai.lib._parsing._completions import type_to_response_format_param
logger = logging.getLogger(__name__)
def llm_generate_content(prompt: str ,pydantic_model) -> str:
        """
        Generate content using OpenAI LLM based on the provided prompt.
        
        Args:
            prompt: The input prompt for the LLM.
            
        Returns:
            ColumnDescription: The generated content as a ColumnDescription object.
        """
        try:
            client = OpenAI(api_key=Config.OPENAI_API_KEY)
            model = Config.OPENAI_MODEL 
            # Call OpenAI API to generate content
            if pydantic_model is None:
                # If no Pydantic model is provided, use a simple string response
                response = client.chat.completions.create(
                            model=model,
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.0)
            else:
                response = client.chat.completions.create(
                            model=model,
                            messages=[{"role": "user", "content": prompt}],
                            temperature=0.0,
                            response_format= type_to_response_format_param(pydantic_model))
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error generating content: {str(e)}")
            raise
       
                