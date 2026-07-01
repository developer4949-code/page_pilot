"""
Factory for creating LLM provider instances.

The rest of the application should never directly instantiate
a provider such as ChatGroq or ChatOpenAI.

Instead, always use:

    llm = LLMFactory.create()

This makes switching providers extremely easy.
"""

from config.settings import LLM_PROVIDER

from llm.groq_provider import GroqProvider
from llm.provider import BaseLLM


class LLMFactory:
    """
    Factory class responsible for creating
    the configured LLM provider.
    """

    @staticmethod
    def create() -> BaseLLM:
        """
        Create and return the configured LLM provider.

        Returns
        -------
        BaseLLM
            An instance of the selected provider.

        Raises
        ------
        ValueError
            If an unsupported provider is configured.
        """

        provider = LLM_PROVIDER.lower()

        if provider == "groq":
            return GroqProvider()

        # Future providers
        #
        # elif provider == "gemini":
        #     return GeminiProvider()
        #
        # elif provider == "openai":
        #     return OpenAIProvider()

        raise ValueError(
            f"Unsupported LLM provider: {LLM_PROVIDER}"
        )