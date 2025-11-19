import math

from langchain_core.globals import set_debug
from langchain_core.runnables import RunnableLambda, RunnableSequence


def add_ten(x: int) -> int:
    return x + 10


def double(x: int) -> int:
    return x * 2


def process_number(x: int) -> int:
    return x // int(math.pi * math.e)


def format_result(x: int) -> str:
    return f"Final result: {x}"


add_ten_runnable: RunnableLambda[int, int] = RunnableLambda(add_ten)
double_runnable: RunnableLambda[int, int] = RunnableLambda(double)
process_runnable: RunnableLambda[int, int] = RunnableLambda(process_number)
format_runnable: RunnableLambda[int, str] = RunnableLambda(format_result)

buggy_chain = RunnableSequence(
    add_ten_runnable, process_runnable, double_runnable, format_runnable
)

# TODO: fix the chain containing a bug below
print(buggy_chain(input=2))

# TODO: what is the output of '_process_number' for the input 722
# FIX: remove answer
set_debug(True)
print(buggy_chain.invoke(722))  # 91
print(buggy_chain.get_graph().draw_ascii())
