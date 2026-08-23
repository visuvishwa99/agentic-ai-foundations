"""Shared LM Studio clients for the Week 8 exercises."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from dotenv import load_dotenv


load_dotenv(Path(__file__).resolve().parent.parent / ".env")

LM_STUDIO_BASE_URL = os.getenv(
    "LM_STUDIO_BASE_URL",
    "http://127.0.0.1:1234/v1",
)
LM_STUDIO_API_KEY = os.getenv("LM_STUDIO_API_KEY", "lm-studio")
CHAT_MODEL = os.getenv("LM_STUDIO_CHAT_MODEL", "qwen2.5-coder-1.5b-instruct")
EMBEDDING_MODEL = os.getenv(
    "LM_STUDIO_EMBEDDING_MODEL",
    "text-embedding-nomic-embed-text-v1.5",
)


def parse_json_object(content: str) -> dict[str, Any]:
    """Parse a JSON object from a raw or fenced model response."""
    text = content.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end < start:
        raise ValueError("LM Studio response did not contain a JSON object")

    result = json.loads(text[start : end + 1])
    if not isinstance(result, dict):
        raise ValueError("LM Studio response was not a JSON object")
    return result


def create_chat_model(
    model_name: str = CHAT_MODEL,
    *,
    temperature: float = 0,
) -> ChatOpenAI:
    """Create a LangChain chat client for the local LM Studio API."""
    return ChatOpenAI(
        model=model_name,
        base_url=LM_STUDIO_BASE_URL,
        api_key=LM_STUDIO_API_KEY,
        temperature=temperature,
    )


def create_embedding_model(
    model_name: str = EMBEDDING_MODEL,
) -> OpenAIEmbeddings:
    """Create an embeddings client for the local LM Studio API."""
    return OpenAIEmbeddings(
        model=model_name,
        base_url=LM_STUDIO_BASE_URL,
        api_key=LM_STUDIO_API_KEY,
        check_embedding_ctx_length=False,
    )
