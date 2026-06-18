---
name: python-helper
description: Python coding assistance, debugging, script templates, and common patterns
---

# Python Helper

## When to Use
User asks for Python help, debugging, script writing, or coding questions.

## Script Templates

**API request with error handling:**
```python
import requests

def api_call(url, headers=None, params=None):
    try:
        resp = requests.get(url, headers=headers, params=params, timeout=30)
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.Timeout:
        print(f"Timeout: {url}")
    except requests.exceptions.HTTPError as e:
        print(f"HTTP {e.response.status_code}: {e.response.text[:200]}")
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    return None
```

**File processing:**
```python
from pathlib import Path
import json, csv

# Read JSON
data = json.loads(Path("file.json").read_text())

# Read CSV
with open("file.csv") as f:
    rows = list(csv.DictReader(f))

# Write JSON
Path("out.json").write_text(json.dumps(data, indent=2))

# Process files in directory
for f in Path("./data").glob("*.csv"):
    print(f.name, f.stat().st_size)
```

**Web scraping:**
```python
import requests
from bs4 import BeautifulSoup

resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
soup = BeautifulSoup(resp.text, "html.parser")
items = soup.select("div.item h2")  # CSS selector
texts = [item.get_text(strip=True) for item in items]
```

**Data transformation with pandas:**
```python
import pandas as pd

df = pd.read_csv("data.csv")
df = df.dropna(subset=["key_col"])              # drop rows missing key
df["date"] = pd.to_datetime(df["date_str"])     # parse dates
df["total"] = df["qty"] * df["price"]           # computed column
summary = df.groupby("category")["total"].agg(["sum", "mean", "count"])
summary.to_csv("summary.csv")
```

## Common Patterns

**List comprehension:**
```python
# Filter + transform
results = [x.strip().lower() for x in items if x and len(x) > 2]

# Nested
flat = [cell for row in matrix for cell in row]

# Dict comprehension
lookup = {item["id"]: item["name"] for item in records}
```

**Error handling:**
```python
try:
    result = risky_operation()
except (ValueError, KeyError) as e:
    logger.error(f"Failed: {e}")
    result = default_value
except Exception as e:
    logger.exception(f"Unexpected error: {e}")
    raise
finally:
    cleanup()
```

**f-strings:**
```python
f"{value:.2f}"          # 2 decimal places
f"{value:,}"            # thousands separator
f"{name:>20}"           # right-align, 20 chars
f"{pct:.1%}"            # percentage (0.156 -> "15.6%")
f"{dt:%Y-%m-%d %H:%M}" # datetime formatting
```

## Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate    # macOS/Linux
pip install -r requirements.txt
pip freeze > requirements.txt
```

## Debugging Tips
- `breakpoint()` -- drops into pdb (Python 3.7+)
- `python3 -m pdb script.py` -- run with debugger
- `print(f"{var=}")` -- Python 3.8+ debug print (shows var name + value)
- `import traceback; traceback.print_exc()` -- print full traceback in except block
- `type(obj)`, `dir(obj)`, `vars(obj)` -- inspect objects
