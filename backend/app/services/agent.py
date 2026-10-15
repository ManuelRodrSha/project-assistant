import json
from pydantic import BaseModel, Field

from app.core.config import settings
from app.llm.client import build_client


SYSTEM_PROMPT = """
Eres un asistente multi-proyecto para programación y gestión de proyectos.

Reglas:
- No tienes acceso al código fuente.
- Solo trabajas con el contexto que te pasa el sistema.
- No inventes información.
- Si falta contexto, pide aclaración.
- Mantén separados los proyectos.
- Devuelve SIEMPRE JSON válido con esta estructura:

{
  "reply": "texto para el usuario",
  "memory_update": {
    "summary": "resumen actualizado o vacío",
    "current_goal": "objetivo actual o vacío",
    "open_tasks_add": [],
    "decisions_add": [],
    "blockers_add": [],
    "notes_add": []
  },
  "needs_clarification": false
}
"""


class AgentOutput(BaseModel):
    reply: str
    memory_update: dict = Field(default_factory=dict)
    needs_clarification: bool = False


def _safe_json_loads(text: str):
    text = text.strip()
    if text.startswith("```"):
        text = text.removeprefix("```json").removeprefix("```").strip()
        if text.endswith("```"):
            text = text[:-3].strip()
    return json.loads(text)


def build_project_context(project, state):
    return {
        "project": {
            "id": project.id,
            "name": project.name,
            "description": project.description,
            "stack": project.stack or [],
            "active": project.active,
            "llm_model": project.llm_model,
            "llm_temperature": project.llm_temperature,
        },
        "state": {
            "summary": state.summary,
            "current_goal": state.current_goal,
            "open_tasks": state.open_tasks or [],
            "decisions": state.decisions or [],
            "blockers": state.blockers or [],
            "notes": state.notes or [],
        },
    }


def chat_with_agent(user_message: str, project_context: dict, global_context: dict):
    client = build_client()

    model = project_context["project"].get("llm_model") or settings.DEFAULT_LLM_MODEL
    temperature = project_context["project"].get("llm_temperature", settings.DEFAULT_LLM_TEMPERATURE)

    prompt = f"""
Memoria global:
{json.dumps(global_context, ensure_ascii=False, indent=2)}

Contexto del proyecto activo:
{json.dumps(project_context, ensure_ascii=False, indent=2)}

Mensaje del usuario:
{user_message}

Responde solo con JSON válido.
"""

    response = client.chat.completions.create(
        model=model,
        temperature=temperature,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ],
    )

    raw = response.choices[0].message.content or ""

    try:
        data = _safe_json_loads(raw)
        return AgentOutput(**data)
    except Exception:
        return AgentOutput(
            reply=raw,
            memory_update={},
            needs_clarification=False,
        )