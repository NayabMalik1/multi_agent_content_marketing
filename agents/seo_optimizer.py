from llm_helper import ask_llm

class SEOOptimizerAgent:
    name = "SEO Optimizer"

    def run(self, content: str, research: dict) -> dict:
        keywords = ", ".join(research.get("keywords", []))
        topic = research.get("outline", "").split("\n")[0].replace("#", "").strip()

        prompt = f"""
You are an expert SEO specialist.
Given this blog content (HTML), optimize it fully.

CONTENT:
{content[:3000]}

PRIMARY KEYWORDS: {keywords}
TOPIC: {topic}

Your tasks:
1. Write an SEO meta title (max 60 chars).
2. Write an SEO meta description (max 160 chars).
3. Add 3–5 internal link placeholders like <a href="/related-topic">anchor text</a> naturally in the content.
4. Ensure keyword density is natural (not stuffed).
5. Add schema-friendly alt text suggestions for images.
6. Return the improved HTML content with links added.

Return ONLY valid JSON with keys:
- meta_title (string)
- meta_description (string)
- optimized_content (string, full HTML body)
- alt_texts (list of strings)
"""
        raw = ask_llm(prompt)
        return self._parse(raw, content, topic, keywords)

    def _parse(self, raw: str, original: str, topic: str, keywords: str) -> dict:
        import json
        try:
            clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            return json.loads(clean)
        except Exception:
            return {
                "meta_title": topic[:60],
                "meta_description": f"Learn everything about {topic}. Expert guide covering best practices, tools, and strategies.",
                "optimized_content": original,
                "alt_texts": [f"Illustration of {topic}", f"{topic} diagram", f"{topic} example"]
            }
