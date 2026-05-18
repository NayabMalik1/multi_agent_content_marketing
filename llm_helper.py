"""
llm_helper.py — Smart LLM router for ContentFlow AI
=====================================================
Priority order (all FREE):
  1. Gemini 1.5 Flash  — 1M tokens/day,  no credit card needed
  2. Groq (fallback)   — 100K tokens/day, ultra fast
  3. Mock              — hardcoded demo,  no key needed

Auto-retry on rate limit with exponential backoff.
Automatically switches provider if one is rate-limited.
"""

import os
import time
import json

# ── Which provider to try first ───────────────────────────────────────────────
def _get_provider_order() -> list:
    """Returns list of available providers in priority order."""
    order = []
    if os.getenv("GEMINI_API_KEY"):
        order.append("gemini")
    if os.getenv("GROQ_API_KEY"):
        order.append("groq")
    if os.getenv("OPENAI_API_KEY"):
        order.append("openai")
    if not order:
        order.append("mock")
    return order


# ── Main entry point ─────────────────────────────────────────────────────────
def ask_llm(prompt: str, json_mode: bool = False) -> str:
    """
    Call the best available LLM.
    Automatically falls back to next provider on rate limit or error.
    """
    providers = _get_provider_order()

    last_error = None
    for provider in providers:
        try:
            if provider == "gemini":
                return _call_gemini(prompt, json_mode)
            elif provider == "groq":
                return _call_groq(prompt, json_mode)
            elif provider == "openai":
                return _call_openai(prompt, json_mode)
            else:
                return _mock(prompt)
        except RateLimitError as e:
            last_error = e
            print(f"[llm_helper] {provider} rate limited — trying next provider...")
            continue
        except Exception as e:
            last_error = e
            print(f"[llm_helper] {provider} failed: {e} — trying next provider...")
            continue

    # All providers failed — use mock as last resort
    print(f"[llm_helper] All providers failed. Last error: {last_error}. Using mock.")
    return _mock(prompt)


# ── Custom exception ─────────────────────────────────────────────────────────
class RateLimitError(Exception):
    pass


# ── Gemini 1.5 Flash (PRIMARY — 1M tokens/day free) ─────────────────────────
def _call_gemini(prompt: str, json_mode: bool = False) -> str:
    try:
        import google.generativeai as genai
    except ImportError:
        raise Exception("google-generativeai not installed. Run: pip install google-generativeai")

    api_key = os.getenv("GEMINI_API_KEY", "")
    if not api_key:
        raise Exception("GEMINI_API_KEY not set")

    if json_mode:
        prompt += "\n\nIMPORTANT: Return ONLY a valid JSON object. No markdown, no explanation, no code fences."

    genai.configure(api_key=api_key)
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=genai.GenerationConfig(
            temperature=0.7,
            max_output_tokens=2048,
        ),
    )

    # Retry up to 3 times on transient errors
    for attempt in range(3):
        try:
            response = model.generate_content(prompt)
            text = response.text.strip()

            # Strip markdown fences if model added them
            if json_mode:
                import re
                text = re.sub(r"^```(?:json)?\s*", "", text)
                text = re.sub(r"\s*```$", "", text)
                text = text.strip()

            return text

        except Exception as e:
            err_str = str(e).lower()

            if "429" in str(e) or "quota" in err_str or "rate" in err_str or "resource_exhausted" in err_str:
                if attempt < 2:
                    wait = (attempt + 1) * 5
                    print(f"[Gemini] Rate limit — waiting {wait}s (attempt {attempt+1}/3)...")
                    time.sleep(wait)
                else:
                    raise RateLimitError(f"Gemini quota exceeded: {e}")

            elif "api key" in err_str or "invalid" in err_str or "permission" in err_str:
                raise Exception(
                    "Gemini API key invalid. "
                    "Get a free key at: aistudio.google.com/apikey"
                )
            else:
                if attempt < 2:
                    time.sleep(2)
                else:
                    raise Exception(f"Gemini error: {e}")


# ── Groq (FALLBACK — 100K tokens/day free) ───────────────────────────────────
def _call_groq(prompt: str, json_mode: bool = False) -> str:
    try:
        from groq import Groq
    except ImportError:
        raise Exception("groq not installed. Run: pip install groq")

    api_key = os.getenv("GROQ_API_KEY", "")
    if not api_key:
        raise Exception("GROQ_API_KEY not set")

    if json_mode:
        prompt += "\n\nIMPORTANT: Return ONLY a valid JSON object. No markdown, no explanation."

    client = Groq(api_key=api_key)

    # Try smaller model first to save tokens, then larger if needed
    models_to_try = [
        "llama-3.1-8b-instant",      # 100K/day, very fast, less tokens used
        "llama-3.3-70b-versatile",   # Higher quality but more tokens
        "mixtral-8x7b-32768",        # Alternative
    ]

    for model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=2000,
                temperature=0.7,
            )
            return response.choices[0].message.content

        except Exception as e:
            err_str = str(e).lower()
            if "429" in str(e) or "rate_limit" in err_str or "tokens per day" in err_str:
                print(f"[Groq] {model} rate limited — trying next model...")
                continue
            elif "model" in err_str and ("not found" in err_str or "decommissioned" in err_str):
                print(f"[Groq] {model} not available — trying next...")
                continue
            else:
                raise Exception(f"Groq error with {model}: {e}")

    raise RateLimitError(
        "All Groq models rate limited. Daily limit reached.\n"
        "Fix: Add GEMINI_API_KEY to .env (free at aistudio.google.com/apikey)"
    )


# ── OpenAI (OPTIONAL — paid) ─────────────────────────────────────────────────
def _call_openai(prompt: str, json_mode: bool = False) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        raise Exception("openai not installed. Run: pip install openai")

    api_key = os.getenv("OPENAI_API_KEY", "")
    if not api_key:
        raise Exception("OPENAI_API_KEY not set")

    if json_mode:
        prompt += "\n\nIMPORTANT: Return ONLY a valid JSON object. No markdown, no explanation."

    client = OpenAI(api_key=api_key)
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"} if json_mode else {"type": "text"},
            max_tokens=2000,
            temperature=0.7,
        )
        return response.choices[0].message.content
    except Exception as e:
        err_str = str(e).lower()
        if "429" in str(e) or "rate" in err_str:
            raise RateLimitError(f"OpenAI rate limited: {e}")
        elif "authentication" in err_str or "invalid" in err_str:
            raise Exception("OpenAI API key invalid. Check platform.openai.com")
        raise Exception(f"OpenAI error: {e}")


# ── Mock (DEMO — no key needed) ───────────────────────────────────────────────
def _mock(prompt: str) -> str:
    """Realistic hardcoded responses for demo/testing."""
    p = prompt.lower()

    if any(w in p for w in ["research", "outline", "keyword", "serp", "competitor"]):
        return json.dumps({
            "keywords": [
                "AI content marketing", "automated blogging",
                "SEO automation", "content pipeline", "AI writing tools",
            ],
            "search_volume": {
                "AI content marketing": 8100,
                "automated blogging": 2400,
                "SEO automation": 5400,
            },
            "outline": [
                "Introduction: The Content Marketing Challenge",
                "What Is AI-Powered Content Marketing?",
                "Key Benefits: Speed, Scale, and Quality",
                "How Multi-Agent Pipelines Work",
                "Real-World Use Cases and Results",
                "Getting Started: Tools and Best Practices",
                "Conclusion and Next Steps",
            ],
            "competitor_titles": [
                "How AI Is Transforming Content Creation in 2025",
                "The Future of Automated SEO Content",
            ],
            "content_gaps": [
                "ROI measurement for AI content tools",
                "Integration with existing CMS workflows",
            ],
        })

    if any(w in p for w in ["write", "draft", "blog", "article"]):
        return """## Introduction: The Content Marketing Challenge

In today's hyper-competitive digital landscape, businesses must produce **high-quality,
SEO-optimised content** at scale. Traditional workflows are slow, expensive, and
inconsistent — a single article can take 8–10 hours of skilled human labour.

## What Is AI-Powered Content Marketing?

AI-powered content marketing uses large language models and autonomous agents to research,
write, optimise, and publish content with minimal human intervention.

## Key Benefits: Speed, Scale, and Quality

- **10× faster**: What takes humans 9 hours completes in under 2 minutes
- **Consistent brand voice**: Every article follows your defined tone guidelines
- **Built-in SEO**: Keywords, meta tags, and links are optimised automatically
- **Cost reduction**: Up to 85% lower content production costs

## How Multi-Agent Pipelines Work

Each agent handles a specific stage. The Researcher gathers data. The Writer produces
the draft. The SEO Optimizer embeds keywords. The Editor checks quality.

## Real-World Use Cases

E-commerce brands use pipelines to generate product guides at scale.
SaaS companies automate their knowledge bases.

## Getting Started

1. Choose your LLM provider — Gemini is free, Groq is fast
2. Define your brand voice and SEO guidelines
3. Run your first pipeline and review the output

## Conclusion

AI multi-agent content pipelines deliver measurable ROI from day one."""

    if any(w in p for w in ["seo", "meta", "keyword", "schema"]):
        return json.dumps({
            "meta_title": "AI Content Marketing Pipeline: Automate Blogs 2025 | ContentFlow",
            "meta_description": (
                "Discover how AI multi-agent pipelines automate content marketing. "
                "Research, write, optimise, and publish 10x faster with 85% cost savings."
            ),
            "seo_keywords": [
                "AI content marketing", "automated blog writing",
                "SEO automation", "content pipeline AI", "multi-agent writing",
            ],
            "internal_links": [
                {"anchor": "AI writing tools",   "url": "/blog/ai-writing-tools"},
                {"anchor": "SEO best practices", "url": "/blog/seo-guide-2025"},
            ],
            "schema_markup": (
                '{"@context":"https://schema.org","@type":"Article",'
                '"headline":"AI Content Marketing Pipeline"}'
            ),
        })

    if any(w in p for w in ["edit", "grammar", "quality", "review", "score"]):
        return json.dumps({
            "score":            8,
            "approved":         True,
            "feedback":         "Content is clear and well-structured.",
            "corrections":      ["Improved transitions", "Reduced passive voice"],
            "polished_content": "",
        })

    if any(w in p for w in ["chart", "visual", "data", "graph"]):
        return json.dumps({
            "charts_count": 2,
            "charts":       ["bar_chart", "line_chart"],
        })

    return json.dumps({"status": "ok", "result": "Processed successfully"})