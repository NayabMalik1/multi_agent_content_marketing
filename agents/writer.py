from llm_helper import ask_llm

class WriterAgent:
    name = "Writer"

    def run(self, research: dict, feedback: str = "") -> str:
        """Write a full blog post from research outline. Accepts optional editor feedback."""
        outline = research.get("outline", "")
        keywords = ", ".join(research.get("keywords", []))
        audience = research.get("audience", "general audience")
        tone = research.get("tone", "professional")

        feedback_block = ""
        if feedback:
            feedback_block = f"""
EDITOR FEEDBACK TO ADDRESS:
{feedback}
Please fix all issues mentioned above before writing.
"""

        prompt = f"""
You are an expert blog writer.
{feedback_block}
Write a complete, engaging blog post based on this outline:

{outline}

Requirements:
- Target audience: {audience}
- Tone: {tone}
- Naturally include these keywords: {keywords}
- Length: 800–1200 words
- Use proper HTML tags: <h1>, <h2>, <p>, <ul>, <li>, <strong>, <em>
- Add a compelling intro and strong CTA conclusion
- Do NOT include <html>, <head>, or <body> tags — only the content body

Return ONLY the HTML content, no markdown code fences.
"""
        return ask_llm(prompt)
