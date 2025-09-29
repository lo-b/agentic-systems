from langchain_core.runnables import RunnableLambda


def _add_one(a: int) -> int:
    return a + 1


def _adder(a: int, b: int) -> int:
    return a + b


def _adder_wrapper(_input: dict[str, int]) -> int:
    return _adder(_input["a"], _input["b"])


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

add_one: RunnableLambda[int, int] = RunnableLambda(_add_one)
adder: RunnableLambda[dict[str, int], int] = RunnableLambda(
    _adder_wrapper, name="adder"
)
_greeter: Greeter = Greeter(greeting="Hello")
greeter: RunnableLambda[str, str] = RunnableLambda(_greeter)
