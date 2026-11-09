import argparse
import json
import os

from matcher import classify_candidate
from pdf_reader import read_pdf
from profile_parser import parse_profile
from report_generator import generate_csv, generate_html, generate_markdown


def load_config(path):

    with open(path, encoding="utf-8") as f:
        return json.load(f)


def analyze(candidates_folder, config):
    """Lee cada PDF de candidatos, lo evalúa contra los cargos y ordena los resultados."""

    jobs = config["jobs"]

    threshold = config["fit_threshold"]

    results = []

    for file in sorted(os.listdir(candidates_folder)):

        if not file.lower().endswith(".pdf"):
            continue

        text = read_pdf(os.path.join(candidates_folder, file))

        if not text.strip():
            print(f"Aviso: no se pudo leer texto de {file}")
            continue

        result = classify_candidate(text, jobs, threshold)

        result["file"] = file

        result["profile"] = parse_profile(text)

        results.append(result)

    # Primero los de mejor coincidencia en su mejor cargo
    results.sort(key=lambda r: max(s["score"] for s in r["scores"].values()), reverse=True)

    return results


def main():

    parser = argparse.ArgumentParser(description="Evalúa perfiles de candidatos contra las vacantes configuradas.")
    parser.add_argument("--candidates", default="input/candidates", help="carpeta con los PDF de candidatos")
    parser.add_argument("--config", default="config.json", help="archivo con cargos, habilidades y pesos")
    parser.add_argument("--output", default="output", help="carpeta donde se guardan los reportes")
    args = parser.parse_args()

    config = load_config(args.config)

    results = analyze(args.candidates, config)

    os.makedirs(args.output, exist_ok=True)

    reports = {
        "report.md": generate_markdown(results, config["jobs"], config["fit_threshold"]),
        "report.csv": generate_csv(results, config["jobs"]),
        "report.html": generate_html(results, config["jobs"], config["fit_threshold"]),
    }

    for name, content in reports.items():

        # El CSV lleva BOM para que Excel muestre bien las tildes
        encoding = "utf-8-sig" if name.endswith(".csv") else "utf-8"

        with open(os.path.join(args.output, name), "w", encoding=encoding, newline="") as f:
            f.write(content)

    print(f"{len(results)} candidatos analizados. Reportes en '{args.output}/': report.md, report.csv y report.html")


if __name__ == "__main__":
    main()
