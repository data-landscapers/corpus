#!/usr/bin/env python3
"""test_staged_queue.py — prove the staged-queue checks fire, and on what.

`lint-staged-queue.py` is a check that will read `clean` for whole batches at a
time, and a check that has only ever passed is not evidence of anything. What it
guards is the defect that costs most and shows least: a staged file carrying
another document's body under correct frontmatter, a correct `url:` and a
correct filename, whose `note:` is therefore a finding derived from the wrong
document under a citation that checks out.

Each case builds a synthetic batch in a temp directory and asserts the severities
the linter returns. The batch is small on purpose — under twenty files the
document-frequency narrowing is skipped by design, so these cases exercise the
signals rather than the batch statistics, and the GNB batch is the evidence for
the statistics half.

    python scripts/test_staged_queue.py
"""

from __future__ import annotations

import importlib.util
import io
import sys
import tempfile
from contextlib import redirect_stdout
from pathlib import Path

_here = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("lsq", _here / "lint-staged-queue.py")
lsq = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(lsq)


def stage(root: Path, name: str, *, title: str, url: str, publisher: str,
          body: str, published: str = "", note: str = "") -> Path:
    published = published or name[:10]
    fm = [
        "---", "type: source", f'title: "{title}"', f"url: {url}",
        f'publisher: "{publisher}"', f"published: {published}",
        "places: [GNB]", "topics: [dpi.id]", "retrieved: 2026-08-27",
        "sweep_batch: progress-filler-TST-2026-08-27",
        "body_completeness: full",
    ]
    if note:
        fm.append(f"note: {note}")
    fm.append("---")
    p = root / name
    p.write_text("\n".join(fm) + "\n\n" + body, encoding="utf-8")
    return p


def run(root: Path, checks: str = ",".join(lsq.ALL_CHECKS)) -> tuple[int, str]:
    buf = io.StringIO()
    argv = sys.argv
    sys.argv = ["lint-staged-queue.py", str(root), "--checks", checks]
    try:
        with redirect_stdout(buf):
            code = lsq.main()
    finally:
        sys.argv = argv
    return code, buf.getvalue()


def severities(out: str) -> dict[str, str]:
    got = {}
    for line in out.splitlines():
        parts = line.split()
        if len(parts) == 2 and parts[0] in (
            "MISFILED", "CROSSED", "SUSPECT", "YAML", "DATE", "TITLE"
        ):
            got[parts[1]] = parts[0]
    return got


def case_clean(root: Path) -> None:
    stage(root, "2025-03-18-bceao-instruction-kyc.md",
          title="Instruction relative à l'identification de la clientèle",
          url="https://www.bceao.int/sites/default/files/instruction-kyc.pdf",
          publisher="Banque Centrale des États de l'Afrique de l'Ouest (BCEAO)",
          body="URL: https://www.bceao.int/sites/default/files/instruction-kyc.pdf\n\n"
               "## Instruction relative à l'identification de la clientèle\n\n"
               "La BCEAO fixe les règles d'identification de la clientèle des "
               "établissements de paiement.\n")
    code, out = run(root)
    assert code == 0, out
    assert "clean" in out, out


def case_misfiled(root: Path) -> None:
    """The exact check: the body's own `URL:` line names another document."""
    stage(root, "2022-01-01-unctad-asycuda-compendium.md",
          title="ASYCUDA Compendium 2022",
          url="https://asycuda.org/wp-content/uploads/ASYCUDA_Compendium_2022.pdf",
          publisher="UNCTAD",
          body="URL: https://www.ecreee.org/mini-redes-desert-to-power/\n\n"
               "# Guiné-Bissau valida estudo de mini-redes\n\n"
               "O ECREEE apresentou o estudo de mini-redes em Bissau.\n")
    stage(root, "2026-03-18-ecreee-mini-redes.md",
          title="Guiné-Bissau valida estudo de mini-redes",
          url="https://www.ecreee.org/mini-redes-desert-to-power/",
          publisher="ECREEE",
          body="URL: https://www.ecreee.org/mini-redes-desert-to-power/\n\n"
               "# Guiné-Bissau valida estudo de mini-redes\n\n"
               "O ECREEE apresentou o estudo de mini-redes em Bissau.\n")
    code, out = run(root, "url")
    assert code == 1, out
    got = severities(out)
    assert got == {"2022-01-01-unctad-asycuda-compendium.md": "MISFILED"}, got
    # the counterpart is named, which is what makes the finding actionable
    assert "belongs to 2026-03-18-ecreee-mini-redes.md" in out, out


def case_crossed_without_url_line(root: Path) -> None:
    """No `URL:` line: title, host, publisher and heading have to carry it, and
    the counterpart search names the file the body belongs to. A swap is the
    shape it names best, and GNB had one — the ASYCUDA compendium and the ECREEE
    mini-grids article held each other's bodies."""
    arn = "# Relatório de Actividades 2021\n\n" + (
        "A Autoridade Reguladora Nacional publica o seu relatório anual de "
        "actividades para 2021, com dados sobre o mercado das telecomunicações, "
        "o parque de assinantes e as receitas do sector.\n\n") * 10
    sdg7 = "# The Energy Progress Report\n\n" + (
        "Tracking SDG 7 reports on progress towards universal access to "
        "electricity and clean cooking, on renewables and on energy "
        "efficiency, country by country.\n\n") * 10
    stage(root, "2025-06-25-tracking-sdg7-energy-progress.md",
          title="Tracking SDG 7: The Energy Progress Report 2025",
          url="https://trackingsdg7.esmap.org/downloads/SDG7-Report2025.pdf",
          publisher="ESMAP", body=arn)
    stage(root, "2021-01-01-arn-relatorio-actividades.md",
          title="Relatório de Actividades 2021",
          url="https://arn.gw/uploads/ARN-Relatorio-2021.pdf",
          publisher="Autoridade Reguladora Nacional (ARN)", body=sdg7)
    code, out = run(root, "body")
    assert code == 1, out
    got = severities(out)
    assert got.get("2025-06-25-tracking-sdg7-energy-progress.md") == "CROSSED", got
    assert got.get("2021-01-01-arn-relatorio-actividades.md") == "CROSSED", got
    assert "on 2021-01-01-arn-relatorio-actividades.md" in out, out
    assert "on 2025-06-25-tracking-sdg7-energy-progress.md" in out, out


def case_source_signal_does_not_outrank_a_blank_title(root: Path) -> None:
    """The GNB miss: a body citing the frontmatter's host does not clear a title
    that scores flat zero on it."""
    stage(root, "2023-04-01-wardip-qgas-p176932.md",
          title="Quadro de Gestão Ambiental e Social (QGAS) — Projecto WARDIP",
          url="https://documents1.worldbank.org/curated/en/txt/P1769320801.txt",
          publisher="Ministério dos Transportes / World Bank",
          body="# The affordability of ICT services\n\nITU Publications. This "
               "report is produced with support from the World Bank and "
               "measures price baskets across 190 economies.\n")
    code, out = run(root, "body")
    assert code == 1, out
    assert severities(out).get("2023-04-01-wardip-qgas-p176932.md") in (
        "SUSPECT", "CROSSED"), out


def case_heading_does_not_raise_its_own_doubt(root: Path) -> None:
    """Seven GNB files opened on an OCR artefact or a document number over a body
    that matched its own title. The heading breaks ties; it does not raise them."""
    stage(root, "2022-01-01-worldbank-digital-economy-assessment.md",
          title="Guinea-Bissau Digital Economy Country Assessment",
          url="https://documents1.worldbank.org/curated/en/txt/P177016.txt",
          publisher="World Bank",
          body="# P177016084979202b08dd501a5690c82506\n\nGuinea-Bissau Digital "
               "Economy Country Assessment. This assessment reviews the digital "
               "economy of Guinea-Bissau across five foundational pillars.\n")
    code, out = run(root, "body")
    assert code == 0, out


def case_short_body_is_suspect_not_crossed(root: Path) -> None:
    """A ten-line postal profile cannot be expected to repeat its own title."""
    stage(root, "2005-03-01-upu-postal-addressing-profile.md",
          title="Guinea-Bissau — UPU postal addressing profile",
          url="https://www.upu.int/PostalEntitiesFiles/gnbEn.pdf",
          publisher="Universal Postal Union",
          body="Author: Piotrowskip\n\nPostcode 4 digits to the left of the "
               "locality name.\nExample: Rua Justino Lopes 12C 1000 BISSAU\n")
    code, out = run(root, "body")
    assert code == 1, out
    assert severities(out) == {
        "2005-03-01-upu-postal-addressing-profile.md": "SUSPECT"}, out


def case_date_yaml_title(root: Path) -> None:
    stage(root, "2023-uneca-dtri-country-profile.md",  # partial date prefix
          title="DTRI country profile",
          url="https://www.uneca.org/dtri/gnb.pdf", publisher="UNECA",
          published="2023-01-01",
          body="# DTRI country profile\n\nThe UNECA digital trade regulatory "
               "integration profile for the country.\n")
    stage(root, "2025-12-03-dgci-instrucao-servico.md",
          title="Instrucao de Servico 25/2025",
          url="https://kontaktu.mef.gw/instrucao-25-2025",
          publisher="Direcção-Geral das Contribuições e Impostos (DGCI)",
          note='Assunto: o NIF passa a ser obrigatorio',  # unquoted `": "`
          body="# Instrução de Serviço 25/2025\n\nA Direcção-Geral das "
               "Contribuições e Impostos emite a presente Instrução de "
               "Serviço.\n")
    code, out = run(root, "date,yaml,title")
    assert code == 1, out
    got = severities(out)
    assert got.get("2023-uneca-dtri-country-profile.md") == "DATE", got
    assert got.get("2025-12-03-dgci-instrucao-servico.md") in ("YAML", "TITLE"), got
    assert "partial" in out, out
    # the title check names the repair the body itself evidences
    assert "`instrucao` -> `Instrução`" in out, out


def main() -> int:
    cases = [
        case_clean,
        case_misfiled,
        case_crossed_without_url_line,
        case_source_signal_does_not_outrank_a_blank_title,
        case_heading_does_not_raise_its_own_doubt,
        case_short_body_is_suspect_not_crossed,
        case_date_yaml_title,
    ]
    failed = 0
    for case in cases:
        with tempfile.TemporaryDirectory() as tmp:
            try:
                case(Path(tmp))
                print(f"  ok    {case.__name__}")
            except AssertionError as exc:
                failed += 1
                print(f"  FAIL  {case.__name__}\n{exc}")
    print(f"{len(cases) - failed}/{len(cases)} passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
