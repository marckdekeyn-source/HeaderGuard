"""
Modul ini bertanggung jawab menghitung security score dan grade
berdasarkan hasil analisis header dari header_rules.py.

Tidak mengimpor apa pun dari FastAPI atau layer lain —
ini adalah pure business logic yang bisa ditest secara independen.
"""

SEVERITY_WEIGHTS = {
    "high": 20,
    "medium": 12.5,
    "low": 5,
}

GRADE_THRESHOLDS = [
    (95, "A+"),
    (90, "A"),
    (70, "B"),
    (50, "C"),
    (30, "D"),
    (0,  "F"),
]


def calculate_score(analysis: dict) -> int:
    """
    Menghitung total security score (0-100) berdasarkan
    header mana saja yang present, dikalikan bobot severity-nya.
    """
    total_score = 0.0

    for header_key, header_data in analysis.items():
        if header_data["present"]:
            weight = SEVERITY_WEIGHTS.get(header_data["severity"], 0)
            total_score += weight

    return round(total_score)


def get_grade(score: int) -> str:
    """
    Mengonversi skor numerik menjadi grade huruf (A+ sampai F).
    """
    for threshold, grade in GRADE_THRESHOLDS:
        if score >= threshold:
            return grade
    return "F"


def get_grade_color(grade: str) -> str:
    """
    Mengembalikan nama warna Tailwind sesuai grade,
    untuk dipakai di frontend saat merender hasil.
    """
    colors = {
        "A+": "emerald",
        "A":  "green",
        "B":  "blue",
        "C":  "yellow",
        "D":  "orange",
        "F":  "red",
    }
    return colors.get(grade, "red")