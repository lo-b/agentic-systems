from langchain_core.runnables import RunnableLambda


def add_one(a: int) -> int:
    return a + 1


def adder(a: int, b: int) -> int:
    return a + b


def adder_wrapper(input: dict[str, int]) -> int:
    return adder(input["a"], input["b"])


class Greeter:
    greeting: str

    def __init__(self, greeting: str):
        self.greeting = greeting

    def __call__(self, *args) -> str:
        invoke_input = args[
            0
        ]  # invoke input will be the first argument of this call function
        return self.greeting + " " + invoke_input


lambda_adder: RunnableLambda[dict[str, int], int] = RunnableLambda(
    lambda d: d["a"] + d["b"]
)

add_one_runnable: RunnableLambda[int, int] = RunnableLambda(add_one)
adder_runnable: RunnableLambda[dict[str, int], int] = RunnableLambda(
    adder_wrapper, name="adder"
)
hello_greeter: Greeter = Greeter(greeting="Hello")
greeter_runnable: RunnableLambda[str, str] = RunnableLambda(hello_greeter)
