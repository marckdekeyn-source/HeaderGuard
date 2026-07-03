"""
Modul ini mengorkestrasi seluruh alur proses scanning:
fetch → analyze → score → recommend.

Layer service adalah jembatan antara routing (main.py) dan
business logic (core/) serta infrastructure (clients/).
Tidak ada logika bisnis di sini — hanya koordinasi antar modul.
"""

from app.clients.http_client import fetch_headers
from app.core.header_rules import analyze_headers
from app.core.scoring import calculate_score, get_grade, get_grade_color
from app.core.recommendations import generate_recommendations
from app.schemas.scan_result import ScanResult


async def run_scan(url: str) -> ScanResult:
    """
    Menjalankan seluruh pipeline scanning untuk satu URL.

    Pipeline:
        1. Fetch HTTP headers dari URL target
        2. Analisis security headers yang ada/tidak ada
        3. Hitung security score berdasarkan severity weights
        4. Tentukan grade (F sampai A+)
        5. Generate rekomendasi untuk header yang hilang

    Args:
        url: URL target yang sudah divalidasi oleh layer routing

    Returns:
        ScanResult object berisi seluruh hasil scanning
    """
    raw_headers, final_url = await fetch_headers(url)
    analysis = analyze_headers(raw_headers)
    score = calculate_score(analysis)
    grade = get_grade(score)
    grade_color = get_grade_color(grade)
    recommendations = generate_recommendations(analysis)

    return ScanResult(
        received_url=url,
        final_url=final_url,
        status="ok",
        score=score,
        grade=grade,
        grade_color=grade_color,
        analysis=analysis,
        recommendations=recommendations,
    )