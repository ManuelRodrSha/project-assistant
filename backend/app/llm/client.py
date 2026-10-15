from openai import OpenAI

from app.core.config import settings


def build_client():
    if not settings.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY no configurada")

    return OpenAI(api_key=settings.OPENAI_API_KEY)