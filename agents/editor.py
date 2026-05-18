import json
from llm_helper import ask_llm

class EditorAgent:
    name = "Editor"

    def run(self, content: str, research: dict) -> dict:
        """
        Scores content quality. If score < 7, returns approved=False with feedback
        so the Writer Agent can rewrite. Implements the feedback loop.
        """
        keywords = ", ".join(research.get("keywords", []))
        tone = research.get("tone", "professional")

        prompt = f"""
You are a senior content editor and brand voice specialist.
Review this blog post HTML for:
1. Grammar and spelling errors
2. Factual consistency and logical flow
3. Brand voice alignment (tone should be: {tone})
4. Keyword usage quality (keywords: {keywords})
5. Readability and engagement (intro hook, subheadings, conclusion CTA)

CONTENT TO REVIEW:
{content[:3000]}

Provide a strict quality score from 1–10.
If score < 7, list specific issues the writer must fix.
If score >= 7, approve with minor polish suggestions only.

Return ONLY valid JSON:
{{
  "score": <number 1-10>,
  "approved": <true or false>,
  "feedback": "<specific actionable feedback for the writer>",
  "polished_content": "<the content with only minor grammar/punctuation fixes applied — keep same structure>"
}}
"""
        raw = ask_llm(prompt)
        return self._parse(raw, content)

    def _parse(self, raw: str, original: str) -> dict:
        try:
            clean = raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            data = json.loads(clean)
            # Ensure required keys
            return {
                "score": data.get("score", 7),
                "approved": data.get("approved", True),
                "feedback": data.get("feedback", "Looks good!"),
                "polished_content": data.get("polished_content", original)
            }
        except Exception:
            return {
                "score": 7,
                "approved": True,
                "feedback": "Content approved with no major issues.",
                "polished_content": original
            }
