import math

from chaining import (
    adder_chain,
    parallel_chain,
    parallel_double_surround,
    sequence,
    surround_thrice,
)
from document import file_runnable
from langchain_core.globals import set_debug
from runnables import add_one_runnable, adder_runnable, greeter_runnable, lambda_adder
from tokens import print_tokens


def hformat(word: str, decal="/", total_width: int = 80) -> str:
    remaining = total_width - len(word)
    left_slashes = math.ceil(remaining / 2)
    right_slashes = math.floor(remaining / 2)

    return decal * left_slashes + word + decal * right_slashes


def main():
    print("////////////////////////////// module_01 //////////////////////////////")
    print("===== RUNNABLES =====")
    print("Add one to 7:", add_one_runnable.invoke(7))
    print("Adding 3 and 9:", adder_runnable.invoke({"a": 3, "b": 9}))
    print("Greeter:", greeter_runnable.invoke("World!"))
    print(f"Lambda adder: {lambda_adder.invoke({'a': 1, 'b': 2})}")

    print("===== CHAIN =====")
    print(f"Adder chain: {adder_chain.invoke({'a': 1, 'b': 2})}")

    print("===== PARALLEL CHAIN =====")
    print(parallel_chain.get_graph().draw_ascii())
    set_debug(True)
    print(f"output: {parallel_chain.invoke({'a': 7, 'b': 2})}")
    set_debug(False)
    print("===== SEQUENCE CHAIN =====")
    print(sequence.get_graph().draw_ascii())
    print(sequence.invoke({"a": 2, "b": 4}))
    print(surround_thrice.invoke(3))
    print(parallel_double_surround.invoke({"a": 3, "b": 3}))
    print("===== TOKENIZATION =====")
    print(print_tokens("Hello agentic world!"))

    print("===== DOCUMENT =====")
    print(file_runnable("./resources/some_file.md"))


if __name__ == "__main__":
    main()
