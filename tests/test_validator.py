"""
Unit test untuk modul app/services/validator.py.

Menguji:
- is_valid_url() untuk berbagai format URL valid dan invalid
- is_private_host() untuk berbagai kategori hostname
"""

import pytest
from app.services.validator import is_valid_url, is_private_host


class TestIsValidUrl:

    # URL Valid
    def test_valid_https_url(self):
        assert is_valid_url("https://example.com") is True

    def test_valid_http_url(self):
        assert is_valid_url("http://example.com") is True

    def test_valid_url_with_path(self):
        assert is_valid_url("https://example.com/path/to/page") is True

    def test_valid_url_with_query(self):
        assert is_valid_url("https://example.com?q=search&page=1") is True

    def test_valid_url_with_port(self):
        assert is_valid_url("https://example.com:8080") is True

    def test_valid_url_with_subdomain(self):
        assert is_valid_url("https://sub.example.com") is True

    def test_valid_url_github(self):
        assert is_valid_url("https://github.com") is True

    # URL Invalid
    def test_invalid_no_scheme(self):
        """URL tanpa scheme harus ditolak."""
        assert is_valid_url("example.com") is False
        assert is_valid_url("www.example.com") is False

    def test_invalid_ftp_scheme(self):
        """Scheme selain http/https harus ditolak."""
        assert is_valid_url("ftp://example.com") is False

    def test_invalid_file_scheme(self):
        """file:// scheme harus ditolak — potensi baca file lokal."""
        assert is_valid_url("file:///etc/passwd") is False

    def test_invalid_javascript_scheme(self):
        """javascript: scheme harus ditolak — potensi XSS."""
        assert is_valid_url("javascript:alert(1)") is False

    def test_invalid_scheme_only(self):
        """Hanya scheme tanpa domain harus ditolak."""
        assert is_valid_url("https://") is False
        assert is_valid_url("http://") is False

    def test_invalid_empty_string(self):
        assert is_valid_url("") is False

    def test_invalid_random_string(self):
        assert is_valid_url("not a url at all") is False

    def test_invalid_ip_with_file_scheme(self):
        assert is_valid_url("file://192.168.1.1") is False


class TestIsPrivateHost:

    def test_localhost_is_private(self):
        """localhost harus diblokir."""
        assert is_private_host("localhost") is True

    def test_loopback_ip_is_private(self):
        """127.x.x.x harus diblokir."""
        assert is_private_host("127.0.0.1") is True
        assert is_private_host("127.0.0.2") is True

    def test_private_class_a_is_blocked(self):
        """10.x.x.x range harus diblokir."""
        assert is_private_host("10.0.0.1") is True
        assert is_private_host("10.255.255.255") is True

    def test_private_class_b_is_blocked(self):
        """172.16.x.x - 172.31.x.x range harus diblokir."""
        assert is_private_host("172.16.0.1") is True
        assert is_private_host("172.31.255.255") is True

    def test_private_class_c_is_blocked(self):
        """192.168.x.x range harus diblokir."""
        assert is_private_host("192.168.1.1") is True
        assert is_private_host("192.168.0.1") is True

    def test_link_local_is_blocked(self):
        """
        169.254.x.x (link-local) harus diblokir.
        Ini adalah range AWS metadata endpoint yang sering dieksploitasi via SSRF.
        """
        assert is_private_host("169.254.169.254") is True

    def test_nonexistent_domain_is_blocked(self):
        """
        Domain yang tidak bisa di-resolve harus diblokir.
        Prinsip fail securely: kalau tidak bisa verifikasi, tolak.
        """
        assert is_private_host("domain-yang-pasti-tidak-ada-xyzabc123.com") is True

    def test_public_domain_is_allowed(self):
        """Domain publik yang valid harus diizinkan."""
        assert is_private_host("github.com") is False
        assert is_private_host("google.com") is False
        assert is_private_host("cloudflare.com") is False