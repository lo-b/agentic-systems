import math

from langchain.globals import set_debug
from langchain_core.runnables import RunnableLambda, RunnableSequence


def _add_ten(x: int) -> int:
    return x + 10


def _double(x: int) -> int:
    return x * 2


def _process_number(x: int) -> int:
    return x // int(math.pi * math.e)


def _format_result(x: int) -> str:
    return f"Final result: {x}"


add_ten: RunnableLambda[int, int] = RunnableLambda(_add_ten)
double: RunnableLambda[int, int] = RunnableLambda(_double)
process: RunnableLambda[int, int] = RunnableLambda(_process_number)
format_result: RunnableLambda[int, str] = RunnableLambda(_format_result)

buggy_chain = RunnableSequence(add_ten, process, double, format_result)

# TODO: fix the chain containing a bug below
print(buggy_chain(input=2))

# TODO: what is the output of '_process_number' for the input 722
# FIX: remove answer
set_debug(True)
print(buggy_chain.invoke(722))  # 91
print(buggy_chain.get_graph().draw_ascii())
