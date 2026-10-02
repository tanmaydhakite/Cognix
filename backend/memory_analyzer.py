import json

from google import genai
from google.genai import types


class MemoryAnalyzer:

    def __init__(self, client, model):

        self.client = client
        self.model = model

        self.system_instruction = """
You are the memory analyzer for TaskPilot AI.

Your job is to decide whether a user's message contains
useful personal information that should be remembered.

SAVE information when it is likely to be useful in future
conversations.

Examples of information worth remembering:

- Important appointments
- Interview dates or times
- Meeting information
- User preferences
- Favorite programming languages
- Important personal plans
- Repeated preferences
- Long-term goals
- Important facts the user explicitly provides

DO NOT save:

- Temporary calculations
- General questions
- General knowledge
- Normal task requests
- Casual conversation
- Information that is not useful later

Return ONLY valid JSON.

If the information should be remembered:

{
    "should_save": true,
    "key": "short_descriptive_key",
    "value": "information_to_remember"
}

If the information should NOT be remembered:

{
    "should_save": false,
    "key": "",
    "value": ""
}

Rules:

1. Use a short descriptive key.
2. Use lowercase snake_case for keys.
3. Keep the value concise but preserve important details.
4. Never invent information.
5. Only extract information actually present in the user's message.
"""


    def analyze(self, user_input):

        response = self.client.models.generate_content(
            model=self.model,
            contents=user_input,
            config=types.GenerateContentConfig(
                system_instruction=self.system_instruction,
                response_mime_type="application/json"
            )
        )

        try:

            result = json.loads(response.text)

            return result

        except Exception:

            return {
                "should_save": False,
                "key": "",
                "value": ""
            }


# --------------------------------------------------
# Test
# --------------------------------------------------

if __name__ == "__main__":

    import os
    from dotenv import load_dotenv

    load_dotenv()

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY is not set in the .env file"
        )

    client = genai.Client(
        api_key=api_key
    )

    analyzer = MemoryAnalyzer(
        client,
        "gemini-3.5-flash-lite"
    )

    test_messages = [
        "My Python interview is tomorrow at 10 AM.",
        "I prefer Python for coding.",
        "What is 25 multiplied by 40?",
        "Show me my tasks."
    ]

    for message in test_messages:

        print("\nUser:")
        print(message)

        result = analyzer.analyze(message)

        print("Memory analysis:")
        print(result)