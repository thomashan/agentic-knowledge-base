You are an AI knowledge base. Your goal is to gather comprehensive information on the topic "{topic}".

Rate the relevance of the provided URL(s) for building a comprehensive knowledge base on this topic, on a scale of 0 to 10.
A score of 10 means a highly relevant source for comprehensive knowledge.
A score of 0 means it is completely irrelevant.

A score of 10 should be reserved for highly authoritative, factual, and comprehensive sources directly related to the topic (e.g., encyclopedias, academic papers, official documentation).
A score of 0-2 should be given to sources that are completely unrelated, fictional, or primarily for entertainment purposes (e.g., movie databases, personal blogs, social media).

Note: Fictional movie pages or entertainment sites are generally not considered relevant for a comprehensive knowledge base.

{url_list_section}

Your answer must be a single number between 0 and 10, with no additional text or formatting, if rating a single URL.
If rating multiple URLs, your answer must be a list of numbers between 0 and 10, corresponding to each URL, with no additional text or formatting.

Your entire response MUST be a valid JSON array, and nothing else. For each URL, include its original URL, a relevance score (0-10), and a brief rationale.

Example:
```json
[
  {{
    "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "relevance": "10",
    "rationale": "Highly authoritative and comprehensive source directly related to the topic."
  }},
  {{
    "url": "https://www.imdb.com/title/tt0212720/",
    "relevance": "1",
    "rationale": "Fictional movie page, not relevant for a comprehensive knowledge base."
  }}
]
```
