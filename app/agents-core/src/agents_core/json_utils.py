import json
import re
from typing import Any


def to_json_object(llm_response: str) -> Any:
    """
    Extracts a JSON object from a string that might be wrapped in markdown.
    """
    json_match = re.search(r"```json\n([\s\S]*?)\n```", llm_response)
    return json.loads(json_match.group(1)) if json_match else json.loads(llm_response)
