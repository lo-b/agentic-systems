from langchain_core.runnables import RunnableLambda


# INFO: Sample function, imported and used in `./module_01/main.py`.
def greet(name):
    return "Hello " + name
