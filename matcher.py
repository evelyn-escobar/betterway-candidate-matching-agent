import re
import unicodedata


def normalize(text):
    """Pasa a minúsculas y quita tildes para comparar textos sin importar el formato."""

    text = unicodedata.normalize("NFKD", text.lower())

    return "".join(c for c in text if not unicodedata.combining(c))


def contains_term(text, term):
    """True si el término aparece como palabra o frase completa (evita que 'sap' coincida con 'sapiens')."""

    pattern = r"(?<![a-z0-9])" + re.escape(normalize(term)) + r"(?![a-z0-9])"

    return re.search(pattern, text) is not None


def score_job(candidate_text, skills):
    """Calcula el puntaje (0-100) ponderado por el peso de cada habilidad encontrada."""

    text = normalize(candidate_text)

    matched, missing = [], []

    for skill in skills:

        if any(contains_term(text, alias) for alias in skill["aliases"]):
            matched.append(skill["name"])
        else:
            missing.append(skill["name"])

    total_weight = sum(skill["weight"] for skill in skills)

    matched_weight = sum(skill["weight"] for skill in skills if skill["name"] in matched)

    score = round(matched_weight * 100 / total_weight) if total_weight else 0

    return {"score": score, "matched": matched, "missing": missing}


def classify(scores, threshold):
    """Recomienda los cargos cuyo puntaje alcanza el umbral: 'A', 'B', 'Both' o 'Neither'."""

    fits = [job for job, result in scores.items() if result["score"] >= threshold]

    if len(fits) > 1:
        return "Both"

    if fits:
        return fits[0]

    return "Neither"


def classify_candidate(candidate_text, jobs, threshold):
    """Evalúa un candidato contra todos los cargos configurados."""

    scores = {job_id: score_job(candidate_text, job["skills"]) for job_id, job in jobs.items()}

    return {"scores": scores, "classification": classify(scores, threshold)}
