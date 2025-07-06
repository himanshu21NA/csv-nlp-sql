import openai
from .prompts import NATURAL_LANGUAGE_ANSWER_PROMPT

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
    response = openai.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.0
    )
    return response.choices[0].message.content
