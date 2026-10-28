"""Configuração compartilhada: carrega o .env e monta embeddings/LLM conforme AI_PROVIDER."""

import os

from dotenv import load_dotenv

load_dotenv()

AI_PROVIDER = os.getenv("AI_PROVIDER", "openai").lower()

POSTGRES_USER = os.getenv("POSTGRES_USER", "postgres")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres")
POSTGRES_DB = os.getenv("POSTGRES_DB", "rag")
POSTGRES_HOST = os.getenv("POSTGRES_HOST", "localhost")
POSTGRES_PORT = os.getenv("POSTGRES_PORT", "5432")

PG_CONNECTION_STRING = (
    f"postgresql+psycopg://{POSTGRES_USER}:{POSTGRES_PASSWORD}"
    f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
)
PG_COLLECTION_NAME = os.getenv("PG_COLLECTION_NAME", "document_collection")

PDF_PATH = os.getenv("PDF_PATH", "document.pdf")
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "1000"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))
SEARCH_K = int(os.getenv("SEARCH_K", "10"))


def get_embeddings():
    if AI_PROVIDER == "openai":
        from langchain_openai import OpenAIEmbeddings

        return OpenAIEmbeddings(
            model=os.getenv("OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    if AI_PROVIDER == "gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings

        return GoogleGenerativeAIEmbeddings(
            model=os.getenv("GOOGLE_EMBEDDING_MODEL", "models/gemini-embedding-001"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
    raise ValueError(f"AI_PROVIDER inválido: {AI_PROVIDER!r} (use 'openai' ou 'gemini')")


def get_llm():
    if AI_PROVIDER == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=os.getenv("OPENAI_LLM_MODEL", "gpt-5-nano"),
            api_key=os.getenv("OPENAI_API_KEY"),
        )
    if AI_PROVIDER == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI

        return ChatGoogleGenerativeAI(
            model=os.getenv("GOOGLE_LLM_MODEL", "gemini-3.5-flash-lite"),
            google_api_key=os.getenv("GOOGLE_API_KEY"),
        )
    raise ValueError(f"AI_PROVIDER inválido: {AI_PROVIDER!r} (use 'openai' ou 'gemini')")
