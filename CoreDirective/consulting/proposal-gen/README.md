# proposal-gen

Professional consulting proposal PDF generator for CoreDirective. Takes a company name and their need, uses Claude AI to generate contextual content, and outputs a branded multi-page PDF.

## Install

```bash
cd builds/proposal-gen
pip install -e .
```

## Setup

Export your Anthropic API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

```bash
# Basic usage
proposal-gen --company "Acme Corp" --need "SOC2 Type II compliance audit"

# With all options
proposal-gen \
  --company "Acme Corp" \
  --contact "Jane Smith" \
  --need "SOC2 Type II compliance audit" \
  --budget "8000-12000" \
  --theme dark \
  --output ./output/acme_soc2.pdf

# Skip AI generation (uses templates only)
proposal-gen --company "TestCo" --need "security assessment" --no-ai
```

## Flags

| Flag | Required | Default | Description |
|------|----------|---------|-------------|
| `--company` | Yes | - | Client company name |
| `--contact` | No | - | Primary contact name |
| `--need` | Yes | - | What the client needs |
| `--budget` | No | - | Budget range (adjusts pricing display) |
| `--theme` | No | light | PDF theme: `light` or `dark` |
| `--output` | No | `./output/{company}_proposal.pdf` | Output file path |
| `--config` | No | `./config.yaml` | Config file override |
| `--no-ai` | No | false | Skip Claude API, use template text |

## Service Type Detection

The tool auto-detects the service type from the `--need` text:

- **SOC2 Compliance** - "soc2", "compliance audit", "type ii"
- **Security Assessment** - "security assessment", "pentest", "vulnerability"
- **n8n Automation** - "n8n", "automation", "workflow", "automate"
- **Cloud Security** - "aws", "cloud security", "cloud hardening"
- **vCISO Retainer** - "vciso", "ciso", "retainer"
- **Incident Response** - "incident response", "ir plan", "tabletop"

Each type generates appropriate phases, deliverables, and pricing.

## PDF Output

6-page professional proposal:

1. **Cover** - Branding, client name, consultant credentials, date
2. **Executive Summary** - AI-generated summary of the engagement
3. **Scope of Work** - Phased approach with deliverables and timelines
4. **Qualifications** - Certifications, stats, relevance framing
5. **Investment** - Pricing table, payment terms, inclusions
6. **Next Steps** - Contact info, proposed start date, signature lines

## Configuration

Edit `config.yaml` to change consultant info, pricing, or banned words. The Python defaults in `config.py` work without the YAML file.

## Themes

- **Light** - White background, dark text, green accents
- **Dark** - Near-black background, light text, green accents

Both use Helvetica, US Letter size, 1-inch margins.
