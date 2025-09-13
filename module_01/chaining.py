from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnableSequence

from .runnables import adder

# TODO: create a sequential adder;
# INFO: getting 'TypeError: 'int' object is not subscriptable'?
# What happens when you run adder after adder? (Hint transform)
_t: RunnableLambda[int, dict[str, int]] = RunnableLambda(
    lambda x: {"a": x, "b": x}, name="transform"
)

adder_chain = RunnableSequence(adder, _t, adder)
parallel_chain = RunnableParallel(a=adder, b=adder)
s = RunnableSequence(parallel_chain, adder)
