"""
Unit test untuk modul app/core/scoring.py.

Menguji:
- calculate_score() dengan berbagai kombinasi header
- get_grade() untuk semua threshold grade
- get_grade_color() untuk semua grade yang valid
"""

import pytest
from app.core.scoring import calculate_score, get_grade, get_grade_color


# ============================================================
# Helper: factory function untuk membuat mock analysis dict
# ============================================================

def make_analysis(present_headers: list[str]) -> dict:
    """
    Membuat mock analysis dictionary untuk keperluan testing.
    Hanya header yang ada di present_headers yang akan di-set present=True.

    Args:
        present_headers: list nama header key yang dianggap 'present'

    Returns:
        dict yang strukturnya sama persis dengan output analyze_headers()
    """
    all_headers = {
        "strict-transport-security": "high",
        "content-security-policy":   "high",
        "x-frame-options":           "medium",
        "x-content-type-options":    "medium",
        "referrer-policy":           "low",
        "permissions-policy":        "low",
        "cross-origin-opener-policy": "medium",
        "cross-origin-resource-policy": "medium",
    }

    return {
        key: {
            "name": key,
            "description": "test",
            "severity": severity,
            "present": key in present_headers,
            "value": "test-value" if key in present_headers else None,
        }
        for key, severity in all_headers.items()
    }


# ============================================================
# Test: calculate_score()
# ============================================================

class TestCalculateScore:

    def test_score_all_headers_present(self):
        """Semua header hadir → skor maksimal 100."""
        analysis = make_analysis([
            "strict-transport-security",
            "content-security-policy",
            "x-frame-options",
            "x-content-type-options",
            "referrer-policy",
            "permissions-policy",
            "cross-origin-opener-policy",
            "cross-origin-resource-policy",
        ])
        assert calculate_score(analysis) == 100

    def test_score_no_headers_present(self):
        """Tidak ada header hadir → skor 0."""
        analysis = make_analysis([])
        assert calculate_score(analysis) == 0

    def test_score_only_high_severity(self):
        """
        Hanya header high severity yang hadir.
        HSTS (20) + CSP (20) = 40.
        """
        analysis = make_analysis([
            "strict-transport-security",
            "content-security-policy",
        ])
        assert calculate_score(analysis) == 40

    def test_score_only_medium_severity(self):
        """
        Hanya header medium severity yang hadir.
        4 header × 12.5 = 50.
        """
        analysis = make_analysis([
            "x-frame-options",
            "x-content-type-options",
            "cross-origin-opener-policy",
            "cross-origin-resource-policy",
        ])
        assert calculate_score(analysis) == 50

    def test_score_only_low_severity(self):
        """
        Hanya header low severity yang hadir.
        2 header × 5 = 10.
        """
        analysis = make_analysis([
            "referrer-policy",
            "permissions-policy",
        ])
        assert calculate_score(analysis) == 10

    def test_score_github_like(self):
        """
        Simulasi hasil GitHub.com dari observasi kita sebelumnya:
        HSTS + CSP + X-Frame + X-Content-Type + Referrer = 70.
        """
        analysis = make_analysis([
            "strict-transport-security",
            "content-security-policy",
            "x-frame-options",
            "x-content-type-options",
            "referrer-policy",
        ])
        assert calculate_score(analysis) == 70

    def test_score_returns_integer(self):
        """Skor harus selalu integer, bukan float."""
        analysis = make_analysis(["x-frame-options"])
        result = calculate_score(analysis)
        assert isinstance(result, int)

    def test_score_empty_analysis(self):
        """Analysis dict kosong → skor 0, tidak crash."""
        assert calculate_score({}) == 0


# ============================================================
# Test: get_grade()
# ============================================================

class TestGetGrade:

    def test_grade_a_plus(self):
        """Skor 95-100 → A+."""
        assert get_grade(100) == "A+"
        assert get_grade(95)  == "A+"

    def test_grade_a(self):
        """Skor 90-94 → A."""
        assert get_grade(94) == "A"
        assert get_grade(90) == "A"

    def test_grade_b(self):
        """Skor 70-89 → B."""
        assert get_grade(89) == "B"
        assert get_grade(70) == "B"

    def test_grade_c(self):
        """Skor 50-69 → C."""
        assert get_grade(69) == "C"
        assert get_grade(50) == "C"

    def test_grade_d(self):
        """Skor 30-49 → D."""
        assert get_grade(49) == "D"
        assert get_grade(30) == "D"

    def test_grade_f(self):
        """Skor 0-29 → F."""
        assert get_grade(29) == "F"
        assert get_grade(0)  == "F"

    def test_grade_boundary_values(self):
        """Test nilai batas (boundary) untuk memastikan threshold tepat."""
        # Tepat di batas A+ / A
        assert get_grade(95) == "A+"
        assert get_grade(94) == "A"
        # Tepat di batas A / B
        assert get_grade(90) == "A"
        assert get_grade(89) == "B"
        # Tepat di batas B / C
        assert get_grade(70) == "B"
        assert get_grade(69) == "C"
        # Tepat di batas C / D
        assert get_grade(50) == "C"
        assert get_grade(49) == "D"
        # Tepat di batas D / F
        assert get_grade(30) == "D"
        assert get_grade(29) == "F"


# ============================================================
# Test: get_grade_color()
# ============================================================

class TestGetGradeColor:

    def test_color_a_plus(self):
        assert get_grade_color("A+") == "emerald"

    def test_color_a(self):
        assert get_grade_color("A") == "green"

    def test_color_b(self):
        assert get_grade_color("B") == "blue"

    def test_color_c(self):
        assert get_grade_color("C") == "yellow"

    def test_color_d(self):
        assert get_grade_color("D") == "orange"

    def test_color_f(self):
        assert get_grade_color("F") == "red"

    def test_color_unknown_grade(self):
        """Grade tidak dikenal → fallback ke 'red' (fail securely)."""
        assert get_grade_color("Z") == "red"
        assert get_grade_color("")  == "red"