from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
    RunnableSequence,
)
from runnables import adder_runnable

t: RunnableLambda[int, dict[str, int]] = RunnableLambda(
    lambda x: {"a": x, "b": x}, name="transform"
)

adder_chain = RunnableSequence(adder_runnable, t, adder_runnable)

parallel_chain = RunnableParallel(a=adder_runnable, b=adder_runnable)

sequence = RunnableSequence(parallel_chain, adder_runnable)


def _f(x):
    return f"({x})"


surround = RunnableLambda(_f)

surround_thrice = surround | surround | surround

parallel_double_surround = RunnablePassthrough() | {
    "a": surround | surround,
    "b": surround | surround,
}
