import csv
import html
import io
from datetime import date


def recommendation(result, jobs):
    """Texto de recomendación según la clasificación del candidato."""

    classification = result["classification"]

    if classification == "Both":
        return "Puede considerarse para ambos cargos."

    if classification == "Neither":
        return "Baja coincidencia con los cargos actuales."

    return f"Mejor perfil para {jobs[classification]['title']}."


def label(classification, jobs):

    if classification == "Both":
        return "Ambos cargos"

    if classification == "Neither":
        return "Ninguno"

    return jobs[classification]["title"]


def summary(results, jobs):

    counts = {job_id: 0 for job_id in jobs}
    counts.update({"Both": 0, "Neither": 0})

    for result in results:
        counts[result["classification"]] += 1

    return counts


def generate_markdown(results, jobs, threshold):
    """Reporte en Markdown, ordenado de mayor a menor coincidencia."""

    counts = summary(results, jobs)

    lines = [
        "# BetterWay – Reporte de coincidencia de candidatos",
        "",
        f"Generado el {date.today().isoformat()} · Umbral de recomendación: {threshold}%",
        "",
        "## Resumen",
        "",
        f"- **Candidatos analizados:** {len(results)}",
    ]

    for job_id, job in jobs.items():
        lines.append(f"- **Recomendados para {job['title']}:** {counts[job_id]}")

    lines += [
        f"- **Recomendados para ambos cargos:** {counts['Both']}",
        f"- **Sin coincidencia suficiente:** {counts['Neither']}",
        "",
        "## Ranking",
        "",
        "| # | Candidato | " + " | ".join(f"Cargo {job_id}" for job_id in jobs) + " | Recomendación |",
        "|---|---|" + "---|" * len(jobs) + "---|",
    ]

    for position, result in enumerate(results, start=1):

        scores = " | ".join(f"{result['scores'][job_id]['score']}%" for job_id in jobs)

        lines.append(
            f"| {position} | {result['profile']['name']} | {scores} | {label(result['classification'], jobs)} |"
        )

    lines += ["", "## Detalle por candidato", ""]

    for result in results:

        profile = result["profile"]

        lines.append(f"### {profile['name']}")
        lines.append("")

        if profile["headline"]:
            lines.append(f"*{profile['headline']}*")
            lines.append("")

        if profile["years"] is not None:
            lines.append(f"- **Experiencia aproximada:** {profile['years']} años")

        lines.append(f"- **Archivo:** {result['file']}")

        for job_id, job in jobs.items():

            score = result["scores"][job_id]

            lines.append(f"- **{job['title']}:** {score['score']}%")
            lines.append(f"  - Tiene: {', '.join(score['matched']) or '—'}")
            lines.append(f"  - Le falta: {', '.join(score['missing']) or '—'}")

        lines.append(f"- **Recomendación:** {recommendation(result, jobs)}")
        lines.append("")

    return "\n".join(lines) + "\n"


def generate_csv(results, jobs):
    """Tabla para abrir en Excel o Google Sheets."""

    buffer = io.StringIO()

    writer = csv.writer(buffer)

    writer.writerow(
        ["posicion", "candidato", "archivo", "experiencia_anios"]
        + [f"puntaje_{job_id}" for job_id in jobs]
        + ["recomendacion"]
    )

    for position, result in enumerate(results, start=1):

        writer.writerow(
            [position, result["profile"]["name"], result["file"], result["profile"]["years"]]
            + [result["scores"][job_id]["score"] for job_id in jobs]
            + [label(result["classification"], jobs)]
        )

    return buffer.getvalue()


def generate_html(results, jobs, threshold):
    """Reporte visual para abrir en el navegador, con barras de puntaje y búsqueda."""

    counts = summary(results, jobs)

    esc = html.escape

    cards = "".join(
        f'<div class="card"><span>{esc(job["title"])}</span><strong>{counts[job_id]}</strong></div>'
        for job_id, job in jobs.items()
    )

    cards += f'<div class="card"><span>Ambos cargos</span><strong>{counts["Both"]}</strong></div>'
    cards += f'<div class="card muted"><span>Sin coincidencia</span><strong>{counts["Neither"]}</strong></div>'

    rows = []

    for position, result in enumerate(results, start=1):

        profile = result["profile"]

        bars = "".join(
            f'<td><div class="bar"><div style="width:{result["scores"][job_id]["score"]}%"></div></div>'
            f'<small>{result["scores"][job_id]["score"]}%</small></td>'
            for job_id in jobs
        )

        detail = "".join(
            f'<p><b>{esc(job["title"])}:</b> tiene {esc(", ".join(result["scores"][job_id]["matched"]) or "—")}'
            f' · le falta {esc(", ".join(result["scores"][job_id]["missing"]) or "—")}</p>'
            for job_id, job in jobs.items()
        )

        years = f"{profile['years']} años" if profile["years"] is not None else "—"

        rows.append(
            f'<tr class="fila" data-tag="{result["classification"]}">'
            f'<td>{position}</td>'
            f'<td><details><summary><b>{esc(profile["name"])}</b><br><small>{esc(profile["headline"])}</small></summary>{detail}</details></td>'
            f'<td>{years}</td>{bars}'
            f'<td><span class="tag tag-{result["classification"]}">{esc(label(result["classification"], jobs))}</span></td></tr>'
        )

    headers = "".join(f"<th>{esc(job['title'])}</th>" for job in jobs.values())

    options = "".join(f'<option value="{job_id}">{esc(job["title"])}</option>' for job_id, job in jobs.items())

    return f"""<!DOCTYPE html>
<html lang="es"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>BetterWay – Reporte de candidatos</title>
<style>
body {{ font-family: "Segoe UI", Arial, sans-serif; margin: 0; background: #f4f6fb; color: #1f2937; }}
header {{ background: linear-gradient(135deg, #1d4ed8, #7c3aed); color: #fff; padding: 28px 32px; }}
header h1 {{ margin: 0 0 6px; }}
main {{ max-width: 1200px; margin: 0 auto; padding: 24px; }}
.cards {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 14px; margin-bottom: 20px; }}
.card {{ background: #fff; border-radius: 12px; padding: 16px; box-shadow: 0 2px 10px rgba(0,0,0,.06); display: flex; flex-direction: column; }}
.card strong {{ font-size: 2rem; color: #1d4ed8; }}
.card.muted strong {{ color: #6b7280; }}
.tools {{ display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 14px; }}
.tools input, .tools select {{ padding: 10px; border: 1px solid #d1d5db; border-radius: 8px; font: inherit; }}
.tools input {{ flex: 1; min-width: 200px; }}
table {{ width: 100%; border-collapse: collapse; background: #fff; border-radius: 12px; overflow: hidden; box-shadow: 0 2px 10px rgba(0,0,0,.06); }}
th, td {{ padding: 12px; text-align: left; border-bottom: 1px solid #eef0f5; vertical-align: top; }}
th {{ background: #f9fafb; font-size: .85rem; color: #4b5563; }}
summary {{ cursor: pointer; }}
details p {{ font-size: .85rem; color: #4b5563; margin: 8px 0 0; }}
.bar {{ width: 120px; height: 8px; background: #e5e7eb; border-radius: 8px; overflow: hidden; }}
.bar div {{ height: 100%; background: linear-gradient(90deg, #1d4ed8, #7c3aed); }}
.tag {{ padding: 4px 10px; border-radius: 20px; font-size: .8rem; font-weight: 600; background: #e0e7ff; color: #3730a3; }}
.tag-Both {{ background: #dcfce7; color: #166534; }}
.tag-Neither {{ background: #f3f4f6; color: #6b7280; }}
@media (max-width: 700px) {{ .bar {{ width: 70px; }} th:nth-child(3), td:nth-child(3) {{ display: none; }} }}
</style></head>
<body>
<header><h1>BetterWay – Reporte de candidatos</h1>
<p>{len(results)} candidatos analizados · Umbral de recomendación {threshold}% · {date.today().isoformat()}</p></header>
<main>
<section class="cards">{cards}</section>
<div class="tools">
  <input id="buscar" type="search" placeholder="Buscar candidato...">
  <select id="filtro"><option value="">Todas las recomendaciones</option>{options}<option value="Both">Ambos cargos</option><option value="Neither">Sin coincidencia</option></select>
</div>
<table><thead><tr><th>#</th><th>Candidato (clic para ver detalle)</th><th>Experiencia</th>{headers}<th>Recomendación</th></tr></thead>
<tbody>{"".join(rows)}</tbody></table>
</main>
<script>
const buscar = document.getElementById("buscar"), filtro = document.getElementById("filtro");
function aplicar() {{
  const q = buscar.value.toLowerCase();
  document.querySelectorAll(".fila").forEach((f) => {{
    const okTexto = f.textContent.toLowerCase().includes(q);
    const okFiltro = !filtro.value || f.dataset.tag === filtro.value || (f.dataset.tag === "Both" && filtro.value !== "Neither" && filtro.value !== "Both");
    f.style.display = okTexto && okFiltro ? "" : "none";
  }});
}}
buscar.addEventListener("input", aplicar); filtro.addEventListener("change", aplicar);
</script>
</body></html>
"""
