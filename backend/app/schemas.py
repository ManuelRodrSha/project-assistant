from typing import Any, Optional

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str
    description: str = ""
    stack: list[str] = Field(default_factory=list)


class ProjectRead(BaseModel):
    id: int
    name: str
    description: str
    stack: list[str]
    active: bool
    llm_model: str
    llm_temperature: float

    class Config:
        from_attributes = True


class ProjectStateRead(BaseModel):
    project_id: int
    summary: str
    current_goal: str
    open_tasks: list[str]
    decisions: list[str]
    blockers: list[str]
    notes: list[str]

    class Config:
        from_attributes = True


class ProjectLLMUpdate(BaseModel):
    llm_model: Optional[str] = None
    llm_temperature: Optional[float] = None


class ChatRequest(BaseModel):
    message: str
    project_id: Optional[int] = None


class ChatResponse(BaseModel):
    project_id: int
    reply: str
    memory_update: dict[str, Any] = Field(default_factory=dict)
    needs_clarification: bool = False