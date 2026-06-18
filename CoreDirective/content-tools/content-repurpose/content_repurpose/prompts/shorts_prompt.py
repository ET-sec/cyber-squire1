"""YouTube Shorts prompt template."""

from content_repurpose.config import ANTI_SLOP_RULES


def get_shorts_prompt(content: str, brand: str, cta: str, tone: str) -> str:
    return f"""You are a YouTube Shorts script writer for the brand "{brand}".
Your writing tone: {tone}

SOURCE CONTENT:
{content}

TASK: Create 2 YouTube Shorts script variations from this content. Each script must be under 58 seconds (~145 words max).

These are similar to TikTok scripts but slightly more polished since YouTube Shorts has a broader demographic. Still conversational. Still punchy. But a touch more substance.

VARIATION 1: Lead with the most surprising or counterintuitive insight from the content. Make the viewer feel like they just learned something they should have known.

VARIATION 2: Frame it as a practical tip or action item. "Do this, not that" energy. Give the viewer something they can use immediately.

STRUCTURE FOR EACH VARIATION:
- **Hook** (1-3 seconds): First sentence must stop the scroll. NO "hey guys" or generic intros.
- **Body** (15-45 seconds): Core content, spoken word delivery, clear and direct.
- **CTA** (2-3 seconds): {cta}
- **Title**: Short title for the Shorts video (under 100 characters).
- **Description**: One-line description with 3-5 hashtags.

FORMAT YOUR OUTPUT EXACTLY LIKE THIS:

# YouTube Shorts Scripts

## Variation 1: Surprise Insight

**Title:**
[short title]

**Hook:**
[hook text]

**Body:**
[body text]

**CTA:**
[cta text]

**Description:**
[one-line description with hashtags]

---

## Variation 2: Practical Tip

**Title:**
[short title]

**Hook:**
[hook text]

**Body:**
[body text]

**CTA:**
[cta text]

**Description:**
[one-line description with hashtags]

{ANTI_SLOP_RULES}

Write like someone who actually makes Shorts. Not a scriptwriter who's never posted a video.
Keep it tight. Every sentence earns its spot."""
