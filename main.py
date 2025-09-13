from langchain_core.globals import set_debug

from module_01.chaining import adder_chain, parallel_chain, s
from module_01.runnables import add_one, adder, greeter, lambda_adder


def main():
    print("==== module_01 ====")
    set_debug(True)
    print("Add one to 7:", add_one.invoke(7))
    set_debug(False)
    print("Adding 3 and 9:", adder.invoke({"a": 3, "b": 9}))
    print("Greeter:", greeter.invoke("World!"))
    print(f"Lambda adder: {lambda_adder.invoke({'a': 1, 'b': 2})}")

    print(f"Adder chain: {adder_chain.invoke({'a': 1, 'b': 2})}")
    print(f"parallel adder: {parallel_chain.invoke({'a': 7, 'b': 2})}")
    print(s.get_graph().draw_ascii())
    print(s.invoke({"a": 2, "b": 4}))


if __name__ == "__main__":
    main()
