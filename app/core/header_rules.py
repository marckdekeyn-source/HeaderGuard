"""
Modul ini mendefinisikan daftar security header yang dianalisis HeaderGuard,
beserta deskripsi dan tingkat kepentingannya (severity) jika header tersebut hilang.
"""

SECURITY_HEADERS = {
    "strict-transport-security": {
        "name": "Strict-Transport-Security (HSTS)",
        "description": "Forces browsers to use HTTPS, preventing man-in-the-middle attacks.",
        "severity": "high",
    },
    "content-security-policy": {
        "name": "Content-Security-Policy (CSP)",
        "description": "Restricts sources of scripts/styles, mitigating XSS attacks.",
        "severity": "high",
    },
    "x-frame-options": {
        "name": "X-Frame-Options",
        "description": "Prevents the page from being embedded in iframes, mitigating clickjacking.",
        "severity": "medium",
    },
    "x-content-type-options": {
        "name": "X-Content-Type-Options",
        "description": "Prevents MIME type sniffing by browsers.",
        "severity": "medium",
    },
    "referrer-policy": {
        "name": "Referrer-Policy",
        "description": "Controls how much referrer information is shared when navigating away.",
        "severity": "low",
    },
    "permissions-policy": {
        "name": "Permissions-Policy",
        "description": "Restricts which browser features (camera, mic, geolocation) can be used.",
        "severity": "low",
    },
    "cross-origin-opener-policy": {
        "name": "Cross-Origin-Opener-Policy (COOP)",
        "description": "Isolates browsing context from cross-origin windows, mitigating side-channel attacks.",
        "severity": "medium",
    },
    "cross-origin-resource-policy": {
        "name": "Cross-Origin-Resource-Policy (CORP)",
        "description": "Controls whether resources can be loaded by other origins.",
        "severity": "medium",
    },
}


def analyze_headers(response_headers: dict) -> dict:
    """
    Membandingkan response header website target dengan daftar SECURITY_HEADERS.
    Mengembalikan dict berisi status 'present' atau 'missing' untuk setiap header.
    """
    normalized_headers = {key.lower(): value for key, value in response_headers.items()}

    result = {}
    for header_key, header_info in SECURITY_HEADERS.items():
        is_present = header_key in normalized_headers

        result[header_key] = {
            **header_info,
            "present": is_present,
            "value": normalized_headers.get(header_key, None),
        }

    return result