from openai import OpenAI
from app.core.config import settings


def clean_url(url):
    if url is None:
        return None
    url = str(url).strip()
    return url if url else None


def build_client(provider: str, base_url: str | None = None):
    provider = (provider or "").lower().strip()
    base_url = clean_url(base_url)

    if provider == "openai":
        if not settings.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY no configurada")

        # Por defecto, usa la URL oficial de OpenAI
        final_base_url = clean_url(settings.OPENAI_BASE_URL) or "https://api.openai.com/v1"

        # Si el proyecto tiene una base_url específica válida, la usamos
        if base_url:
            final_base_url = base_url

        return OpenAI(
            api_key=settings.OPENAI_API_KEY,
            base_url=final_base_url,
        )

    if provider == "ollama":
        return OpenAI(
            api_key="ollama",
            base_url=base_url or settings.OLLAMA_BASE_URL,
        )

    if provider == "openai_compatible":
        if not base_url:
            raise ValueError("openai_compatible requiere base_url")
        return OpenAI(
            api_key="dummy",
            base_url=base_url,
        )

    raise ValueError(f"Proveedor LLM no soportado: {provider}")