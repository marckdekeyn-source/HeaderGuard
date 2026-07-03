"""
Modul ini mendefinisikan struktur data (schema) untuk request dan response
endpoint /scan menggunakan Pydantic BaseModel.

Memisahkan definisi data dari logika bisnis dan routing —
siapa pun yang membaca file ini langsung tahu 'bentuk data' yang dipakai app ini.
"""

from pydantic import BaseModel
from typing import Optional


class HeaderDetail(BaseModel):
    """Struktur data untuk satu security header dalam hasil analisis."""
    name: str
    description: str
    severity: str
    present: bool
    value: Optional[str] = None


class RecommendationDetail(BaseModel):
    """Struktur data untuk satu item rekomendasi."""
    header: str
    severity: str
    title: str
    description: str
    fix: str
    fix_description: str
    references: str


class ScanResult(BaseModel):
    """
    Struktur data lengkap untuk response endpoint POST /scan.
    FastAPI otomatis memvalidasi dan mengonversi return value
    ke format ini jika kita gunakan sebagai response_model.
    """
    received_url: str
    final_url: str
    status: str
    score: int
    grade: str
    grade_color: str
    analysis: dict[str, HeaderDetail]
    recommendations: list[RecommendationDetail]