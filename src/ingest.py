import os
from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, CSVLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
INDEX_DIR = Path(__file__).resolve().parent.parent / "faiss_index"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def cargar_documentos():
    """Carga todos los PDF y CSV encontrados en /data."""
    documentos = []

    if not DATA_DIR.exists():
        raise FileNotFoundError(
            f"No existe la carpeta {DATA_DIR}. Crea 'data/' y coloca ahí tus PDFs/CSVs."
        )

    archivos = list(DATA_DIR.glob("*"))
    if not archivos:
        raise FileNotFoundError(
            f"La carpeta {DATA_DIR} está vacía. Coloca ahí tus documentos (PDF o CSV)."
        )

    for archivo in archivos:
        try:
            if archivo.suffix.lower() == ".pdf":
                print(f"Leyendo PDF: {archivo.name}")
                loader = PyPDFLoader(str(archivo))
                docs = loader.load()
                for d in docs:
                    d.metadata["source"] = archivo.name
                documentos.extend(docs)

            elif archivo.suffix.lower() == ".csv":
                print(f"Leyendo CSV: {archivo.name}")
                loader = CSVLoader(file_path=str(archivo), encoding="utf-8")
                docs = loader.load()
                for d in docs:
                    d.metadata["source"] = archivo.name
                documentos.extend(docs)

            else:
                print(f"Ignorado (formato no soportado): {archivo.name}")

        except Exception as e:
            print(f"  ⚠️  Error leyendo {archivo.name}: {e}")

    print(f"\nTotal de documentos cargados: {len(documentos)}")
    return documentos


def trocear_documentos(documentos):
    """Divide los documentos en fragmentos manejables para el modelo."""
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150,
        separators=["\n\n", "\n", ".", " ", ""],
    )
    fragmentos = splitter.split_documents(documentos)
    print(f"Total de fragmentos (chunks) generados: {len(fragmentos)}")
    return fragmentos


def construir_indice(fragmentos):
    """Genera embeddings locales y construye/guarda el índice FAISS."""
    print(f"\nGenerando embeddings con el modelo local '{EMBEDDING_MODEL}'...")
    print("(la primera vez descarga el modelo, ~90MB, luego funciona sin internet)")

    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    vectorstore = FAISS.from_documents(fragmentos, embeddings)

    vectorstore.save_local(str(INDEX_DIR))
    print(f"\n✅ Índice guardado en: {INDEX_DIR}")


if __name__ == "__main__":
    print("=== Ingesta de documentos — Alura Agente ===\n")
    docs = cargar_documentos()
    chunks = trocear_documentos(docs)
    construir_indice(chunks)
    print("\nListo. Ahora puedes ejecutar: python src/agent.py  (modo consola)")
    print("o: streamlit run src/app.py  (interfaz web)")
