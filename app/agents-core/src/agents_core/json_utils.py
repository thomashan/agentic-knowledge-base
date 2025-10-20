import json
import re


def to_json_object(llm_response: str) -> list[dict[str, str]]:
    """
    Extracts a JSON object from a string that might be wrapped in markdown.
    """
    json_match = re.search(r"```(json|python)\n([\s\S]*?)\n```", llm_response, re.DOTALL)
    if json_match:
        return json.loads(json_match.group(2))
    return json.loads(llm_response)
