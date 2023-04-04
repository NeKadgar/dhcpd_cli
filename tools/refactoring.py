import re


def normalize_whitespaces(text: str) -> str:
    # Replace all consecutive whitespace characters with a single space
    return re.sub(r'\s+', ' ', text.strip())


def add_necessary_spaces(text: str) -> str:
    # Adds space before '{' and '}' and after ';'
    text = re.sub(r"(\w|\W)(\{ |\})", r"\1 \2", text)
    text = re.sub(r"(\;)(\w)", r"\1 \2", text)
    return text


def normalize_text(text: str) -> str:
    return add_necessary_spaces(
        normalize_whitespaces(text)
    )
