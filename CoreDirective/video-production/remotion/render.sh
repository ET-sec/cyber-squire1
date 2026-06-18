#!/usr/bin/env bash
#
# render.sh - Batch render all 19 CoreDirective video compositions.
#
# Usage: bash render.sh
#
# Output goes to ./out/ directory.
# Renders all 7 CertCards, 10 DidYouKnow facts, 1 DebtTracker, 1 YouTubeIntro.

set -euo pipefail

OUT_DIR="./out"
mkdir -p "$OUT_DIR"

echo "======================================"
echo "  CoreDirective Video Batch Renderer"
echo "======================================"
echo ""

COMPOSITIONS=(
  # 7 Cert Cards (5s each, 1080x1920)
  "CertCard-CASP"
  "CertCard-CCNA"
  "CertCard-AWS"
  "CertCard-SSCP"
  "CertCard-SecurityPlus"
  "CertCard-NetworkPlus"
  "CertCard-CC"
  # 10 DidYouKnow Facts (4s each, 1080x1920)
  "Fact-CyberJobs"
  "Fact-Salary"
  "Fact-Ransomware"
  "Fact-HumanError"
  "Fact-NoDegree"
  "Fact-CASPSalary"
  "Fact-BreachCost"
  "Fact-DoD8140"
  "Fact-FirstVirus"
  "Fact-AWSCloud"
  # 1 DebtTracker (6s, 1080x1920)
  "DebtTracker-Default"
  # 1 YouTubeIntro (5s, 1920x1080)
  "YouTubeIntro-Default"
)

TOTAL=${#COMPOSITIONS[@]}
COUNT=0

for COMP in "${COMPOSITIONS[@]}"; do
  COUNT=$((COUNT + 1))
  echo "[$COUNT/$TOTAL] Rendering: $COMP"
  npx remotion render src/index.ts "$COMP" "$OUT_DIR/$COMP.mp4" --log=error
  echo "  -> $OUT_DIR/$COMP.mp4"
  echo ""
done

echo "======================================"
echo "  All $TOTAL videos rendered!"
echo "  Output: $OUT_DIR/"
echo "======================================"
