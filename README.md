# 🛡️ HeaderGuard

**HeaderGuard** is an open-source web security tool that analyzes HTTP security headers of any website, calculates a weighted security score, and provides actionable recommendations for improvement.

Built with Python, FastAPI, and Tailwind CSS.

---

## ✨ Features

- **Instant URL scanning** — analyze any public website's security headers in seconds
- **8 security headers analyzed** — HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, COOP, CORP
- **Weighted scoring system** — severity-based scoring (F to A+) that reflects real security risk
- **Actionable recommendations** — specific fix suggestions with MDN references for every missing header
- **Redirect chain awareness** — follows redirects with browser-like User-Agent for accurate results
- **SSRF protection** — blocks scanning of private/internal network addresses
- **Modern dark UI** — clean, responsive interface built with Tailwind CSS

---

## 🖥️ Screenshot

<img width="1267" height="702" alt="image" src="https://github.com/user-attachments/assets/0f988239-941b-4d71-8dea-31aa818fb496" />

<img width="1382" height="766" alt="image" src="https://github.com/user-attachments/assets/8250a177-00d2-4556-a395-602cf61494ee" />

<img width="1297" height="697" alt="F" src="https://github.com/user-attachments/assets/32193260-c92c-4242-bfb9-a66ffbe32168" />

<img width="1121" height="665" alt="security_F" src="https://github.com/user-attachments/assets/c7ba6468-873b-4fb8-b99b-01d8d1434732" />

<img width="1227" height="855" alt="Recom_F" src="https://github.com/user-attachments/assets/7f88e2a3-7c57-4f2f-b629-3b3ca6fef5e3" />

---

## 🏗️ Architecture

HeaderGuard follows a **Layered Architecture** with clean separation of concerns:

```
Presentation Layer   →  app/main.py (FastAPI routes) + app/templates/
        ↓
Application Layer    →  app/services/ (orchestration + validation)
        ↓
Domain Layer         →  app/core/ (scoring, header rules, recommendations)
        ↓
Infrastructure Layer →  app/clients/ (httpx wrapper)
```

### Project Structure

```
web-security-header-checker/
├── app/
│   ├── main.py                     # FastAPI entry point & routing
│   ├── core/
│   │   ├── header_rules.py         # Security header definitions & analysis
│   │   ├── scoring.py              # Weighted scoring & grade calculation
│   │   └── recommendations.py      # Actionable fix recommendations
│   ├── services/
│   │   ├── scan_service.py         # Scan pipeline orchestration
│   │   └── validator.py            # URL validation & SSRF protection
│   ├── clients/
│   │   └── http_client.py          # httpx wrapper with error handling
│   ├── schemas/
│   │   └── scan_result.py          # Pydantic response models
│   ├── templates/
│   │   └── index.html              # Main page template
│   └── static/
│       └── js/
│           └── main.js             # Frontend scan logic & UI rendering
├── tests/
│   ├── test_scoring.py
│   ├── test_header_rules.py
│   ├── test_recommendations.py
│   └── test_validator.py
├── requirements.txt
├── .gitignore
└── README.md
```

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- pip

### Installation

**1. Clone the repository**

```bash
git clone https://github.com/marckdekeyn-source/HeaderGuard/
cd web-security-header-checker
```

**2. Create and activate a virtual environment**

```bash
# Windows
python -m venv venv
venv\Scripts\activate.bat

# Linux / macOS
python3 -m venv venv
source venv/bin/activate
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Run the development server**

```bash
uvicorn app.main:app --reload
```

**5. Open your browser**

```
http://127.0.0.1:8000
```

---

## 🔍 Usage

1. Enter any public website URL (e.g. `https://github.com`)
2. Click **Scan**
3. View the security score, grade, header status table, and recommendations

### Grading System

| Score | Grade | Meaning |
|-------|-------|---------|
| 95–100 | A+ | Perfect — all headers implemented |
| 90–94 | A | Excellent security posture |
| 70–89 | B | Good, minor improvements needed |
| 50–69 | C | Fair — several headers missing |
| 30–49 | D | Poor — critical headers missing |
| 0–29 | F | Critical — most headers absent |

### Scoring Weights

Headers are weighted by severity to reflect real-world security risk:

| Severity | Headers | Points Each |
|----------|---------|-------------|
| High | HSTS, CSP | 20 pts |
| Medium | X-Frame-Options, X-Content-Type-Options, COOP, CORP | 12.5 pts |
| Low | Referrer-Policy, Permissions-Policy | 5 pts |
| **Total** | | **100 pts** |

---

## 🔒 Security Design

HeaderGuard is built with security in mind:

- **SSRF Protection** — blocks all requests to private/internal IP ranges (`10.x`, `172.16.x`, `192.168.x`, `127.x`, `169.254.x`) to prevent Server-Side Request Forgery attacks
- **Input validation** — strict URL validation using whitelist approach (only `http://` and `https://` schemes allowed)
- **XSS prevention** — all user-supplied data rendered via `escapeHtml()` before DOM insertion
- **Secure error handling** — errors return user-friendly messages without leaking internal stack traces

---

## 🧪 Running Tests

```bash
pytest tests/ -v
```

Expected output: **61 passed** across 4 test modules covering scoring, header analysis, recommendations, and input validation.

```
========================= 61 passed in 5.95s =========================
```

---

## 📡 API Reference

### `GET /`
Returns the main HeaderGuard web interface.

### `POST /scan`

Scans a website's security headers.

**Request** (form data):

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | Yes | Full URL to scan (must include `http://` or `https://`) |

**Response** (JSON):

```json
{
  "received_url": "https://github.com",
  "final_url": "https://github.com/",
  "status": "ok",
  "score": 70,
  "grade": "B",
  "grade_color": "blue",
  "analysis": {
    "strict-transport-security": {
      "name": "Strict-Transport-Security (HSTS)",
      "description": "Forces browsers to use HTTPS...",
      "severity": "high",
      "present": true,
      "value": "max-age=31536000; includeSubdomains; preload"
    }
  },
  "recommendations": [
    {
      "header": "cross-origin-opener-policy",
      "severity": "medium",
      "title": "Enable Cross-Origin-Opener-Policy (COOP)",
      "description": "...",
      "fix": "Cross-Origin-Opener-Policy: same-origin",
      "fix_description": "...",
      "references": "https://developer.mozilla.org/..."
    }
  ]
}
```

**Error Responses:**

| Status | Cause |
|--------|-------|
| `400` | Invalid URL format, SSL error, redirect loop, or SSRF attempt |
| `503` | Timeout, DNS resolution failure, or connection refused |

---

## 🛠️ Tech Stack

| Component | Technology |
|-----------|------------|
| Backend | Python 3.12+, FastAPI 0.138+ |
| HTTP Client | httpx 0.28+ |
| Template Engine | Jinja2 |
| Frontend | HTML, Tailwind CSS (CDN), Vanilla JavaScript |
| Server | Uvicorn |
| Testing | pytest |

---

## 🗺️ Roadmap

### v1.0 (Current)
- [x] 8 security header analysis
- [x] Weighted scoring (F to A+)
- [x] Actionable recommendations with MDN references
- [x] SSRF protection
- [x] 61 unit tests

### v2.0 (Planned)
- [ ] Scan history
- [ ] Export results to JSON/PDF
- [ ] Detect CSP report-only vs enforce mode
- [ ] Public REST API with rate limiting
- [ ] Side-by-side domain comparison

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License — see the [LICENSE](LICENSE) file for details.

---

## 👤 Author

**Your Name**
- GitHub: [marckdekeyn-source](https://github.com/marckdekeyn-source)

---

> Built as a learning project for Python, FastAPI, and web security concepts.
