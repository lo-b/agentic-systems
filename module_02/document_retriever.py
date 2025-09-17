from pathlib import Path
from statistics import median

from langchain_community.document_loaders import PyPDFLoader
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_nomic import NomicEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter


def index_book(
    path: str, tmp_path: str, chunk_size_overlap: tuple[int, int] | None = None
) -> InMemoryVectorStore:
    embedding_model = NomicEmbeddings(
        model="nomic-embed-text-v1.5", inference_mode="local", device="cpu"
    )
    store = InMemoryVectorStore(embedding_model)
    fp = Path(tmp_path)

    if fp.exists():
        return store.load(tmp_path, embedding_model)

    loader = PyPDFLoader(path)
    docs = loader.load()
    print(
        "AMOUNT OF DOCUMENTS:",
        len(docs),
        "MEDIAN CONTENT LEN:",
        median([len(doc.page_content) for doc in docs]),
    )
    if chunk_size_overlap is not None:
        print("CHUNKING DOCUMENTS ...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size_overlap[0],
            chunk_overlap=chunk_size_overlap[1],
            add_start_index=True,
        )
        docs = text_splitter.split_documents(docs)
        print(
            "NEW AMOUNT:",
            len(docs),
            "NEW MEDIAN:",
            median([len(doc.page_content) for doc in docs]),
        )

    _ = store.add_documents(docs)
    store.dump(tmp_path)
    return store
