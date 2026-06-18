"""LinkedIn prompt template."""

from content_repurpose.config import ANTI_SLOP_RULES


def get_linkedin_prompt(content: str, brand: str, cta: str, tone: str) -> str:
    return f"""You are a LinkedIn content writer for the brand "{brand}".
Your writing tone: {tone}

SOURCE CONTENT:
{content}

TASK: Create one LinkedIn post from this content.

REQUIREMENTS:
- Pattern-interrupt opener. NO "I'm excited to announce" or "I've been thinking about". Start with a bold statement, surprising stat, or contrarian take.
- 150-300 words total.
- Professional but human. You're a person posting, not a brand account.
- Include 1-2 specific data points, stats, or concrete examples from the source content.
- End with a genuine question that invites discussion. Not a rhetorical throwaway.
- Line breaks every 1-2 sentences. LinkedIn rewards readability.
- Max 3 hashtags at the very end.
- Max 2-3 emojis total, used sparingly (one near the start, one near the end is fine).
- CTA woven naturally into the post: {cta}

FORMAT YOUR OUTPUT EXACTLY LIKE THIS:

# LinkedIn Post

[Full post text with line breaks, ready to copy-paste into LinkedIn]

{ANTI_SLOP_RULES}

Write like a real person sharing a professional insight. Not a thought leader performing.
Short paragraphs. Real talk. No buzzword soup."""
