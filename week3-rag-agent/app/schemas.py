from pydantic import BaseModel, Field


class AskRequest(BaseModel):
    session_id: str = Field(..., min_length=3, description="Client-provided session id")
    question: str = Field(..., min_length=1, description="User question")


class AskResponse(BaseModel):
    answer: str
    used_tools: bool = False
    tool_name: str | None = None
    tool_input: str | None = None
    tool_output: str | None = None


class IngestTextRequest(BaseModel):
    text: str = Field(..., min_length=1)
    source: str = Field(default="manual", min_length=1)
