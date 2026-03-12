# md2gdoc

Convert Markdown to DOCX with Google Docs-friendly styling. Write in Markdown, upload to Google Drive, review as a native Google Doc.

## Why

Google Docs' "Paste from Markdown" produces clean results — Arial font, 1.15 line spacing, Roboto Mono for code. But you can't automate paste. This tool runs Pandoc with a reference template that matches Google Docs' styling, so the imported DOCX looks like you pasted it by hand.

## Install

```bash
# Prerequisites
brew install pandoc

# Clone and symlink
git clone https://github.com/edmondop/md2gdoc.git
ln -s "$(pwd)/md2gdoc/md2gdoc" /usr/local/bin/md2gdoc
```

## Usage

```bash
md2gdoc design-doc.md                        # → design-doc.docx
md2gdoc design-doc.md -o output.docx         # explicit output
md2gdoc design-doc.md --open                 # convert and open
md2gdoc design-doc.md -r my-template.docx    # custom reference template
```

## Features

- **Google Docs styling** — Arial 11pt, 1.15 line spacing, matching heading sizes
- **YAML frontmatter** — `title`, `author`, `date` become document metadata
- **GFM support** — tables, fenced code blocks, task lists
- **Embedded images** — PNG, JPEG, SVG (with automatic PNG fallback)
- **Inline code** — Roboto Mono in green (#188038), matching Google Docs rendering
- **Code blocks** — Roboto Mono 10pt, no background shading

## Custom Templates

The default template matches Google Docs styling. To use a custom template (e.g., company branding):

```bash
# Option 1: Per-command
md2gdoc doc.md -r ~/templates/company-reference.docx

# Option 2: User default (auto-detected)
mkdir -p ~/.config/md2gdoc
cp company-reference.docx ~/.config/md2gdoc/reference.docx
```

To rebuild the default template:

```bash
uv run build-reference.py
```

## How It Works

1. `build-reference.py` extracts Pandoc's default reference DOCX and modifies its styles to match Google Docs conventions
2. `md2gdoc` runs Pandoc with this reference template, GFM extensions, and YAML frontmatter support
3. The output DOCX uses native Word styles (`Heading 1`, `Normal`, etc.) that Google Docs recognizes on import

## Template Comparison

| Property | Google Docs Default | md2gdoc Default | Pandoc Default |
|----------|-------------------|-----------------|----------------|
| Body font | Arial 11pt | Arial 11pt | Cambria 12pt |
| Line spacing | 1.15 | 1.15 | 1.0 |
| Code font | Roboto Mono | Roboto Mono | Courier New |
| Inline code color | #188038 (green) | #188038 (green) | none |
| Heading colors | none / #434343 | none / #434343 | #0F4761 (blue) |
| After-paragraph gap | none | none | 10pt |

## Development

```bash
# Lint
shellcheck md2gdoc
ruff check build-reference.py

# Test
bash tests/test_conversion.sh
```

## License

[MIT](LICENSE)
