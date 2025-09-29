from os import environ
from statistics import median
from uuid import uuid4

from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_core.documents import Document
from langchain_nomic import NomicEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams

assert load_dotenv(), ".env file missing or empty"


def load_pdf_as_docs(
    path: str, chunk_size_overlap: tuple[int, int] | None = None
) -> list[Document]:
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

    return docs


def vector_store_index(
    docs: list[Document],
    collection_name: str,
    batch_size: int = 128,
) -> QdrantVectorStore:
    embeddings = NomicEmbeddings(
        model="nomic-embed-text-v1.5", inference_mode="local", device="cpu"
    )
    sample_text = "SAMPLE TEXT"  # example text to determine embedding size
    embedding_size = len(embeddings.embed_query(sample_text))

    client = QdrantClient(
        url=f"https://{environ['QDRANT_CLUSTER_ENDPOINT']}:6333",
        api_key=environ["QDRANT_API_KEY"],
    )

    if not client.collection_exists(collection_name):
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(size=embedding_size, distance=Distance.COSINE),
        )

    code_vector_store = QdrantVectorStore(
        client=client,
        collection_name=collection_name,
        embedding=embeddings,
    )

    if (
        client.collection_exists(collection_name)
        and client.get_collection(collection_name).points_count == 0
    ):
        uuids = [str(uuid4()) for _ in range(len(docs))]
        code_vector_store.add_documents(
            documents=docs, ids=uuids, batch_size=batch_size
        )

    return code_vector_store
