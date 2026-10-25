"""LLM providers used to generate grounded answers."""

from __future__ import annotations

import os
from typing import Protocol


class LLMConfigurationError(RuntimeError):
    """Raised when a selected provider cannot be configured."""


class LLMClient(Protocol):
    def complete(self, prompt: str) -> str:
        """Return a completion for the supplied prompt."""


class OpenAIClient:
    def __init__(self, api_key: str) -> None:
        from openai import OpenAI

        self.client = OpenAI(api_key=api_key)

    def complete(self, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model="gpt-4o-mini",
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        return response.choices[0].message.content or ""


class AnthropicClient:
    def __init__(self, api_key: str) -> None:
        from anthropic import Anthropic

        self.client = Anthropic(api_key=api_key)

    def complete(self, prompt: str) -> str:
        response = self.client.messages.create(
            model="claude-3-5-haiku-latest",
            max_tokens=700,
            temperature=0,
            messages=[{"role": "user", "content": prompt}],
        )
        return "".join(block.text for block in response.content if block.type == "text")


def get_llm() -> LLMClient:
    """Build the LLM client selected by LLM_PROVIDER."""
    provider = os.getenv("LLM_PROVIDER", "").lower()
    if provider == "openai":
        key = os.getenv("OPENAI_API_KEY")
        if key:
            return OpenAIClient(key)
    elif provider == "anthropic":
        key = os.getenv("ANTHROPIC_API_KEY")
        if key:
            return AnthropicClient(key)
    elif provider:
        raise LLMConfigurationError("LLM_PROVIDER must be 'openai' or 'anthropic'.")
    raise LLMConfigurationError("Add LLM_PROVIDER and its API key to .env before asking a question.")
