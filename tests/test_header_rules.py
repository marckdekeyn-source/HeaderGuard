"""
Unit test untuk modul app/core/header_rules.py.

Menguji:
- analyze_headers() mendeteksi header yang ada dengan benar
- analyze_headers() mendeteksi header yang hilang dengan benar
- Normalisasi case-insensitive pada key header
- Nilai (value) header tersimpan dengan benar
"""

import pytest
from app.core.header_rules import analyze_headers, SECURITY_HEADERS


class TestAnalyzeHeaders:

    def test_detects_present_headers(self):
        """Header yang ada di response harus terdeteksi present=True."""
        mock_response = {
            "strict-transport-security": "max-age=31536000; includeSubDomains",
            "content-security-policy": "default-src 'self'",
            "x-frame-options": "DENY",
        }
        result = analyze_headers(mock_response)

        assert result["strict-transport-security"]["present"] is True
        assert result["content-security-policy"]["present"] is True
        assert result["x-frame-options"]["present"] is True

    def test_detects_missing_headers(self):
        """Header yang tidak ada di response harus terdeteksi present=False."""
        mock_response = {
            "content-type": "text/html",
            "date": "Wed, 01 Jul 2026 00:00:00 GMT",
        }
        result = analyze_headers(mock_response)

        assert result["strict-transport-security"]["present"] is False
        assert result["content-security-policy"]["present"] is False
        assert result["x-frame-options"]["present"] is False

    def test_case_insensitive_detection(self):
        """
        HTTP header bersifat case-insensitive.
        'Strict-Transport-Security' harus sama dengan 'strict-transport-security'.
        """
        mock_response = {
            "Strict-Transport-Security": "max-age=31536000",
            "X-Frame-Options": "DENY",
            "Content-Security-Policy": "default-src 'self'",
        }
        result = analyze_headers(mock_response)

        assert result["strict-transport-security"]["present"] is True
        assert result["x-frame-options"]["present"] is True
        assert result["content-security-policy"]["present"] is True

    def test_header_value_stored_correctly(self):
        """Nilai header yang present harus tersimpan dengan benar."""
        hsts_value = "max-age=31536000; includeSubDomains; preload"
        mock_response = {
            "strict-transport-security": hsts_value,
        }
        result = analyze_headers(mock_response)

        assert result["strict-transport-security"]["value"] == hsts_value

    def test_missing_header_value_is_none(self):
        """Header yang tidak ada harus punya value=None."""
        mock_response = {}
        result = analyze_headers(mock_response)

        assert result["strict-transport-security"]["value"] is None
        assert result["content-security-policy"]["value"] is None

    def test_result_contains_all_eight_headers(self):
        """
        Hasil analisis harus selalu berisi tepat 8 header,
        tidak peduli berapa banyak header yang ada di response.
        """
        mock_response = {"content-type": "text/html"}
        result = analyze_headers(mock_response)

        assert len(result) == len(SECURITY_HEADERS)
        for key in SECURITY_HEADERS:
            assert key in result

    def test_result_contains_required_fields(self):
        """Setiap entry hasil analisis harus punya semua field yang dibutuhkan."""
        result = analyze_headers({})
        required_fields = {"name", "description", "severity", "present", "value"}

        for header_key, header_data in result.items():
            assert required_fields.issubset(header_data.keys()), \
                f"Header '{header_key}' missing required fields"

    def test_severity_values_are_valid(self):
        """Semua severity harus bernilai salah satu dari: high, medium, low."""
        result = analyze_headers({})
        valid_severities = {"high", "medium", "low"}

        for header_key, header_data in result.items():
            assert header_data["severity"] in valid_severities, \
                f"Header '{header_key}' has invalid severity: {header_data['severity']}"

    def test_empty_response_headers(self):
        """Response header kosong tidak boleh menyebabkan crash."""
        result = analyze_headers({})
        assert len(result) == 8
        for header_data in result.values():
            assert header_data["present"] is False