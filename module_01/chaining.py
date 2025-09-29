from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
    RunnableSequence,
)
from runnables import adder

_t: RunnableLambda[int, dict[str, int]] = RunnableLambda(
    lambda x: {"a": x, "b": x}, name="transform"
)

adder_chain = RunnableSequence(adder, _t, adder)

parallel_chain = RunnableParallel(a=adder, b=adder)

s = RunnableSequence(parallel_chain, adder)


def _f(x):
    return f"({x})"


surround = RunnableLambda(_f)

surround_thrice = surround | surround | surround

parallel_double_surround = RunnablePassthrough() | {
    "a": surround | surround,
    "b": surround | surround,
}
