from pydantic import BaseModel

class AskRequest(BaseModel):
    question: str

class AskResponse(BaseModel):
    answer: str
    used_tools: bool = False