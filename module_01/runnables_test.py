import unittest

from langchain_core.runnables import Runnable

from .runnables import add_one_runnable, adder_runnable, greeter_runnable


class TestAddOne(unittest.TestCase):
    def test_add_one(self):
        x = 1
        want = x + 1
        assert add_one_runnable is not None, "runnable is 'None'"
        assert isinstance(add_one_runnable, Runnable), "not a runnable"
        self.assertEqual(add_one_runnable.invoke(x), want)


class TestAdder(unittest.TestCase):
    def test_addition(self):
        a = 2
        b = 7
        want = a + b
        assert adder_runnable is not None, "runnable is 'None'"
        self.assertEqual(adder_runnable.invoke({"a": a, "b": b}), want)


class TestGreeter(unittest.TestCase):
    def test_greeting(self):
        input = "World!"
        want = "Hello World!"
        assert greeter_runnable is not None
        assert isinstance(greeter_runnable, Runnable)
        self.assertEqual(greeter_runnable.invoke(input), want)


if __name__ == "__main__":
    unittest.main()
