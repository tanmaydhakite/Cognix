import re


def clean_response(text):
    if not text:
        return ""

    text = str(text)

    # Remove Markdown headings
    text = re.sub(r"^\s*#+\s*", "", text, flags=re.MULTILINE)

    # Remove bold / italic markers
    text = text.replace("**", "")
    text = text.replace("__", "")
    text = text.replace("`", "")

    # Replace Markdown table separators
    text = text.replace("|", " ")

    # Remove excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Remove leading/trailing spaces from each line
    lines = [line.strip() for line in text.splitlines()]

    return "\n".join(lines).strip()