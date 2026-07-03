"""
Modul ini adalah wrapper untuk library httpx.
Semua detail implementasi HTTP (timeout, headers, error handling)
terisolasi di sini — layer lain tidak perlu tahu library apa yang dipakai.

Jika suatu saat kita ganti httpx dengan library lain,
hanya file ini yang perlu diubah.
"""

import httpx
from fastapi import HTTPException


BROWSER_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}


async def fetch_headers(url: str) -> tuple[dict, str]:
    """
    Mengirim HTTP GET request ke URL target dengan User-Agent browser.

    Catatan versi: httpx==0.28.x tidak punya httpx.SSLError sebagai
    exception terpisah — SSL error muncul sebagai httpx.ConnectError
    dengan pesan yang mengandung kata kunci SSL/certificate.

    Args:
        url: URL target yang sudah divalidasi

    Returns:
        Tuple (headers dict, final_url string) setelah semua redirect diikuti.

    Raises:
        HTTPException 400: untuk SSL error dan redirect loop
        HTTPException 503: untuk timeout, DNS error, dan koneksi gagal
    """
    try:
        async with httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=True,
            headers=BROWSER_HEADERS,
        ) as client:
            response = await client.get(url)
            final_url = str(response.url)
            return dict(response.headers), final_url

    except httpx.ConnectTimeout:
        raise HTTPException(
            status_code=503,
            detail=(
                "Connection timed out. The server did not respond within 10 seconds. "
                "The website may be slow or blocking automated requests."
            )
        )

    except httpx.ReadTimeout:
        raise HTTPException(
            status_code=503,
            detail=(
                "Read timed out. The server accepted the connection but did not "
                "send a response in time. Try again later."
            )
        )

    except httpx.ConnectError as e:
        error_msg = str(e).lower()

        if "ssl" in error_msg or "certificate" in error_msg or "tls" in error_msg:
            raise HTTPException(
                status_code=400,
                detail=(
                    "SSL/TLS certificate error. The website's security certificate "
                    "is invalid, expired, or self-signed. "
                    "HeaderGuard cannot scan sites with broken HTTPS configurations."
                )
            )

        if "name or service not known" in error_msg \
                or "nodename nor servname" in error_msg \
                or "getaddrinfo failed" in error_msg \
                or "dns" in error_msg \
                or "name resolution" in error_msg:
            raise HTTPException(
                status_code=503,
                detail=(
                    "DNS resolution failed. The domain could not be found. "
                    "Please check the URL for typos, or the website may no longer exist."
                )
            )

        raise HTTPException(
            status_code=503,
            detail=(
                "Could not connect to the website. "
                "The server may be offline, blocking requests, or the port may be closed."
            )
        )

    except httpx.TooManyRedirects:
        raise HTTPException(
            status_code=400,
            detail=(
                "Too many redirects. The website appears to have a redirect loop "
                "or an unusually long redirect chain (more than 20 redirects)."
            )
        )

    except httpx.HTTPError:
        raise HTTPException(
            status_code=503,
            detail="An unexpected network error occurred while scanning the website."
        )