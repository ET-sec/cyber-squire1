"""Platform-specific prompt templates."""

from content_repurpose.prompts.tiktok_prompt import get_tiktok_prompt
from content_repurpose.prompts.linkedin_prompt import get_linkedin_prompt
from content_repurpose.prompts.twitter_prompt import get_twitter_prompt
from content_repurpose.prompts.reddit_prompt import get_reddit_prompt
from content_repurpose.prompts.youtube_prompt import get_youtube_prompt
from content_repurpose.prompts.shorts_prompt import get_shorts_prompt

__all__ = [
    "get_tiktok_prompt",
    "get_linkedin_prompt",
    "get_twitter_prompt",
    "get_reddit_prompt",
    "get_youtube_prompt",
    "get_shorts_prompt",
]
