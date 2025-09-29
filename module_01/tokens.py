import tiktoken

# TODO: use the tiktoken encoder to the string 'Hello agentic world!'
# Q: Taking the 'gpt-4' model, how many tokens does the string consist of?
s = "Hello agentic world!"


def print_tokens(s: str) -> list[str]:
    enc = tiktoken.encoding_for_model("gpt-4")
    texts = enc.encode(s)
    tokens = enc.decode_tokens_bytes(texts)

    return [token.decode() for token in tokens]
