from langchain_core.runnables import (
    RunnableLambda,
    RunnableParallel,
    RunnablePassthrough,
    RunnableSequence,
)

from .runnables import adder

# TODO: create a sequential adder;
# INFO: getting 'TypeError: 'int' object is not subscriptable'?
# What happens when you run adder after adder? (Hint transform)
_t: RunnableLambda[int, dict[str, int]] = RunnableLambda(
    lambda x: {"a": x, "b": x}, name="transform"
)

adder_chain = RunnableSequence(adder, _t, adder)

# TODO: create a sequential chain of adders (two in- and outputs)
parallel_chain = RunnableParallel(a=adder, b=adder)

# TODO: create a sequential chain with the following signature:
# f(a, b) -> c, and the following chain:
#   1. run the adder in parallel
#   2. run the adder, again, on the output of (1)
# INFO: build 'inside-out'; first build the parallel chain;
# then chain this again (as a sequence)
s = RunnableSequence(parallel_chain, adder)


# TODO: composing of runnables is also possible using LangChain Expression Language (LCEL)
# Compose a simple chain that adds parenthesis '()' around its input.
def _f(x):
    return f"({x})"


surround = RunnableLambda(_f)

surround_thrice = surround | surround | surround

# TODO: Create a parallel chain using LCEL
# (note that '|' can only be used to create a RunnableSequence from two runnables,
# I.e. dictionary is not a RunnableParallel object)
# LCEL with parallel
# INFO: (hint) use 'RunnablePassthrough'
parallel_double_surround = RunnablePassthrough() | {
    "a": surround | surround,
    "b": surround | surround,
}
