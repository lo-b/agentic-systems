from pprint import pp

from cloud_retriever import load_pdf_as_docs, vector_store_index
from document_retriever import index_book


def main():
    print("////////////////////////////// module_02 //////////////////////////////")
    print("===== SIMPLE INDEX =====")
    retriever = index_book(
        path="./resources/the-little-go-book-karl-seguin.pdf",
        tmp_path="./tmp/retriever",
        chunk_size_overlap=(250, 50),
    )

    answer = retriever.similarity_search("iterate array", k=1)
    pp(answer[0].model_dump())

    print("===== CLOUD INDEX =====")
    docs = load_pdf_as_docs(
        "./resources/the-little-go-book-karl-seguin.pdf",
        chunk_size_overlap=(250, 50),
    )
    vstore = vector_store_index(docs, "little-go-book-local-embeds")
    retriever = vstore.as_retriever()
    pp(retriever.invoke("iterate array")[0].model_dump())


if __name__ == "__main__":
    main()
