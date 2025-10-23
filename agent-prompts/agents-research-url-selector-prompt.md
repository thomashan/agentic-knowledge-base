Task: Rate URL relevance for building a knowledge base on "{topic}"

Scoring Guide (0-10):
- 9-10: Official documentation, encyclopedias, academic papers, authoritative sources
- 7-8: Quality articles, reputable news, technical blogs with expertise
- 4-6: Tangentially related, partial information, less authoritative
- 1-3: Barely related, entertainment, social media, promotional content
- 0: Completely irrelevant, broken links, fictional content

{url_list_section}

Requirements:
1. Output ONLY valid JSON - no other text
2. Use exact URLs without escaping (correct: https://example.com/page not https:\/\/example.com\/page)
3. Rate each URL based on its content summary and relevance to "{topic}"
4. Keep rationales under 15 words

Output format:
```
[
{{"url": "https://example.com/page1", "relevance": "10", "rationale": "Official documentation with comprehensive coverage"}},
{{"url": "https://example.com/page2", "relevance": "3", "rationale": "Entertainment site, not knowledge-focused"}}
]
```
