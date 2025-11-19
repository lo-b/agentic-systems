from dotenv import load_dotenv
from runnables import greet

assert load_dotenv(), ".env file empty or not found"


def main():
    print("////////////////////////////// module_01 //////////////////////////////")
    print("===== RUNNABLES =====")
    print(greet("Agentic World!"))
    # ...


if __name__ == "__main__":
    main()
