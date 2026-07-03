"""
Entry point aplikasi HeaderGuard.
File ini hanya berisi setup FastAPI dan definisi route (endpoint).
Semua logika bisnis didelegasikan ke layer service, core, dan clients.
"""

from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from urllib.parse import urlparse

from app.services.validator import is_valid_url, is_private_host
from app.services.scan_service import run_scan

app = FastAPI(
    title="HeaderGuard",
    description="Web Security Header Checker - Analyze and score your website's security headers"
)

app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def read_root(request: Request):
    """Menampilkan halaman utama HeaderGuard."""
    return templates.TemplateResponse(request=request, name="index.html")


@app.post("/scan")
async def scan_url(url: str = Form(...)):
    """
    Endpoint utama: menerima URL, memvalidasi, lalu menjalankan
    pipeline scanning lengkap dan mengembalikan hasil sebagai JSON.
    """
    url = url.strip()

    # Validasi 1: format URL
    if not is_valid_url(url):
        raise HTTPException(
            status_code=400,
            detail=(
                "Invalid URL format. "
                "URL must start with http:// or https:// and include a valid domain."
            )
        )

    # Validasi 2: proteksi SSRF
    hostname = urlparse(url).netloc.split(":")[0]
    if is_private_host(hostname):
        raise HTTPException(
            status_code=400,
            detail=(
                "Scanning private or internal network addresses "
                "is not allowed for security reasons."
            )
        )

    result = await run_scan(url)
    return result