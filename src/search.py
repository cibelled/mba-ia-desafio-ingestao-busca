"""Busca semântica: vetoriza a pergunta e retorna os k resultados mais relevantes do pgVector."""

from langchain_postgres import PGVector

import config


def get_vector_store() -> PGVector:
    embeddings = config.get_embeddings()
    return PGVector(
        embeddings=embeddings,
        collection_name=config.PG_COLLECTION_NAME,
        connection=config.PG_CONNECTION_STRING,
        use_jsonb=True,
    )


def search(query: str, k: int = config.SEARCH_K):
    store = get_vector_store()
    return store.similarity_search_with_score(query, k=k)


if __name__ == "__main__":
    pergunta = input("Pergunta para teste de busca: ")
    resultados = search(pergunta)
    for doc, score in resultados:
        print(f"\n--- score={score:.4f} ---")
        print(doc.page_content)
