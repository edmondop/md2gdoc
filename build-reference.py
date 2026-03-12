#!/usr/bin/env python3
# /// script
# requires-python = ">=3.10"
# dependencies = ["python-docx", "lxml"]
# ///
"""Build a Pandoc reference DOCX that matches Google Docs 'paste from markdown' styling.

Run with:
    uv run build-reference.py
    uv run build-reference.py --output my-reference.docx

The generated reference DOCX configures:
    - Arial 11pt body text (Google Docs default)
    - Roboto Mono 10pt for code blocks and inline code
    - 1.15 line spacing (Google Docs default)
    - Heading styles matching Google Docs conventions
    - Green inline code (#188038) matching Google Docs rendering
"""

import argparse
import subprocess
import tempfile
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor
from lxml import etree


def build_reference(*, output_path: Path) -> None:
    with tempfile.NamedTemporaryFile(suffix=".docx", delete=False) as tmp:
        subprocess.run(
            ["pandoc", "-o", tmp.name, "--print-default-data-file", "reference.docx"],
            check=True,
        )
        doc = Document(tmp.name)

    _set_default_font(doc, name="Arial", size=Pt(11))
    _set_default_line_spacing(doc)
    _style_headings(doc)
    _style_code(doc)
    _style_body(doc)

    doc.save(str(output_path))
    print(f"Built {output_path}")


def _set_default_font(doc: Document, *, name: str, size: Pt) -> None:
    dd = doc.styles.element.find(qn("w:docDefaults"))
    rpr = dd.find(qn("w:rPrDefault")).find(qn("w:rPr"))

    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = etree.SubElement(rpr, qn("w:rFonts"))

    for theme_attr in ["asciiTheme", "eastAsiaTheme", "hAnsiTheme", "cstheme"]:
        key = qn(f"w:{theme_attr}")
        if key in fonts.attrib:
            del fonts.attrib[key]

    for attr in ["ascii", "hAnsi", "eastAsia", "cs"]:
        fonts.set(qn(f"w:{attr}"), name)

    half_pts = str(int(size.pt * 2))
    for tag in ["w:sz", "w:szCs"]:
        el = rpr.find(qn(tag))
        if el is None:
            el = etree.SubElement(rpr, qn(tag))
        el.set(qn("w:val"), half_pts)


def _set_default_line_spacing(doc: Document) -> None:
    dd = doc.styles.element.find(qn("w:docDefaults"))
    pprd = dd.find(qn("w:pPrDefault"))
    if pprd is None:
        pprd = etree.SubElement(dd, qn("w:pPrDefault"))
    ppr = pprd.find(qn("w:pPr"))
    if ppr is None:
        ppr = etree.SubElement(pprd, qn("w:pPr"))

    spacing = ppr.find(qn("w:spacing"))
    if spacing is None:
        spacing = etree.SubElement(ppr, qn("w:spacing"))

    # Google Docs default: 1.15x line spacing, no paragraph gaps
    spacing.set(qn("w:line"), "276")
    spacing.set(qn("w:lineRule"), "auto")
    spacing.set(qn("w:after"), "0")
    spacing.set(qn("w:before"), "0")


def _style_headings(doc: Document) -> None:
    configs = {
        "Heading 1": {"size": Pt(20), "color": None, "bold": True, "before": Pt(20), "after": Pt(6)},
        "Heading 2": {"size": Pt(16), "color": None, "bold": False, "before": Pt(18), "after": Pt(6)},
        "Heading 3": {"size": Pt(14), "color": RGBColor(0x43, 0x43, 0x43), "bold": False, "before": Pt(16), "after": Pt(4)},
    }

    for style_name, cfg in configs.items():
        style = doc.styles[style_name]
        style.font.name = "Arial"
        style.font.size = cfg["size"]
        style.font.bold = cfg["bold"]

        rpr = style.element.find(qn("w:rPr"))
        if rpr is not None:
            color_el = rpr.find(qn("w:color"))
            if cfg["color"] is None:
                if color_el is not None:
                    rpr.remove(color_el)
            else:
                style.font.color.rgb = cfg["color"]

        style.paragraph_format.space_before = cfg["before"]
        style.paragraph_format.space_after = cfg["after"]


def _style_code(doc: Document) -> None:
    if "Source Code" in doc.styles:
        sc = doc.styles["Source Code"]
        sc.font.name = "Roboto Mono"
        sc.font.size = Pt(10)
        sc.paragraph_format.space_before = Pt(0)
        sc.paragraph_format.space_after = Pt(0)

        ppr = sc.element.find(qn("w:pPr"))
        if ppr is not None:
            shd = ppr.find(qn("w:shd"))
            if shd is not None:
                ppr.remove(shd)

    if "Verbatim Char" in doc.styles:
        vc = doc.styles["Verbatim Char"]
        vc.font.name = "Roboto Mono"
        vc.font.size = Pt(10)
        vc.font.color.rgb = RGBColor(0x18, 0x80, 0x38)


def _style_body(doc: Document) -> None:
    for style_name in ["Normal", "First Paragraph", "Block Text", "Compact"]:
        if style_name in doc.styles:
            style = doc.styles[style_name]
            style.font.name = "Arial"
            style.font.size = Pt(11)
            style.paragraph_format.space_before = Pt(0)
            style.paragraph_format.space_after = Pt(0)

    if "Body Text" in doc.styles:
        bt = doc.styles["Body Text"]
        bt.font.name = "Arial"
        bt.font.size = Pt(11)
        bt.paragraph_format.space_before = Pt(0)
        bt.paragraph_format.space_after = Pt(0)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build a Pandoc reference DOCX matching Google Docs styling.",
    )
    parser.add_argument(
        "-o", "--output",
        default="gdocs-reference.docx",
        help="Output path for the reference DOCX (default: gdocs-reference.docx)",
    )
    args = parser.parse_args()
    build_reference(output_path=Path(args.output))


if __name__ == "__main__":
    main()
