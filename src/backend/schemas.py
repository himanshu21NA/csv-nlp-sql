from pydantic import BaseModel
from typing import Optional

class ColumnDescription(BaseModel):
    description: str

class SQLGenerationResponse(BaseModel):
    sql: str
    explanation: Optional[str] = None
