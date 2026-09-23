from pathlib import Path
from datetime import datetime
from textwrap import wrap
from fpdf import FPDF
from app.config import get_settings
from app.schemas import ComicPanel


def _pdf_text(value: str, width: int = 15) -> str:
    lines = []
    for line in str(value).splitlines() or [""]:
        lines.extend(wrap(
            line,
            width=width,
            break_long_words=True,
            break_on_hyphens=False,
        ) or [""])
    return "\n".join(lines)


def _multi_cell(pdf: FPDF, height: float, text: str) -> None:
    pdf.set_x(pdf.l_margin)
    pdf.multi_cell(0, height, text)


def save_pdf(title: str, panels: list[ComicPanel]) -> str:
    settings = get_settings()
    settings.ensure_directories()

    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)

    for panel in panels:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 18)
        _multi_cell(pdf, 10, _pdf_text(
            f"Panel {panel.panel_number}: {panel.title}", width=12))

        image_name = panel.image_url.rsplit("/", 1)[-1]
        image_path = settings.panels_dir / image_name
        if image_path.exists():
            pdf.image(str(image_path), x=15, y=35, w=180)

        pdf.set_y(145)
        pdf.set_font("Helvetica", "I", 10)
        _multi_cell(pdf, 6, _pdf_text(panel.scene_description))

        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 11)
        _multi_cell(pdf, 6, "Caption")
        pdf.set_font("Helvetica", "", 10)
        _multi_cell(pdf, 6, _pdf_text(panel.caption))

        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 11)
        _multi_cell(pdf, 6, "Narration")
        pdf.set_font("Helvetica", "", 10)
        _multi_cell(pdf, 6, _pdf_text(panel.narration))

        if panel.dialogue:
            pdf.ln(2)
            pdf.set_font("Helvetica", "B", 11)
            _multi_cell(pdf, 6, "Dialogue")
            pdf.set_font("Helvetica", "", 10)
            _multi_cell(pdf, 6, _pdf_text(panel.dialogue))

    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = "".join(
        c if c.isalnum() or c in "-_" else "_" for c in title)[:50]
    filename = f"{safe_title or 'comic'}_{stamp}.pdf"
    output = settings.exports_dir / filename
    pdf.output(str(output))
    return str(output)
