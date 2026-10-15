import json
from sqlalchemy.orm import Session

from app.db.models import Project, ProjectState
from app.schemas import ProjectCreate, ProjectLLMUpdate


def unique_list(items):
    seen = set()
    out = []
    for item in items:
        if item not in seen:
            seen.add(item)
            out.append(item)
    return out


def get_projects(db: Session):
    return db.query(Project).order_by(Project.active.desc(), Project.updated_at.desc()).all()


def get_project(db: Session, project_id: int):
    return db.query(Project).filter(Project.id == project_id).first()


def get_project_by_name(db: Session, name: str):
    return db.query(Project).filter(Project.name == name).first()


def get_active_project(db: Session):
    return db.query(Project).filter(Project.active.is_(True)).first()


def ensure_project_state(db: Session, project_id: int):
    state = db.query(ProjectState).filter(ProjectState.project_id == project_id).first()
    if not state:
        state = ProjectState(
            project_id=project_id,
            summary="",
            current_goal="",
            open_tasks=[],
            decisions=[],
            blockers=[],
            notes=[],
        )
        db.add(state)
        db.commit()
        db.refresh(state)
    return state


def create_project(db: Session, payload: ProjectCreate):
    project = Project(
        name=payload.name,
        description=payload.description,
        stack=payload.stack,
        active=False,
    )
    db.add(project)
    db.commit()
    db.refresh(project)

    ensure_project_state(db, project.id)
    return project


def set_active_project(db: Session, project_id: int):
    db.query(Project).update({Project.active: False})
    project = get_project(db, project_id)
    if not project:
        return None

    project.active = True
    db.commit()
    db.refresh(project)
    return project


def get_state(db: Session, project_id: int):
    return ensure_project_state(db, project_id)


def update_project_llm(db: Session, project_id: int, payload: ProjectLLMUpdate):
    project = get_project(db, project_id)
    if not project:
        return None

    if payload.llm_provider is not None:
        project.llm_provider = payload.llm_provider
    if payload.llm_model is not None:
        project.llm_model = payload.llm_model
    if payload.llm_base_url is not None:
        project.llm_base_url = payload.llm_base_url
    if payload.llm_temperature is not None:
        project.llm_temperature = payload.llm_temperature

    db.commit()
    db.refresh(project)
    return project


def update_state_from_payload(db: Session, project_id: int, payload):
    state = ensure_project_state(db, project_id)

    if payload.summary is not None:
        state.summary = payload.summary

    if payload.current_goal is not None:
        state.current_goal = payload.current_goal

    state.open_tasks = unique_list((state.open_tasks or []) + payload.open_tasks_add)
    state.decisions = unique_list((state.decisions or []) + payload.decisions_add)
    state.blockers = unique_list((state.blockers or []) + payload.blockers_add)
    state.notes = unique_list((state.notes or []) + payload.notes_add)

    db.commit()
    db.refresh(state)
    return state


def apply_memory_update(db: Session, project_id: int, memory_update: dict):
    """
    memory_update esperado:
    {
      "summary": "...",
      "current_goal": "...",
      "open_tasks_add": [...],
      "decisions_add": [...],
      "blockers_add": [...],
      "notes_add": [...]
    }
    """
    state = ensure_project_state(db, project_id)

    if memory_update.get("summary") is not None:
        state.summary = memory_update["summary"]

    if memory_update.get("current_goal") is not None:
        state.current_goal = memory_update["current_goal"]

    state.open_tasks = unique_list((state.open_tasks or []) + memory_update.get("open_tasks_add", []))
    state.decisions = unique_list((state.decisions or []) + memory_update.get("decisions_add", []))
    state.blockers = unique_list((state.blockers or []) + memory_update.get("blockers_add", []))
    state.notes = unique_list((state.notes or []) + memory_update.get("notes_add", []))

    db.commit()
    db.refresh(state)
    return state