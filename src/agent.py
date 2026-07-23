import os
from pathlib import Path
from dotenv import load_dotenv

from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain.chains import create_retrieval_chain
from langchain_core.prompts import ChatPromptTemplate

load_dotenv()

INDEX_DIR = Path(__file__).resolve().parent.parent / "faiss_index"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
LLM_MODEL = "gemini-3-flash-preview" # modelo gratuito en Google AI Studio

PROMPT_SISTEMA = """Eres el asistente virtual interno de Santos Pegasus Soluciones.
Respondes preguntas de nuevos desarrolladores y empleados basándote
ÚNICAMENTE en el contexto de los documentos internos que se te entregan.

Reglas:
- Si la respuesta está en el contexto, respóndela de forma clara, directa y concreta.
- Si el contexto no contiene la respuesta, di explícitamente que no encontraste
  esa información en la documentación disponible. No inventes datos.
- Cuando sea útil, menciona de qué documento proviene la información.

Contexto:
{context}
"""


def cargar_agente():
    """Carga el índice vectorial y arma la cadena RAG. Devuelve el 'retrieval chain'."""
    if not INDEX_DIR.exists():
        raise FileNotFoundError(
            "No se encontró faiss_index/. Ejecuta primero: python src/ingest.py"
        )

    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise EnvironmentError(
            "No se encontró GOOGLE_API_KEY. Crea un archivo .env (copia .env.example) "
            "y pon tu clave de https://aistudio.google.com/apikey"
        )

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = FAISS.load_local(
        str(INDEX_DIR), embeddings, allow_dangerous_deserialization=True
    )
    retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

    llm = ChatGoogleGenerativeAI(model=LLM_MODEL, google_api_key=api_key, temperature=0)

    prompt = ChatPromptTemplate.from_messages(
        [("system", PROMPT_SISTEMA), ("human", "{input}")]
    )

    combine_docs_chain = create_stuff_documents_chain(llm, prompt)
    rag_chain = create_retrieval_chain(retriever, combine_docs_chain)
    return rag_chain


def preguntar(rag_chain, pregunta: str):
    """Hace una pregunta al agente y devuelve (respuesta, lista_de_fuentes)."""
    resultado = rag_chain.invoke({"input": pregunta})
    respuesta = resultado["answer"]
    fuentes = sorted({doc.metadata.get("source", "desconocido") for doc in resultado["context"]})
    return respuesta, fuentes


if __name__ == "__main__":
    print("=== Alura Agente — Santos Pegasus Soluciones (modo consola) ===")
    print("Escribe 'salir' para terminar.\n")

    chain = cargar_agente()

    while True:
        pregunta = input("Tú: ").strip()
        if pregunta.lower() in {"salir", "exit", "quit"}:
            break
        if not pregunta:
            continue

        respuesta, fuentes = preguntar(chain, pregunta)
        print(f"\nAgente: {respuesta}")
        print(f"(Fuente(s): {', '.join(fuentes)})\n")
