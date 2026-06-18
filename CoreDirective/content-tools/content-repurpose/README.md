# content-repurpose

CLI tool that takes one piece of long-form content and generates platform-optimized versions for TikTok, LinkedIn, X/Twitter, Reddit, YouTube metadata, and YouTube Shorts.

Powered by Claude (Anthropic API).

## Install

```bash
cd builds/content-repurpose
pip install -e .
```

## Setup

Set your Anthropic API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

```bash
# From a YouTube script
content-repurpose --script ./scripts/ep1.md

# From a topic
content-repurpose --topic "Why CASP+ is the most underrated cybersecurity certification"

# From a transcript
content-repurpose --transcript ./transcripts/ep1.txt --output ./content/ep1/

# From any text file
content-repurpose --text ./drafts/blog-post.md

# With overrides
content-repurpose --topic "Zero trust is broken" --brand "CoreDirective" --tone "blunt, technical" --output ./out/
```

## Flags

| Flag | Description | Default |
|------|-------------|---------|
| `--script <path>` | YouTube script markdown | - |
| `--transcript <path>` | Transcript text file | - |
| `--text <path>` | Any long-form text file | - |
| `--topic <string>` | Generate from a topic | - |
| `--brand <name>` | Brand name | CoreDirective |
| `--cta <string>` | Call to action | Follow for more cybersecurity content |
| `--output <dir>` | Output directory | ./output/ |
| `--tone <string>` | Writing tone | direct, confident, slightly irreverent |
| `--config <path>` | Path to config.yaml | auto-detected |

## Output

All files are written to the output directory:

```
output/
  tiktok_scripts.md      # 3 TikTok script variations
  linkedin_post.md       # LinkedIn post
  twitter_thread.md      # 7-tweet X/Twitter thread
  reddit_post.md         # Reddit post + suggested subreddits
  youtube_metadata.md    # Titles, description, tags, thumbnails
  youtube_shorts.md      # 2 YouTube Shorts scripts
```

## Configuration

Edit `config.yaml` to set defaults:

```yaml
brand: "CoreDirective"
cta: "Follow for more cybersecurity content"
tone: "direct, confident, slightly irreverent, no corporate speak"
model: "claude-sonnet-4-5-20250929"
output_dir: "./output"

platforms:
  tiktok: true
  linkedin: true
  twitter: true
  reddit: true
  youtube: true
  shorts: true
```

Set any platform to `false` to skip it during generation.
