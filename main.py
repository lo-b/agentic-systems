from pprint import pp

from langchain_core.globals import set_debug

from module_01.chaining import (
    adder_chain,
    parallel_chain,
    parallel_double_surround,
    s,
    surround_thrice,
)
from module_01.document import file_runnable
from module_01.runnables import add_one, adder, greeter, lambda_adder
from module_01.tokens import print_tokens
from module_02.cloud_retriever import load_pdf_as_docs, vector_store_index
from module_02.document_retriever import index_book


def main():
    print("==== module_01 ====")
    print("Add one to 7:", add_one.invoke(7))
    print("Adding 3 and 9:", adder.invoke({"a": 3, "b": 9}))
    print("Greeter:", greeter.invoke("World!"))
    print(f"Lambda adder: {lambda_adder.invoke({'a': 1, 'b': 2})}")
    print(f"Adder chain: {adder_chain.invoke({'a': 1, 'b': 2})}")

    print("PARALLEL CHAIN")
    print(parallel_chain.get_graph().draw_ascii())
    set_debug(True)
    print(f"parallel adder: {parallel_chain.invoke({'a': 7, 'b': 2})}")
    set_debug(False)
    print(s.get_graph().draw_ascii())
    print(s.invoke({"a": 2, "b": 4}))

    print(surround_thrice.invoke(3))
    print(parallel_double_surround.invoke({"a": 3, "b": 3}))
    print(print_tokens("Hello agentic world!"))
    print(file_runnable("./resources/some_file.md"))

    print("==== module_02 ====")
    print("SIMPLE INDEX")
    retriever = index_book(
        path="./resources/the-little-go-book-karl-seguin.pdf",
        tmp_path="./tmp/retriever",
        chunk_size_overlap=(250, 50),
    )

    answer = retriever.similarity_search("iterate array", k=1)
    pp(answer[0].model_dump())

    print("CLOUD INDEX")
    docs = load_pdf_as_docs(
        "./resources/the-little-go-book-karl-seguin.pdf",
        chunk_size_overlap=(250, 50),
    )
    vstore = vector_store_index(docs, "little-go-book-local-embeds")
    retriever = vstore.as_retriever()
    pp(retriever.invoke("iterate array")[0].model_dump())


if __name__ == "__main__":
    main()
