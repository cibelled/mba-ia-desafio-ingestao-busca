"""Lê o PDF configurado, divide em chunks e grava os embeddings no PostgreSQL/pgVector."""

from langchain_community.document_loaders import PyPDFLoader
from langchain_postgres import PGVector
from langchain_text_splitters import RecursiveCharacterTextSplitter
from tenacity import retry, stop_after_attempt, wait_exponential

import config

# Lotes pequenos evitam bater no rate limit de embeddings da API (free tier do Gemini, por ex.)
BATCH_SIZE = 10


@retry(stop=stop_after_attempt(6), wait=wait_exponential(multiplier=2, min=5, max=60), reraise=True)
def _add_batch(store: PGVector, batch: list) -> None:
    # Retry com backoff: a camada gratuita de embeddings (Gemini/OpenAI) limita requisições por
    # minuto, e PDFs grandes passam desse limite mesmo em lotes.
    store.add_documents(batch)


def ingest() -> None:
    print(f"Carregando PDF: {config.PDF_PATH}")
    loader = PyPDFLoader(config.PDF_PATH)
    documents = loader.load()

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=config.CHUNK_SIZE,
        chunk_overlap=config.CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(documents)
    print(f"{len(chunks)} chunks gerados (chunk_size={config.CHUNK_SIZE}, overlap={config.CHUNK_OVERLAP})")

    embeddings = config.get_embeddings()

    store = PGVector(
        embeddings=embeddings,
        collection_name=config.PG_COLLECTION_NAME,
        connection=config.PG_CONNECTION_STRING,
        use_jsonb=True,
        pre_delete_collection=True,
    )

    total_batches = (len(chunks) - 1) // BATCH_SIZE + 1
    for i in range(0, len(chunks), BATCH_SIZE):
        batch = chunks[i : i + BATCH_SIZE]
        _add_batch(store, batch)
        print(f"Lote {i // BATCH_SIZE + 1}/{total_batches} gravado ({len(batch)} chunks)")

    print("Ingestão concluída com sucesso.")


if __name__ == "__main__":
    ingest()
