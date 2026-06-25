from __future__ import annotations

import copy
import html
import re
from pathlib import Path

from subscripts.main_gui_devbox_log import get_devbox_logger


MODULE_LOGGER = get_devbox_logger(__file__)
MODULE_LOGGER.info("Module loaded.")


def _dependencies() -> dict[str, object]:
    try:
        from reportlab.graphics import renderPDF
        from reportlab.lib.colors import HexColor
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.pdfgen import canvas
        from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
        from svglib.svglib import svg2rlg
    except ImportError as error:
        raise RuntimeError("PDF generation requires reportlab and svglib.") from error
    return locals()


def _find_font(fonts_path: Path, preferred: str, fallback: str) -> Path:
    for name in (preferred, fallback):
        matches = [item for item in fonts_path.rglob(name) if item.is_file()]
        if matches:
            return matches[0]
    raise FileNotFoundError(f"Required font was not found: {preferred}")


def _register_fonts(pdf: dict[str, object], project_root: Path, reporter) -> dict[str, str]:
    fonts = project_root / "resources" / "fonts"
    files = {
        "body": _find_font(fonts, "LexendExa-Light.ttf", "LexendExa-VariableFont_wght.ttf"),
        "main": _find_font(fonts, "Oxanium-ExtraBold.ttf", "Oxanium-VariableFont_wght.ttf"),
        "sub": _find_font(fonts, "Oxanium-Bold.ttf", "Oxanium-VariableFont_wght.ttf"),
    }
    names = {"body": "DevBoxLexendExaLight", "main": "DevBoxOxaniumExtraBold", "sub": "DevBoxOxaniumBold"}
    known = set(pdf["pdfmetrics"].getRegisteredFontNames())
    for key, file_path in files.items():
        if names[key] not in known:
            pdf["pdfmetrics"].registerFont(pdf["TTFont"](names[key], str(file_path)))
    reporter.info("PDF fonts registered.", "; ".join(str(path.name) for path in files.values()))
    return names


def _drawing(pdf: dict[str, object], svg_file: Path):
    drawing = pdf["svg2rlg"](str(svg_file))
    if drawing is None:
        raise RuntimeError(f"SVG could not be loaded: {svg_file}")
    return drawing


def _draw_fitted(canvas, drawing, x, y, width, height, render_pdf) -> None:
    copied = copy.deepcopy(drawing)
    original_width, original_height = float(copied.width), float(copied.height)
    scale = min(width / original_width, height / original_height)
    copied.scale(scale, scale)
    render_pdf.draw(copied, canvas, x + (width - original_width * scale) / 2, y + (height - original_height * scale) / 2)


def _page_decorator(pdf, header, footer, title: str):
    page_width, page_height = pdf["A4"]
    mm, render_pdf = pdf["mm"], pdf["renderPDF"]
    def decorate(canvas, _document) -> None:
        canvas.saveState(); canvas.setTitle(title)
        _draw_fitted(canvas, header, 0, page_height - 30 * mm, page_width, 30 * mm, render_pdf)
        _draw_fitted(canvas, footer, 0, 0, page_width, 22 * mm, render_pdf)
        canvas.restoreState()
    return decorate


def _story(pdf, text: str, fonts: dict[str, str]):
    color, mm = pdf["HexColor"]("#4D4D4D"), pdf["mm"]
    style = pdf["ParagraphStyle"]
    body = style("Body", fontName=fonts["body"], fontSize=8.7, leading=13.2, textColor=color, spaceAfter=2.2 * mm, wordWrap="CJK")
    main = style("Main", fontName=fonts["main"], fontSize=17, leading=21, textColor=color, spaceBefore=5 * mm, spaceAfter=4 * mm, wordWrap="CJK")
    sub = style("Sub", fontName=fonts["sub"], fontSize=10.8, leading=14.5, textColor=color, spaceBefore=3.2 * mm, spaceAfter=2.4 * mm, wordWrap="CJK")
    items, paragraph, main_seen = [], [], False
    def flush() -> None:
        if paragraph:
            items.append(pdf["Paragraph"](html.escape(" ".join(paragraph)), body)); paragraph.clear()
    for line in text.splitlines():
        value = line.strip()
        if not value:
            flush(); continue
        markdown = re.match(r"^(#{1,6})\s+(.+)$", value)
        numbered = re.match(r"^\d+(?:\.\d+)*\.?\s+.+$", value)
        uppercase = value.isupper() and any(char.isalpha() for char in value)
        if markdown or numbered or (not main_seen and value):
            flush(); heading = markdown.group(2) if markdown else value
            is_sub = bool(markdown and len(markdown.group(1)) > 1) or bool(numbered and "." in value.split()[0])
            items.append(pdf["Paragraph"](html.escape(heading), sub if is_sub else main)); main_seen = True; continue
        bullet = re.match(r"^[-*•]\s+(.+)$", value)
        if bullet:
            flush(); items.append(pdf["Paragraph"]("• " + html.escape(bullet.group(1)), body)); continue
        paragraph.append(value)
    flush()
    return items


def _create_one(pdf, form_file: Path, output_file: Path, title: str, fonts, header, footer) -> None:
    text = form_file.read_text(encoding="utf-8")
    story = _story(pdf, text, fonts)
    if not story:
        raise RuntimeError(f"Printable content was empty: {form_file.name}")
    document = pdf["SimpleDocTemplate"](str(output_file), pagesize=pdf["A4"], leftMargin=18 * pdf["mm"], rightMargin=18 * pdf["mm"], topMargin=40 * pdf["mm"], bottomMargin=31 * pdf["mm"])
    decorator = _page_decorator(pdf, header, footer, title)

    class DeterministicCanvas(pdf["canvas"].Canvas):
        def __init__(self, *arguments, **keywords) -> None:
            keywords["invariant"] = 1
            super().__init__(*arguments, **keywords)

    document.build(
        story,
        onFirstPage=decorator,
        onLaterPages=decorator,
        canvasmaker=DeterministicCanvas,
    )


def create_legal_pdfs(context, german: dict[str, object], english: dict[str, object], reporter) -> None:
    jobs = (
        ("terms_of_use", "TERMS_OF_USE_FORM_DE.txt", "TERMS_OF_USE_DE.pdf", "Nutzungsbedingungen", german),
        ("terms_of_use", "TERMS_OF_USE_FORM_EN.txt", "TERMS_OF_USE_EN.pdf", "Terms of Use", english),
        ("privacy_policy", "PRIVACY_POLICY_FORM_DE.txt", "PRIVACY_POLICY_DE.pdf", "Datenschutzbestimmungen", german),
        ("privacy_policy", "PRIVACY_POLICY_FORM_EN.txt", "PRIVACY_POLICY_EN.pdf", "Privacy Policy", english),
    )
    active = [job for job in jobs if str(job[4].get(job[0]) or "").strip()]
    if not active:
        reporter.info("No legal PDF content present; PDF creation skipped."); return
    pdf = _dependencies(); fonts = _register_fonts(pdf, context.project_root, reporter)
    graphics = context.project_root / "resources" / "graphics"
    header, footer = _drawing(pdf, graphics / "header.svg"), _drawing(pdf, graphics / "footer.svg")
    for _, form_name, output_name, title, _ in active:
        _create_one(pdf, context.docs_path / form_name, context.docs_path / output_name, title, fonts, header, footer)
        reporter.info("Legal PDF created.", output_name)
