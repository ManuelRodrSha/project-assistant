from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, JSON, String, Text, func
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), unique=True, nullable=False, index=True)
    description = Column(Text, default="")
    stack = Column(JSON, default=list)
    active = Column(Boolean, default=False, nullable=False)

    llm_provider = Column(String(50), default="openai", nullable=False)
    llm_model = Column(String(100), default="gpt-4.1-mini", nullable=False)
    llm_base_url = Column(String(255), nullable=True)
    llm_temperature = Column(Float, default=0.2, nullable=False)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class ProjectState(Base):
    __tablename__ = "project_states"

    project_id = Column(Integer, ForeignKey("projects.id"), primary_key=True)

    summary = Column(Text, default="")
    current_goal = Column(Text, default="")
    open_tasks = Column(JSON, default=list)
    decisions = Column(JSON, default=list)
    blockers = Column(JSON, default=list)
    notes = Column(JSON, default=list)

    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())