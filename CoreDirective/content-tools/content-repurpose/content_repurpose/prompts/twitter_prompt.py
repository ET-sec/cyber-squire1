"""X/Twitter thread prompt template."""

from content_repurpose.config import ANTI_SLOP_RULES


def get_twitter_prompt(content: str, brand: str, cta: str, tone: str) -> str:
    return f"""You are an X/Twitter thread writer for the brand "{brand}".
Your writing tone: {tone}

SOURCE CONTENT:
{content}

TASK: Create a 7-tweet thread from this content.

REQUIREMENTS:
- Tweet 1: Strong hook that makes people want to read the thread. Include a thread indicator like "(thread)" or an arrow.
- Tweets 2-6: Core content broken into atomic points. Each tweet must stand completely on its own. Someone should get value from any single tweet even without context.
- Tweet 7: CTA tweet. {cta}
- Every tweet MUST be under 280 characters. Count carefully.
- Use "1/", "2/", etc. numbering at the start of each tweet.
- NO hashtags in tweets 1-6. Only include 2-3 hashtags in the final tweet (tweet 7).
- NO emojis except sparingly (one per tweet max, and only if it adds clarity).
- Each tweet should flow into the next but also work independently.

FORMAT YOUR OUTPUT EXACTLY LIKE THIS:

# X/Twitter Thread

**1/**
[tweet text]

**2/**
[tweet text]

**3/**
[tweet text]

**4/**
[tweet text]

**5/**
[tweet text]

**6/**
[tweet text]

**7/**
[tweet text with hashtags]

{ANTI_SLOP_RULES}

Write like someone with real opinions on X. Crisp. Direct. No filler.
Each tweet must earn its spot in the thread."""
