from chaining import (
    adder_chain,
    parallel_chain,
    parallel_double_surround,
    s,
    surround_thrice,
)
from document import file_runnable
from langchain_core.globals import set_debug
from runnables import add_one, adder, greeter, lambda_adder
from tokens import print_tokens


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


if __name__ == "__main__":
    main()
