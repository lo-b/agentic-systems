from dotenv import load_dotenv

# INFO: imports the 'greet' function from 'runnables.py'
from runnables import greet

# Check prescence of .env file and load all variables
assert load_dotenv(), ".env file empty or not found"


def main():
    print("////////////////////////////// module_01 //////////////////////////////")
    print("===== RUNNABLES =====")
    print(greet("Agentic World!"))
    # ...


if __name__ == "__main__":
    main()
