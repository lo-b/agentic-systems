from uuid import uuid4

from langchain_community.document_loaders import UnstructuredMarkdownLoader
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda


def file_runnable(path: str) -> int:
    raise NotImplementedError("Implement me")
