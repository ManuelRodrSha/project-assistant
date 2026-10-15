from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud
from app.db.session import get_db
from app.schemas import (
    ChatRequest,
    ChatResponse,
    ProjectCreate,
    ProjectLLMUpdate,
    ProjectRead,
    ProjectStateRead,
)
from app.services.agent import build_project_context, chat_with_agent

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.get("/projects", response_model=list[ProjectRead])
def list_projects(db: Session = Depends(get_db)):
    return crud.get_projects(db)


@router.post("/projects", response_model=ProjectRead)
def create_project(payload: ProjectCreate, db: Session = Depends(get_db)):
    existing = crud.get_project_by_name(db, payload.name)
    if existing:
        raise HTTPException(status_code=400, detail="Ya existe un proyecto con ese nombre")

    return crud.create_project(db, payload)


@router.post("/projects/{project_id}/activate", response_model=ProjectRead)
def activate_project(project_id: int, db: Session = Depends(get_db)):
    project = crud.set_active_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    return project


@router.get("/projects/active", response_model=ProjectRead)
def get_active_project(db: Session = Depends(get_db)):
    project = crud.get_active_project(db)
    if not project:
        raise HTTPException(status_code=404, detail="No hay proyecto activo")

    return project


@router.get("/projects/{project_id}/state", response_model=ProjectStateRead)
def get_project_state(project_id: int, db: Session = Depends(get_db)):
    project = crud.get_project(db, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    return crud.get_state(db, project_id)


@router.patch("/projects/{project_id}/llm", response_model=ProjectRead)
def update_project_llm(
    project_id: int,
    payload: ProjectLLMUpdate,
    db: Session = Depends(get_db),
):
    project = crud.update_project_llm(db, project_id, payload)
    if not project:
        raise HTTPException(status_code=404, detail="Proyecto no encontrado")

    return project


@router.post("/chat", response_model=ChatResponse)
def chat(payload: ChatRequest, db: Session = Depends(get_db)):
    # Elegir proyecto: explícito o activo
    if payload.project_id is not None:
        project = crud.get_project(db, payload.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Proyecto no encontrado")
    else:
        project = crud.get_active_project(db)
        if not project:
            raise HTTPException(status_code=400, detail="No hay proyecto activo")

    state = crud.get_state(db, project.id)

    project_context = build_project_context(project, state)

    global_context = {
        "mode": "homelab assistant",
        "notes": [
            "Asistente multi-proyecto sin acceso al código fuente",
            "Mantener contexto separado por proyecto",
        ],
    }

    llm_config = {
        "provider": project.llm_provider,
        "model": project.llm_model,
        "base_url": project.llm_base_url,
        "temperature": project.llm_temperature,
    }

    result = chat_with_agent(
        user_message=payload.message,
        project_context=project_context,
        global_context=global_context,
        llm_config=llm_config,
    )

    if result.memory_update:
        crud.apply_memory_update(db, project.id, result.memory_update)

    return ChatResponse(
        project_id=project.id,
        reply=result.reply,
        memory_update=result.memory_update,
        needs_clarification=result.needs_clarification,
    )