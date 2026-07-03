"""
Modul ini menangani semua validasi input sebelum proses scanning dimulai.
Memisahkan logika validasi dari routing agar mudah ditest dan dimodifikasi.
"""

import socket
import ipaddress
from urllib.parse import urlparse


PRIVATE_IP_NETWORKS = [
    ipaddress.IPv4Network("10.0.0.0/8"),
    ipaddress.IPv4Network("172.16.0.0/12"),
    ipaddress.IPv4Network("192.168.0.0/16"),
    ipaddress.IPv4Network("127.0.0.0/8"),
    ipaddress.IPv4Network("169.254.0.0/16"),
    ipaddress.IPv4Network("0.0.0.0/8"),
    ipaddress.IPv4Network("100.64.0.0/10"),
]


def is_valid_url(url: str) -> bool:
    """
    Validasi format URL: harus punya scheme (http/https)
    dan netloc (domain) yang jelas.

    Args:
        url: string URL yang akan divalidasi

    Returns:
        True jika URL valid, False jika tidak
    """
    try:
        result = urlparse(url)
        return all([
            result.scheme in ("http", "https"),
            result.netloc != ""
        ])
    except ValueError:
        return False


def is_private_host(hostname: str) -> bool:
    """
    Mengecek apakah hostname mengarah ke IP private/internal.
    Mencegah SSRF attack — penyerang tidak bisa memakai HeaderGuard
    sebagai proxy untuk mengakses jaringan internal server kita.

    Args:
        hostname: nama domain atau IP yang akan dicek

    Returns:
        True jika HOST BERBAHAYA (harus ditolak), False jika aman
    """
    try:
        ip_str = socket.gethostbyname(hostname)
        ip_obj = ipaddress.IPv4Address(ip_str)
        return any(ip_obj in network for network in PRIVATE_IP_NETWORKS)
    except (socket.gaierror, ValueError, OSError):
        return True