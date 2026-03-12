#!/usr/bin/env bash
# Smoke tests for md2gdoc conversion.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
MD2GDOC="${REPO_DIR}/md2gdoc"
FIXTURE="${REPO_DIR}/tests/fixtures/sample-design-doc.md"

TMPDIR="$(mktemp -d)"
trap 'rm -rf "$TMPDIR"' EXIT

echo "Running md2gdoc smoke tests..."

# Test 1: Basic conversion
echo -n "  [1/5] Basic conversion... "
"$MD2GDOC" "$FIXTURE" -o "$TMPDIR/basic.docx"
if [[ -f "$TMPDIR/basic.docx" && $(stat -f%z "$TMPDIR/basic.docx" 2>/dev/null || stat -c%s "$TMPDIR/basic.docx") -gt 0 ]]; then
    echo "OK"
else
    echo "FAIL: output file missing or empty"
    exit 1
fi

# Test 2: Default output name (input.md → input.docx)
echo -n "  [2/5] Default output name... "
cp "$FIXTURE" "$TMPDIR/my-doc.md"
(cd "$TMPDIR" && "$MD2GDOC" my-doc.md)
if [[ -f "$TMPDIR/my-doc.docx" ]]; then
    echo "OK"
else
    echo "FAIL: expected my-doc.docx"
    exit 1
fi

# Test 3: Help flag
echo -n "  [3/5] Help flag... "
HELP_OUTPUT="$("$MD2GDOC" --help 2>&1)"
if echo "$HELP_OUTPUT" | grep -q "Usage:"; then
    echo "OK"
else
    echo "FAIL: help output missing Usage"
    exit 1
fi

# Test 4: Missing input file
echo -n "  [4/5] Missing input error... "
if "$MD2GDOC" "$TMPDIR/nonexistent.md" -o "$TMPDIR/out.docx" 2>/dev/null; then
    echo "FAIL: should have exited with error"
    exit 1
else
    echo "OK"
fi

# Test 5: Output is valid DOCX (zip with word/document.xml)
echo -n "  [5/5] Valid DOCX structure... "
if python3 -c "
import zipfile, sys
with zipfile.ZipFile('$TMPDIR/basic.docx') as z:
    sys.exit(0 if 'word/document.xml' in z.namelist() else 1)
" 2>/dev/null; then
    echo "OK"
else
    echo "FAIL: not a valid DOCX file"
    exit 1
fi

echo ""
echo "All tests passed."
