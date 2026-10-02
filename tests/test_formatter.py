from backend.response_formatter import clean_response


text = """
# Task Completed

**Step 1:** Open website

###### Result

| Name | Value |
| Test | 123 |
"""

print(clean_response(text))