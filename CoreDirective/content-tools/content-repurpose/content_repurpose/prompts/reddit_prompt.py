"""Reddit prompt template."""

from content_repurpose.config import ANTI_SLOP_RULES


def get_reddit_prompt(content: str, brand: str, cta: str, tone: str, subreddits: list[str]) -> str:
    subreddit_list = ", ".join(subreddits)
    return f"""You are writing a Reddit post based on content from "{brand}".
Your writing tone: {tone}

SOURCE CONTENT:
{content}

TASK: Create a Reddit post from this content.

REQUIREMENTS:
- Suggest 2-3 subreddits where this would fit best. Choose from: {subreddit_list}
- Write a clear, specific post title that would get clicks on Reddit (not clickbait, just clear value).
- The post body should be value-first. Detailed. Helpful. Like you're genuinely trying to help someone in the community.
- Casual community-member tone. You're a person sharing what you've learned, not promoting anything.
- NO links anywhere in the post body. Reddit communities downvote self-promotion.
- End the post with a genuine question that invites discussion and personal experiences.
- After the main post, write a suggested follow-up comment that could naturally include a link to the original content. This is separate from the post body.

FORMAT YOUR OUTPUT EXACTLY LIKE THIS:

# Reddit Post

**Suggested Subreddits:**
[list subreddits]

**Title:**
[post title]

**Post Body:**
[full post text]

---

**Suggested Follow-up Comment:**
[a natural comment you could post later that includes a link reference]

{ANTI_SLOP_RULES}

Write like you actually participate in these communities. No marketing voice.
Be genuinely helpful. Share specifics, not vague advice."""
