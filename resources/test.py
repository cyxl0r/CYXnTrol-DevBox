from __future__ import annotations

from pathlib import Path
import copy
import html
import importlib.util
import os
import re
import shutil
import sqlite3
import sys
import tempfile
import zipfile


home_path = Path(__file__).resolve().parent
os.chdir(home_path)

current_path = home_path
projekt_root_path = None

while True:
    root_file = current_path / ".root"

    if root_file.is_file():
        content = root_file.read_text(encoding="utf-8").strip()

        if content == "project-root":
            projekt_root_path = current_path
            break

    parent_path = current_path.parent

    if parent_path == current_path:
        print("No project root found.")
        sys.exit(0)

    current_path = parent_path
    os.chdir(current_path)


rnd_prv = projekt_root_path / "platform" / "tools" / "random_string_provider.py"
tme_prv = projekt_root_path / "platform" / "tools" / "timestamp_provider.py"


def load_module(module_name: str, module_file: Path):
    module_spec = importlib.util.spec_from_file_location(
        module_name,
        module_file,
    )

    if module_spec is None or module_spec.loader is None:
        raise RuntimeError(f"Could not load module: {module_file}")

    module = importlib.util.module_from_spec(module_spec)
    module_spec.loader.exec_module(module)

    return module


def quote_identifier(identifier: str) -> str:
    return '"' + identifier.replace('"', '""') + '"'


def table_exists(connection: sqlite3.Connection, table_name: str) -> bool:
    cursor = connection.execute(
        """
        SELECT name
        FROM sqlite_master
        WHERE type = 'table'
          AND name = ?
        """,
        (table_name,),
    )

    return cursor.fetchone() is not None


def get_table_columns(
    connection: sqlite3.Connection,
    table_name: str,
) -> list[str]:
    cursor = connection.execute(
        f"PRAGMA table_info({quote_identifier(table_name)})"
    )

    return [
        str(row[1])
        for row in cursor.fetchall()
    ]


def get_first_row(
    connection: sqlite3.Connection,
    table_name: str,
) -> dict[str, object]:
    if not table_exists(connection, table_name):
        return {}

    cursor = connection.execute(
        f"""
        SELECT *
        FROM {quote_identifier(table_name)}
        LIMIT 1
        """
    )

    row = cursor.fetchone()

    if row is None:
        return {}

    return {
        key: row[key]
        for key in row.keys()
    }


def get_manufacturer_row(
    connection: sqlite3.Connection,
) -> dict[str, object]:
    table_name = "manufacturer_credentials"

    if not table_exists(connection, table_name):
        return {}

    columns = get_table_columns(connection, table_name)

    if "manufacturer_name" not in columns:
        return get_first_row(connection, table_name)

    cursor = connection.execute(
        f"""
        SELECT *
        FROM {quote_identifier(table_name)}
        WHERE {quote_identifier("manufacturer_name")} IS NULL
           OR {quote_identifier("manufacturer_name")} != ?
        LIMIT 1
        """,
        ("__devbox_internal_key__",),
    )

    row = cursor.fetchone()

    if row is None:
        return {}

    return {
        key: row[key]
        for key in row.keys()
    }


def get_product_row(
    connection: sqlite3.Connection,
) -> dict[str, object]:
    table_name = "product_credentials"

    if not table_exists(connection, table_name):
        return {}

    columns = get_table_columns(connection, table_name)

    if "product_name" in columns:
        cursor = connection.execute(
            f"""
            SELECT *
            FROM {quote_identifier(table_name)}
            WHERE LOWER({quote_identifier("product_name")}) = ?
            LIMIT 1
            """,
            ("devbox",),
        )

        row = cursor.fetchone()

        if row is not None:
            return {
                key: row[key]
                for key in row.keys()
            }

    order_column = "product_id" if "product_id" in columns else "rowid"

    cursor = connection.execute(
        f"""
        SELECT *
        FROM {quote_identifier(table_name)}
        ORDER BY {quote_identifier(order_column)} ASC
        LIMIT 1
        """
    )

    row = cursor.fetchone()

    if row is None:
        return {}

    return {
        key: row[key]
        for key in row.keys()
    }


def normalize_table_prefix(value: object) -> str:
    return "".join(
        character.lower()
        for character in str(value or "")
        if character.isalnum() or character == "_"
    )


def get_document_row(
    connection: sqlite3.Connection,
    product_name: object,
    language_code: str,
) -> dict[str, object]:
    normalized_product_name = normalize_table_prefix(product_name)

    if normalized_product_name == "devbox":
        table_name = f"devbox_document_credentials_{language_code}"
    else:
        table_name = (
            f"{normalized_product_name}_document_credentials_{language_code}"
        )

    return get_first_row(connection, table_name)


def as_text(value: object) -> str:
    if value is None:
        return ""

    if isinstance(value, bytes):
        return ""

    return str(value)


def extract_year(value: object) -> str:
    text_value = as_text(value)

    for index in range(len(text_value) - 3):
        candidate = text_value[index:index + 4]

        if candidate.isdigit():
            return candidate

    return text_value


def get_value(
    data: dict[str, object],
    column_name: str,
) -> str:
    return as_text(data.get(column_name))


def fill_document(
    document_file: Path,
    placeholder_values: dict[str, str],
) -> None:
    if not document_file.is_file():
        return

    document_text = document_file.read_text(
        encoding="utf-8",
    )

    for placeholder_name, placeholder_value in placeholder_values.items():
        document_text = document_text.replace(
            f"{{{{{placeholder_name}}}}}",
            placeholder_value,
        )

    document_file.write_text(
        document_text,
        encoding="utf-8",
    )


def find_file_by_name(
    search_directory: Path,
    file_name: str,
) -> Path:
    if not search_directory.is_dir():
        raise FileNotFoundError(
            f"Search directory not found: {search_directory}"
        )

    requested_name = file_name.casefold()

    for item in search_directory.rglob("*"):
        if item.is_file() and item.name.casefold() == requested_name:
            return item

    raise FileNotFoundError(
        f"Required file was not found: {file_name} "
        f"in {search_directory}"
    )


def import_pdf_dependencies() -> dict[str, object]:
    try:
        from reportlab.lib.colors import HexColor
        from reportlab.lib.enums import TA_LEFT
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.pdfbase import pdfmetrics
        from reportlab.pdfbase.ttfonts import TTFont
        from reportlab.platypus import (
            Paragraph,
            SimpleDocTemplate,
            Spacer,
        )
        from reportlab.graphics import renderPDF
        from svglib.svglib import svg2rlg
    except ImportError as error:
        raise RuntimeError(
            "PDF generation requires the Python packages "
            "'reportlab' and 'svglib'. Install them with: "
            "python -m pip install reportlab svglib"
        ) from error

    return {
        "HexColor": HexColor,
        "TA_LEFT": TA_LEFT,
        "A4": A4,
        "ParagraphStyle": ParagraphStyle,
        "mm": mm,
        "pdfmetrics": pdfmetrics,
        "TTFont": TTFont,
        "Paragraph": Paragraph,
        "SimpleDocTemplate": SimpleDocTemplate,
        "Spacer": Spacer,
        "renderPDF": renderPDF,
        "svg2rlg": svg2rlg,
    }


def register_pdf_fonts(
    pdf_modules: dict[str, object],
    project_root: Path,
) -> dict[str, str]:
    fonts_directory = project_root / "resources" / "fonts"

    body_font_file = find_file_by_name(
        fonts_directory,
        "LexendExa-Light.ttf",
    )

    main_heading_font_file = find_file_by_name(
        fonts_directory,
        "Oxanium-ExtraBold.ttf",
    )

    sub_heading_font_file = find_file_by_name(
        fonts_directory,
        "Oxanium-Bold.ttf",
    )

    pdfmetrics = pdf_modules["pdfmetrics"]
    TTFont = pdf_modules["TTFont"]

    font_definitions = {
        "DevBoxLexendExaLight": body_font_file,
        "DevBoxOxaniumExtraBold": main_heading_font_file,
        "DevBoxOxaniumBold": sub_heading_font_file,
    }

    registered_fonts = set(pdfmetrics.getRegisteredFontNames())

    for font_name, font_file in font_definitions.items():
        if font_name not in registered_fonts:
            pdfmetrics.registerFont(
                TTFont(
                    font_name,
                    str(font_file),
                )
            )

    return {
        "body": "DevBoxLexendExaLight",
        "main_heading": "DevBoxOxaniumExtraBold",
        "sub_heading": "DevBoxOxaniumBold",
    }


def load_svg_drawing(
    pdf_modules: dict[str, object],
    svg_file: Path,
):
    if not svg_file.is_file():
        raise FileNotFoundError(
            f"SVG file not found: {svg_file}"
        )

    svg2rlg = pdf_modules["svg2rlg"]
    drawing = svg2rlg(str(svg_file))

    if drawing is None:
        raise RuntimeError(
            f"Could not load SVG drawing: {svg_file}"
        )

    return drawing


def draw_svg_fitted(
    canvas,
    drawing,
    x: float,
    y: float,
    width: float,
    height: float,
    render_pdf,
) -> None:
    drawing_copy = copy.deepcopy(drawing)

    drawing_width = float(getattr(drawing_copy, "width", 0))
    drawing_height = float(getattr(drawing_copy, "height", 0))

    if drawing_width <= 0 or drawing_height <= 0:
        raise RuntimeError(
            "SVG drawing has invalid dimensions."
        )

    scale_factor = min(
        width / drawing_width,
        height / drawing_height,
    )

    rendered_width = drawing_width * scale_factor
    rendered_height = drawing_height * scale_factor

    drawing_copy.scale(
        scale_factor,
        scale_factor,
    )

    render_x = x + ((width - rendered_width) / 2)
    render_y = y + ((height - rendered_height) / 2)

    render_pdf.draw(
        drawing_copy,
        canvas,
        render_x,
        render_y,
    )


def create_pdf_page_decorator(
    pdf_modules: dict[str, object],
    header_drawing,
    footer_drawing,
    document_title: str,
):
    A4 = pdf_modules["A4"]
    mm = pdf_modules["mm"]
    render_pdf = pdf_modules["renderPDF"]

    page_width, page_height = A4

    header_height = 30 * mm
    footer_height = 22 * mm

    def decorate_page(canvas, document) -> None:
        canvas.saveState()
        canvas.setTitle(document_title)

        draw_svg_fitted(
            canvas=canvas,
            drawing=header_drawing,
            x=0,
            y=page_height - header_height,
            width=page_width,
            height=header_height,
            render_pdf=render_pdf,
        )

        draw_svg_fitted(
            canvas=canvas,
            drawing=footer_drawing,
            x=0,
            y=0,
            width=page_width,
            height=footer_height,
            render_pdf=render_pdf,
        )

        canvas.restoreState()

    return decorate_page


def get_heading_type(
    text_line: str,
    main_heading_already_added: bool,
) -> str | None:
    stripped_line = text_line.strip()

    if not stripped_line:
        return None

    if not main_heading_already_added:
        return "main"

    markdown_match = re.match(
        r"^(#{1,6})\s+(.+)$",
        stripped_line,
    )

    if markdown_match is not None:
        heading_markers = markdown_match.group(1)

        if len(heading_markers) == 1:
            return "main"

        return "sub"

    if re.match(
        r"^\d+\.\s+\S+",
        stripped_line,
    ):
        return "main"

    if re.match(
        r"^\d+(?:\.\d+)+\.?\s+\S+",
        stripped_line,
    ):
        return "sub"

    if (
        stripped_line.isupper()
        and any(character.isalpha() for character in stripped_line)
        and len(stripped_line) <= 120
    ):
        return "main"

    return None


def clean_heading_text(text_line: str) -> str:
    return re.sub(
        r"^#{1,6}\s+",
        "",
        text_line.strip(),
    )


def build_pdf_story(
    pdf_modules: dict[str, object],
    document_text: str,
    font_names: dict[str, str],
):
    HexColor = pdf_modules["HexColor"]
    TA_LEFT = pdf_modules["TA_LEFT"]
    ParagraphStyle = pdf_modules["ParagraphStyle"]
    Paragraph = pdf_modules["Paragraph"]
    Spacer = pdf_modules["Spacer"]
    mm = pdf_modules["mm"]

    text_color = HexColor("#4D4D4D")

    body_style = ParagraphStyle(
        name="DevBoxBodyText",
        fontName=font_names["body"],
        fontSize=8.7,
        leading=13.2,
        textColor=text_color,
        alignment=TA_LEFT,
        spaceAfter=2.2 * mm,
        wordWrap="CJK",
    )

    main_heading_style = ParagraphStyle(
        name="DevBoxMainHeading",
        fontName=font_names["main_heading"],
        fontSize=17,
        leading=21,
        textColor=text_color,
        alignment=TA_LEFT,
        spaceBefore=5 * mm,
        spaceAfter=4 * mm,
        wordWrap="CJK",
    )

    sub_heading_style = ParagraphStyle(
        name="DevBoxSubHeading",
        fontName=font_names["sub_heading"],
        fontSize=10.8,
        leading=14.5,
        textColor=text_color,
        alignment=TA_LEFT,
        spaceBefore=3.2 * mm,
        spaceAfter=2.4 * mm,
        wordWrap="CJK",
    )

    story = []
    paragraph_lines: list[str] = []
    main_heading_already_added = False

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return

        paragraph_text = " ".join(
            line.strip()
            for line in paragraph_lines
            if line.strip()
        )

        if paragraph_text:
            story.append(
                Paragraph(
                    html.escape(paragraph_text),
                    body_style,
                )
            )

        paragraph_lines.clear()

    for raw_line in document_text.splitlines():
        stripped_line = raw_line.strip()

        if not stripped_line:
            flush_paragraph()

            if story:
                story.append(
                    Spacer(
                        1,
                        1.5 * mm,
                    )
                )

            continue

        heading_type = get_heading_type(
            stripped_line,
            main_heading_already_added,
        )

        if heading_type is not None:
            flush_paragraph()

            heading_text = clean_heading_text(
                stripped_line
            )

            if heading_type == "main":
                story.append(
                    Paragraph(
                        html.escape(heading_text),
                        main_heading_style,
                    )
                )

                main_heading_already_added = True
            else:
                story.append(
                    Paragraph(
                        html.escape(heading_text),
                        sub_heading_style,
                    )
                )

            continue

        bullet_match = re.match(
            r"^[-*•]\s+(.+)$",
            stripped_line,
        )

        if bullet_match is not None:
            flush_paragraph()

            bullet_text = bullet_match.group(1)

            story.append(
                Paragraph(
                    "• " + html.escape(bullet_text),
                    body_style,
                )
            )

            continue

        paragraph_lines.append(stripped_line)

    flush_paragraph()

    return story


def create_pdf_document(
    pdf_modules: dict[str, object],
    document_file: Path,
    pdf_file: Path,
    document_title: str,
    font_names: dict[str, str],
    header_drawing,
    footer_drawing,
) -> None:
    A4 = pdf_modules["A4"]
    SimpleDocTemplate = pdf_modules["SimpleDocTemplate"]
    mm = pdf_modules["mm"]

    if not document_file.is_file():
        raise FileNotFoundError(
            f"Document form not found: {document_file}"
        )

    document_text = document_file.read_text(
        encoding="utf-8",
    )

    story = build_pdf_story(
        pdf_modules=pdf_modules,
        document_text=document_text,
        font_names=font_names,
    )

    if not story:
        raise RuntimeError(
            f"Document does not contain any printable content: "
            f"{document_file}"
        )

    left_margin = 18 * mm
    right_margin = 18 * mm
    top_margin = 40 * mm
    bottom_margin = 31 * mm

    document = SimpleDocTemplate(
        str(pdf_file),
        pagesize=A4,
        leftMargin=left_margin,
        rightMargin=right_margin,
        topMargin=top_margin,
        bottomMargin=bottom_margin,
    )

    page_decorator = create_pdf_page_decorator(
        pdf_modules=pdf_modules,
        header_drawing=header_drawing,
        footer_drawing=footer_drawing,
        document_title=document_title,
    )

    document.build(
        story,
        onFirstPage=page_decorator,
        onLaterPages=page_decorator,
    )

    print(f"PDF created: {pdf_file}")


def create_legal_pdfs(
    project_root: Path,
    docs_directory: Path,
    document_row_de: dict[str, object],
    document_row_en: dict[str, object],
) -> None:
    document_jobs = [
        {
            "field_name": "terms_of_use",
            "form_name": "TERMS_OF_USE_FORM_DE.txt",
            "pdf_name": "TERMS_OF_USE_DE.pdf",
            "title": "Nutzungsbedingungen",
            "row": document_row_de,
        },
        {
            "field_name": "terms_of_use",
            "form_name": "TERMS_OF_USE_FORM_EN.txt",
            "pdf_name": "TERMS_OF_USE_EN.pdf",
            "title": "Terms of Use",
            "row": document_row_en,
        },
        {
            "field_name": "privacy_policy",
            "form_name": "PRIVACY_POLICY_FORM_DE.txt",
            "pdf_name": "PRIVACY_POLICY_DE.pdf",
            "title": "Datenschutzbestimmungen",
            "row": document_row_de,
        },
        {
            "field_name": "privacy_policy",
            "form_name": "PRIVACY_POLICY_FORM_EN.txt",
            "pdf_name": "PRIVACY_POLICY_EN.pdf",
            "title": "Privacy Policy",
            "row": document_row_en,
        },
    ]

    active_jobs = [
        job
        for job in document_jobs
        if get_value(
            job["row"],
            job["field_name"],
        ).strip()
    ]

    if not active_jobs:
        print(
            "No Terms of Use or Privacy Policy content found. "
            "PDF creation skipped."
        )
        return

    pdf_modules = import_pdf_dependencies()

    font_names = register_pdf_fonts(
        pdf_modules=pdf_modules,
        project_root=project_root,
    )

    header_file = (
        project_root
        / "resources"
        / "graphics"
        / "header.svg"
    )

    footer_file = (
        project_root
        / "resources"
        / "graphics"
        / "footer.svg"
    )

    header_drawing = load_svg_drawing(
        pdf_modules=pdf_modules,
        svg_file=header_file,
    )

    footer_drawing = load_svg_drawing(
        pdf_modules=pdf_modules,
        svg_file=footer_file,
    )

    for job in active_jobs:
        form_file = docs_directory / job["form_name"]
        pdf_file = docs_directory / job["pdf_name"]

        create_pdf_document(
            pdf_modules=pdf_modules,
            document_file=form_file,
            pdf_file=pdf_file,
            document_title=job["title"],
            font_names=font_names,
            header_drawing=header_drawing,
            footer_drawing=footer_drawing,
        )


def copy_publish_file(
    source_file: Path,
    target_file: Path,
    required: bool,
) -> None:
    target_file.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    if source_file.is_file():
        shutil.copy2(
            source_file,
            target_file,
        )

        print(
            f"Published document: "
            f"{source_file.name} -> {target_file}"
        )
        return

    if target_file.is_file():
        try:
            target_file.unlink()
            print(
                f"Removed stale document: {target_file}"
            )
        except OSError as error:
            print(
                f"Could not remove stale document: "
                f"{target_file}"
            )
            print(error)

    if required:
        raise FileNotFoundError(
            f"Required document was not created: {source_file}"
        )

    print(
        f"Optional document not created and skipped: "
        f"{source_file.name}"
    )


def publish_document_outputs(
    root_dir: Path,
    docs_directory: Path,
    assets_path: Path,
    documents_path: Path,
    pictures_path: Path,
) -> None:
    assets_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    documents_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    pictures_path.mkdir(
        parents=True,
        exist_ok=True,
    )

    root_document_jobs = [
        (
            docs_directory / "README_FORM_EN.txt",
            root_dir / "readme.md",
            True,
        ),
        (
            docs_directory / "README_FORM_DE.txt",
            root_dir / "readme_de.md",
            True,
        ),
        (
            docs_directory / "LICENSE_FORM_EN.txt",
            root_dir / "license.md",
            True,
        ),
        (
            docs_directory / "LICENSE_FORM_DE.txt",
            root_dir / "license_de.md",
            True,
        ),
    ]

    asset_document_jobs = [
        (
            docs_directory / "ARCHITECTURE_FORM_EN.txt",
            documents_path / "en_architecture.md",
            True,
        ),
        (
            docs_directory / "ARCHITECTURE_FORM_DE.txt",
            documents_path / "de_architektur.md",
            True,
        ),
        (
            docs_directory / "RULES_CATALOG_FORM_EN.txt",
            documents_path / "en_rules_catalog.md",
            True,
        ),
        (
            docs_directory / "RULES_CATALOG_FORM_DE.txt",
            documents_path / "de_regelkatalog.md",
            True,
        ),
        (
            docs_directory / "TODO_LIST_FORM_EN.txt",
            documents_path / "en_todo_list.md",
            True,
        ),
        (
            docs_directory / "TODO_LIST_FORM_DE.txt",
            documents_path / "de_todo_liste.md",
            True,
        ),
        (
            docs_directory / "TERMS_OF_USE_EN.pdf",
            documents_path / "en_terms_of_use.pdf",
            False,
        ),
        (
            docs_directory / "TERMS_OF_USE_DE.pdf",
            documents_path / "de_nutzungsbedingungen.pdf",
            False,
        ),
        (
            docs_directory / "PRIVACY_POLICY_EN.pdf",
            documents_path / "en_privacy_policy.pdf",
            False,
        ),
        (
            docs_directory / "PRIVACY_POLICY_DE.pdf",
            documents_path / "de_datenschutzbestimmungen.pdf",
            False,
        ),
    ]

    for source_file, target_file, required in root_document_jobs:
        copy_publish_file(
            source_file=source_file,
            target_file=target_file,
            required=required,
        )

    for source_file, target_file, required in asset_document_jobs:
        copy_publish_file(
            source_file=source_file,
            target_file=target_file,
            required=required,
        )

    print(f"Assets path ready: {assets_path}")
    print(f"Documents path ready: {documents_path}")
    print(f"Pictures path ready: {pictures_path}")


if not rnd_prv.is_file():
    print(f"Provider not found: {rnd_prv}")
    sys.exit(1)

if not tme_prv.is_file():
    print(f"Provider not found: {tme_prv}")
    sys.exit(1)


rnd_module = load_module(
    "random_string_provider",
    rnd_prv,
)

tme_module = load_module(
    "timestamp_provider",
    tme_prv,
)

timestamp_value = tme_module.generate_combined_timestamp(
    variants=[4, 14],
)

random_value = rnd_module.generate_string(
    length=128,
    variant=1,
)

temp_path = Path(tempfile.gettempdir()) / f"{timestamp_value}_{random_value}"
root_dir = temp_path / "root_dir"
docs_directory = temp_path / "docs"

assets_path = root_dir / "assets"
documents_path = assets_path / "documents"
pictures_path = assets_path / "pictures"

temp_path.mkdir(
    parents=True,
    exist_ok=False,
)

root_dir.mkdir(
    parents=True,
    exist_ok=True,
)

shutil.copytree(
    projekt_root_path,
    root_dir,
    dirs_exist_ok=True,
)

pycache_directories = sorted(
    [
        item
        for item in root_dir.rglob("__pycache__")
        if item.is_dir()
    ],
    key=lambda item: len(item.parts),
    reverse=True,
)

for pycache_directory in pycache_directories:
    shutil.rmtree(
        pycache_directory,
        ignore_errors=True,
    )

applications_directory = root_dir / "applications"

if applications_directory.is_dir():
    shutil.rmtree(
        applications_directory,
        ignore_errors=True,
    )

applications_directory.mkdir(
    parents=True,
    exist_ok=True,
)

fonts_directory = root_dir / "resources" / "fonts"

if fonts_directory.is_dir():
    font_files = [
        item
        for item in fonts_directory.rglob("*")
        if item.is_file()
    ]

    for font_file in font_files:
        try:
            font_file.unlink()
        except OSError as error:
            print(f"Could not delete font file: {font_file}")
            print(error)

third_party_installers_directory = (
    root_dir
    / "resources"
    / "third_party_installers"
)

if third_party_installers_directory.is_dir():
    installer_files = [
        item
        for item in third_party_installers_directory.iterdir()
        if item.is_file()
    ]

    installer_file_names = [
        item.name
        for item in installer_files
    ]

    for installer_file in installer_files:
        try:
            installer_file.unlink()
        except OSError as error:
            print(f"Could not delete installer file: {installer_file}")
            print(error)

    for installer_file_name in installer_file_names:
        dummy_file = (
            third_party_installers_directory
            / installer_file_name
        )

        dummy_file.write_text(
            "Dummy.EXE",
            encoding="utf-8",
        )

devbox_exe_file = (
    root_dir
    / "resources"
    / "applications"
    / "devbox"
    / "devbox.exe"
)

if devbox_exe_file.is_file():
    try:
        devbox_exe_file.unlink()
    except OSError as error:
        print(f"Could not delete DevBox EXE file: {devbox_exe_file}")
        print(error)

docs_directory.mkdir(
    parents=True,
    exist_ok=True,
)

doc_forms_file = (
    root_dir
    / "resources"
    / "organization"
    / "doc_forms.r0b"
)

if doc_forms_file.is_file():
    try:
        with zipfile.ZipFile(doc_forms_file, "r") as archive:
            archive.extractall(docs_directory)
    except (OSError, zipfile.BadZipFile) as error:
        print(f"Could not extract document forms: {doc_forms_file}")
        print(error)
else:
    print(f"Document forms ZIP not found: {doc_forms_file}")

database_file = (
    root_dir
    / "resources"
    / "organization"
    / "devbox_db.r0b"
)

if database_file.is_file():
    connection = sqlite3.connect(database_file)
    connection.row_factory = sqlite3.Row

    try:
        manufacturer_row = get_manufacturer_row(connection)
        product_row = get_product_row(connection)

        product_name = get_value(
            product_row,
            "product_name",
        )

        document_row_de = get_document_row(
            connection,
            product_name,
            "de",
        )

        document_row_en = get_document_row(
            connection,
            product_name,
            "en",
        )

        base_placeholders = {
            "LICENSE_NAME": get_value(product_row, "license_name"),
            "LICENSE_VERSION": get_value(product_row, "license_version"),
            "AUTHOR_NAME": (
                get_value(manufacturer_row, "author_name")
                or get_value(product_row, "author")
            ),
            "AUTHOR_DISPLAY_NAME": (
                get_value(manufacturer_row, "author_display_name")
                or get_value(product_row, "author")
            ),
            "COPYRIGHT_YEAR": get_value(product_row, "copyright_year"),
            "PUBLICATION_YEAR": extract_year(
                product_row.get("release_date")
            ),
            "PROJECT_START_YEAR": extract_year(
                product_row.get("programming_start")
            ),
            "COUNTRY": (
                get_value(manufacturer_row, "country")
                or get_value(product_row, "country")
            ),
            "COUNTRY_CODE": (
                get_value(manufacturer_row, "country_code")
                or get_value(product_row, "country_code")
            ),
        }

        document_placeholder_map = {
            "short_description": "PROJECT_SHORT_DESCRIPTION",
            "long_description": "PROJECT_LONG_DESCRIPTION",
            "purpose": "PROJECT_PURPOSE",
            "context": "PROJECT_CONTEXT",
            "core_idea": "PROJECT_CORE_IDEA",
            "features_and_goals": "PROJECT_FEATURES_AND_GOALS",
            "architecture_overview": "PROJECT_ARCHITECTURE_OVERVIEW",
            "architecture": "PROJECT_ARCHITECTURE",
            "rules_catalog": "PROJECT_RULES_CATALOG",
            "status": "PROJECT_STATUS",
            "installation_and_start": "PROJECT_INSTALLATION_AND_START",
            "configuration": "PROJECT_CONFIGURATION",
            "technology": "PROJECT_TECHNOLOGY",
            "repository_note": "PROJECT_REPOSITORY_NOTE",
            "terms_of_use": "PROJECT_TERMS_OF_USE",
            "privacy_policy": "PROJECT_PRIVACY_POLICY",
            "todo_list": "PROJECT_TODO_LIST",
        }

        placeholders_de = dict(base_placeholders)
        placeholders_en = dict(base_placeholders)

        for column_name, placeholder_name in document_placeholder_map.items():
            placeholders_de[placeholder_name] = get_value(
                document_row_de,
                column_name,
            )

            placeholders_en[placeholder_name] = get_value(
                document_row_en,
                column_name,
            )

        fill_document(
            docs_directory / "LICENSE_FORM_DE.txt",
            placeholders_de,
        )

        fill_document(
            docs_directory / "README_FORM_DE.txt",
            placeholders_de,
        )

        fill_document(
            docs_directory / "ARCHITECTURE_FORM_DE.txt",
            placeholders_de,
        )

        fill_document(
            docs_directory / "RULES_CATALOG_FORM_DE.txt",
            placeholders_de,
        )

        fill_document(
            docs_directory / "TODO_LIST_FORM_DE.txt",
            placeholders_de,
        )

        fill_document(
            docs_directory / "TERMS_OF_USE_FORM_DE.txt",
            placeholders_de,
        )

        fill_document(
            docs_directory / "PRIVACY_POLICY_FORM_DE.txt",
            placeholders_de,
        )

        fill_document(
            docs_directory / "LICENSE_FORM_EN.txt",
            placeholders_en,
        )

        fill_document(
            docs_directory / "README_FORM_EN.txt",
            placeholders_en,
        )

        fill_document(
            docs_directory / "ARCHITECTURE_FORM_EN.txt",
            placeholders_en,
        )

        fill_document(
            docs_directory / "RULES_CATALOG_FORM_EN.txt",
            placeholders_en,
        )

        fill_document(
            docs_directory / "TODO_LIST_FORM_EN.txt",
            placeholders_en,
        )

        fill_document(
            docs_directory / "TERMS_OF_USE_FORM_EN.txt",
            placeholders_en,
        )

        fill_document(
            docs_directory / "PRIVACY_POLICY_FORM_EN.txt",
            placeholders_en,
        )

        create_legal_pdfs(
            project_root=projekt_root_path,
            docs_directory=docs_directory,
            document_row_de=document_row_de,
            document_row_en=document_row_en,
        )

        publish_document_outputs(
            root_dir=root_dir,
            docs_directory=docs_directory,
            assets_path=assets_path,
            documents_path=documents_path,
            pictures_path=pictures_path,
        )

    finally:
        connection.close()
else:
    print(f"Database not found: {database_file}")

if database_file.is_file():
    try:
        database_file.unlink()
    except OSError as error:
        print(f"Could not delete database file: {database_file}")
        print(error)

os.startfile(root_dir)