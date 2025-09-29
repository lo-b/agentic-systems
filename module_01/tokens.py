import tiktoken

s = "Hello agentic world!"


def print_tokens(s: str) -> list[str]:
    enc = tiktoken.encoding_for_model("gpt-4")
    texts = enc.encode(s)
    tokens = enc.decode_tokens_bytes(texts)

    return [token.decode() for token in tokens]
