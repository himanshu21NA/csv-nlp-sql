import openai
from .prompts import NATURAL_LANGUAGE_ANSWER_PROMPT
from .llm import llm_generate_content
def generate_natural_language_answer(question: str, sql: str, result_df):
    """
    Generate a natural language answer to a user's question based on the SQL query and its result DataFrame.
    The DataFrame is used as the citation for the answer.
    """
    # Prepare a concise preview of the result
    result_preview = result_df.to_markdown(index=False)
    prompt = NATURAL_LANGUAGE_ANSWER_PROMPT.format(
        question=question,
        sql=sql,
        result_preview=result_preview
    )
    # Call OpenAI API to generate the answer
    return llm_generate_content(
        prompt=prompt,
        pydantic_model= None)