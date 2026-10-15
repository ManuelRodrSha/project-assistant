def update_project_llm(db: Session, project_id: int, payload):
    project = get_project(db, project_id)
    if not project:
        return None

    if payload.llm_model is not None:
        project.llm_model = payload.llm_model
    if payload.llm_temperature is not None:
        project.llm_temperature = payload.llm_temperature

    db.commit()
    db.refresh(project)
    return project