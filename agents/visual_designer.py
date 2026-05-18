import os
import json
import requests
from llm_helper import ask_llm

UNSPLASH_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")

class VisualDesignerAgent:
    name = "Visual Designer"

    def run(self, content: str, research: dict) -> dict:
        """
        1. Uses LLM to suggest image concepts per section.
        2. Fetches free images from Unsplash API (or returns placeholder URLs).
        3. Returns image embed HTML snippets.
        """
        keywords = research.get("keywords", [])
        main_keyword = keywords[0] if keywords else "technology"

        prompt = f"""
You are a visual content designer.
Based on this blog topic keywords: {', '.join(keywords[:5])}

Suggest 3 image concepts that would best illustrate the content.
For each, give:
- A short descriptive search query (for stock photos)
- Where in the blog it should appear (intro, middle, conclusion)
- Alt text

Return ONLY valid JSON as a list of 3 objects with keys: query, placement, alt_text
"""
        raw = ask_llm(prompt)
        suggestions = self._parse_suggestions(raw, main_keyword)
        images = self._fetch_images(suggestions)
        html_embeds = self._build_html(images)
        return {"suggestions": suggestions, "images": images, "html_embeds": html_embeds}

    def _parse_suggestions(self, raw: str, fallback: str) -> list:
        try:
            clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(clean)
        except Exception:
            return [
                {"query": fallback, "placement": "intro", "alt_text": f"{fallback} overview"},
                {"query": f"{fallback} team", "placement": "middle", "alt_text": f"{fallback} in action"},
                {"query": f"{fallback} results", "placement": "conclusion", "alt_text": f"{fallback} success"}
            ]

    def _fetch_images(self, suggestions: list) -> list:
        images = []
        for s in suggestions:
            url = self._unsplash_fetch(s["query"]) or self._placeholder(s["query"])
            images.append({**s, "url": url})
        return images

    def _unsplash_fetch(self, query: str) -> str:
        if not UNSPLASH_KEY:
            return ""
        try:
            r = requests.get(
                "https://api.unsplash.com/search/photos",
                params={"query": query, "per_page": 1, "orientation": "landscape"},
                headers={"Authorization": f"Client-ID {UNSPLASH_KEY}"},
                timeout=8
            )
            data = r.json()
            results = data.get("results", [])
            if results:
                return results[0]["urls"]["regular"]
        except Exception:
            pass
        return ""

    def _placeholder(self, query: str) -> str:
        encoded = query.replace(" ", "+")
        return f"https://source.unsplash.com/800x400/?{encoded}"

    def _build_html(self, images: list) -> str:
        parts = []
        for img in images:
            parts.append(
                f'<figure style="margin:2rem 0;text-align:center;">'
                f'<img src="{img["url"]}" alt="{img["alt_text"]}" '
                f'style="max-width:100%;border-radius:8px;box-shadow:0 4px 16px rgba(0,0,0,0.12);" />'
                f'<figcaption style="color:#666;font-size:0.875rem;margin-top:0.5rem;">'
                f'{img["alt_text"]}</figcaption></figure>'
            )
        return "\n".join(parts)
