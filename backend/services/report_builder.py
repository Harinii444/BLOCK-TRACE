import json
import time
from pathlib import Path

from fpdf import FPDF

REPORTS_DIR = Path(__file__).resolve().parent.parent.parent / "reports"

PDF_HEADER = "BLOCK TRACE Forensic Report"
PDF_FOOTER = "This is an investigative aid. Not legal evidence."
PDF_COLUMNS = ["Hop", "From", "To", "Txid", "Amount", "Risk", "VASP"]
PDF_WIDTHS = [8, 32, 32, 50, 18, 12, 18]
PDF_BUDGETS = [3, 24, 24, 38, 10, 3, 12]


def _clean(value) -> str:
    if value is None:
        return ""
    text = str(value)
    return text.encode("latin-1", errors="replace").decode("latin-1")


def _truncate(text: str, max_len: int) -> str:
    text = _clean(text)
    if len(text) <= max_len:
        return text
    if max_len <= 3:
        return text[:max_len]
    return text[: max_len - 3] + "..."


def _hop_rows(path: list) -> list:
    rows = []
    for hop in path:
        rows.append(
            [
                str(hop.get("hop_number", "")),
                _truncate(hop.get("from_wallet"), PDF_BUDGETS[1]),
                _truncate(hop.get("to_wallet"), PDF_BUDGETS[2]),
                _truncate(hop.get("txid"), PDF_BUDGETS[3]),
                "%.6f" % (hop.get("amount") or 0),
                str(hop.get("risk_score", 0)),
                _truncate(hop.get("vasp_match"), PDF_BUDGETS[6]),
            ]
        )
    return rows


def _risk_breakdown(trace_result: dict) -> list:
    breakdown = trace_result.get("risk_breakdown")
    if breakdown:
        return breakdown
    path = trace_result.get("path", [])
    return [
        {
            "wallet": hop.get("wallet") or hop.get("to_wallet"),
            "risk_score": hop.get("risk_score", 0),
            "reasons": hop.get("reasons", []),
        }
        for hop in path
    ]


class ForensicReportPDF(FPDF):
    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.cell(
            0,
            10,
            "%s  |  Page %d" % (PDF_FOOTER, self.page_no()),
            align="C",
        )


def generate_json(trace_result: dict, out_dir=REPORTS_DIR) -> str:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    wallet = trace_result.get("wallet_address", "unknown")
    ts = int(trace_result.get("traced_at", time.time()))
    path = out_dir / f"{wallet}_{ts}.json"
    path.write_text(json.dumps(trace_result, indent=2), encoding="utf-8")
    return str(path)


def generate_pdf(trace_result: dict, out_dir=REPORTS_DIR) -> str:
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    wallet = trace_result.get("wallet_address", "unknown")
    ts = int(trace_result.get("traced_at", time.time()))

    pdf = ForensicReportPDF()
    pdf.set_auto_page_break(auto=True, margin=18)
    pdf.add_page()

    pdf.set_font("helvetica", "B", 16)
    pdf.cell(0, 10, PDF_HEADER, align="C", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(2)

    pdf.set_font("helvetica", "", 10)
    pdf.cell(
        0,
        6,
        "Wallet under investigation: %s" % _clean(trace_result.get("wallet_address")),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.cell(
        0,
        6,
        "Trace timestamp: %s" % _clean(time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(trace_result.get("traced_at", time.time())))),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.cell(
        0,
        6,
        "Merkle root: %s" % _clean(trace_result.get("merkle_root")),
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(4)

    pdf.set_font("helvetica", "B", 8)
    for col, width in zip(PDF_COLUMNS, PDF_WIDTHS):
        pdf.cell(width, 7, col, border=1, align="C")
    pdf.ln()

    pdf.set_font("helvetica", "", 8)
    for row in _hop_rows(trace_result.get("path", [])):
        for cell_text, width in zip(row, PDF_WIDTHS):
            pdf.cell(width, 7, cell_text, border=1)
        pdf.ln()

    pdf.ln(4)
    pdf.set_font("helvetica", "B", 10)
    pdf.cell(0, 7, "Risk Score Breakdown", new_x="LMARGIN", new_y="NEXT")

    for item in _risk_breakdown(trace_result):
        pdf.set_font("helvetica", "B", 9)
        pdf.cell(
            0,
            6,
            "%s : %d/100" % (_clean(item.get("wallet")), item.get("risk_score", 0)),
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.set_font("helvetica", "", 8)
        for reason in item.get("reasons", []):
            pdf.cell(0, 5, "   - %s" % _clean(reason), new_x="LMARGIN", new_y="NEXT")

    path = out_dir / f"{wallet}_{ts}.pdf"
    pdf.output(str(path))
    return str(path)