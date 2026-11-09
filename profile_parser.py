import re
from datetime import date

MONTHS = {
    "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
    "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
}

DATE_RANGE = re.compile(
    r"([A-Za-z]{3})[a-z]*\.?\s+(\d{4})\s*[-–]\s*(present|actual|presente|([A-Za-z]{3})[a-z]*\.?\s+(\d{4}))",
    re.IGNORECASE,
)


def parse_profile(text, today=None):
    """Extrae nombre, titular, ubicación y años aproximados de experiencia de un perfil."""

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    return {
        "name": lines[0] if lines else "Sin nombre",
        "headline": lines[1] if len(lines) > 1 else "",
        "location": lines[2] if len(lines) > 2 and len(lines[2]) < 60 else "",
        "years": estimate_years(text, today),
    }


def estimate_years(text, today=None):
    """Años desde el primer empleo hasta el último, según los rangos 'Mes Año - Mes Año/Present'."""

    today = today or date.today()

    starts, ends = [], []

    for start_month, start_year, end, end_month, end_year in DATE_RANGE.findall(text):

        start_m = MONTHS.get(start_month[:3].lower())

        if not start_m:
            continue

        starts.append(int(start_year) * 12 + start_m)

        if end_year:
            ends.append(int(end_year) * 12 + MONTHS.get(end_month[:3].lower(), 12))
        else:
            ends.append(today.year * 12 + today.month)

    if not starts:
        return None

    return round((max(ends) - min(starts)) / 12, 1)
