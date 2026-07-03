"""
Unit test untuk modul app/core/recommendations.py.

Menguji:
- generate_recommendations() hanya menghasilkan rekomendasi untuk header missing
- Urutan rekomendasi dari severity tertinggi ke terendah
- Struktur field setiap rekomendasi
- Kasus edge: semua header present, tidak ada header present
"""

import pytest
from app.core.recommendations import generate_recommendations


def make_analysis(present_headers: list[str]) -> dict:
    """Helper: buat mock analysis dict."""
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
            "value": None,
        }
        for key, severity in all_headers.items()
    }


class TestGenerateRecommendations:

    def test_no_recommendations_when_all_present(self):
        """Semua header hadir → tidak ada rekomendasi."""
        analysis = make_analysis(list({
            "strict-transport-security",
            "content-security-policy",
            "x-frame-options",
            "x-content-type-options",
            "referrer-policy",
            "permissions-policy",
            "cross-origin-opener-policy",
            "cross-origin-resource-policy",
        }))
        result = generate_recommendations(analysis)
        assert result == []

    def test_all_headers_missing_generates_eight_recommendations(self):
        """Semua header hilang → 8 rekomendasi."""
        analysis = make_analysis([])
        result = generate_recommendations(analysis)
        assert len(result) == 8

    def test_only_missing_headers_get_recommendations(self):
        """Hanya header yang missing yang mendapat rekomendasi."""
        present = [
            "strict-transport-security",
            "content-security-policy",
            "x-frame-options",
        ]
        analysis = make_analysis(present)
        result = generate_recommendations(analysis)

        # 8 total - 3 present = 5 rekomendasi
        assert len(result) == 5

        # Header yang present tidak boleh muncul di rekomendasi
        rec_headers = [r["header"] for r in result]
        for p in present:
            assert p not in rec_headers

    def test_recommendations_sorted_by_severity(self):
        """
        Rekomendasi harus diurutkan: high → medium → low.
        High severity harus muncul sebelum medium dan low.
        """
        analysis = make_analysis([])
        result = generate_recommendations(analysis)

        severity_order = {"high": 0, "medium": 1, "low": 2}
        orders = [severity_order[r["severity"]] for r in result]

        assert orders == sorted(orders), \
            "Recommendations are not sorted from high to low severity"

    def test_recommendation_has_required_fields(self):
        """Setiap rekomendasi harus punya semua field yang dibutuhkan frontend."""
        analysis = make_analysis([])
        result = generate_recommendations(analysis)

        required_fields = {
            "header", "severity", "title",
            "description", "fix", "fix_description", "references"
        }

        for rec in result:
            assert required_fields.issubset(rec.keys()), \
                f"Recommendation missing fields: {required_fields - rec.keys()}"

    def test_high_severity_recommendations_appear_first(self):
        """Header high severity harus selalu muncul di posisi paling atas."""
        analysis = make_analysis([])
        result = generate_recommendations(analysis)

        if len(result) > 0:
            assert result[0]["severity"] == "high"

    def test_recommendation_references_is_valid_url(self):
        """Field references harus berisi URL yang valid (dimulai dengan https://)."""
        analysis = make_analysis([])
        result = generate_recommendations(analysis)

        for rec in result:
            assert rec["references"].startswith("https://"), \
                f"Invalid reference URL: {rec['references']}"