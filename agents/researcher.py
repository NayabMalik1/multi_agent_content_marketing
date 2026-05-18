import os
import json
import requests
from llm_helper import ask_llm

SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")

class ResearcherAgent:
    name = "Researcher"

    def run(self, topic: str) -> dict:
        """
        1. Fetch real search results (SerpAPI free tier) OR fallback mock.
        2. Use LLM to build keyword list + detailed outline.
        """
        serp_results = self._fetch_serp(topic)
        prompt = f"""
You are an expert content researcher.
Topic: "{topic}"
Top search snippets from the web:
{serp_results}

Your tasks:
1. List 10 high-value SEO keywords (comma-separated).
2. Write a detailed blog outline with H1, 5-7 H2 sections (each with 2-3 bullet sub-points).
3. Suggest target audience and content tone.

Return ONLY valid JSON with keys: keywords (list), outline (string), audience (string), tone (string).
"""
        raw = ask_llm(prompt)
        return self._parse(raw, topic)

    def _fetch_serp(self, topic: str) -> str:
        if not SERPAPI_KEY:
            return self._mock_serp(topic)
        try:
            url = "https://serpapi.com/search"
            params = {"q": topic, "api_key": SERPAPI_KEY, "num": 5, "engine": "google"}
            r = requests.get(url, params=params, timeout=10)
            data = r.json()
            snippets = []
            for item in data.get("organic_results", [])[:5]:
                snippets.append(f"- {item.get('title','')}: {item.get('snippet','')}")
            return "\n".join(snippets) if snippets else self._mock_serp(topic)
        except Exception:
            return self._mock_serp(topic)

    def _mock_serp(self, topic: str) -> str:
        return (
            f"- Top guide to {topic}: everything you need to know in 2024\n"
            f"- {topic} best practices and strategies for success\n"
            f"- How {topic} is transforming industries worldwide\n"
            f"- Beginner to advanced: mastering {topic}\n"
            f"- {topic} trends, tools, and future predictions"
        )

    def _parse(self, raw: str, topic: str) -> dict:
        try:
            clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(clean)
        except Exception:
            return {
                "keywords": [topic, f"{topic} guide", f"best {topic}", f"{topic} tips", f"{topic} 2024"],
                "outline": f"# The Complete Guide to {topic}\n## Introduction\n## Key Concepts\n## Best Practices\n## Tools & Resources\n## Case Studies\n## Conclusion",
                "audience": "General professional audience",
                "tone": "Informative and engaging"
            }
