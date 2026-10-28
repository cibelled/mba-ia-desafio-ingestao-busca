"""CLI de chat: recebe perguntas do usuário e responde com base apenas no conteúdo do PDF ingerido."""

import config
from search import search

PROMPT_TEMPLATE = """CONTEXTO:
{contexto}

REGRAS:
- Responda somente com base no CONTEXTO.
- Se a informação não estiver explicitamente no CONTEXTO, responda:
  "Não tenho informações necessárias para responder sua pergunta."
- Nunca invente ou use conhecimento externo.
- Nunca produza opiniões ou interpretações além do que está escrito.

EXEMPLOS DE PERGUNTAS FORA DO CONTEXTO:
Pergunta: "Qual é a capital da França?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Quantos clientes temos em 2024?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

Pergunta: "Você acha isso bom ou ruim?"
Resposta: "Não tenho informações necessárias para responder sua pergunta."

PERGUNTA DO USUÁRIO:
{pergunta}

RESPONDA A "PERGUNTA DO USUÁRIO"
"""


def responder(pergunta: str, llm) -> str:
    resultados = search(pergunta, k=config.SEARCH_K)
    contexto = "\n\n".join(doc.page_content for doc, _score in resultados)
    prompt = PROMPT_TEMPLATE.format(contexto=contexto, pergunta=pergunta)
    resposta = llm.invoke(prompt)
    return resposta.content


def main() -> None:
    llm = config.get_llm()
    print("Chat pronto. Digite sua pergunta (ou 'sair' para encerrar).\n")
    while True:
        pergunta = input("PERGUNTA: ").strip()
        if not pergunta:
            continue
        if pergunta.lower() in {"sair", "exit", "quit"}:
            break
        resposta = responder(pergunta, llm)
        print(f"RESPOSTA: {resposta}\n")


if __name__ == "__main__":
    main()
