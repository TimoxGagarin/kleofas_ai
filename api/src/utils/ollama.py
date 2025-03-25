import httpx

from api.src.settings import settings


async def chat_with_llama(messages: list[dict[str, str]]) -> str:
    async with httpx.AsyncClient() as client:
        return (
            await client.post(
                f"http://{settings.OLLAMA_HOST}:{settings.OLLAMA_PORT}/api/chat",
                json={
                    "model": "llama3.2",
                    "messages": messages,
                    "stream": False,
                },
                timeout=60,
            )
        ).json()["message"]["content"]
