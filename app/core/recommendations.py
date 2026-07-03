"""
Modul ini menghasilkan rekomendasi perbaikan yang actionable
untuk setiap security header yang hilang dari hasil scan.

Pure business logic — tidak ada dependency ke FastAPI atau layer lain.
"""

RECOMMENDATIONS = {
    "strict-transport-security": {
        "title": "Enable HTTP Strict Transport Security (HSTS)",
        "description": (
            "Your site does not enforce HTTPS connections. Without HSTS, users may "
            "connect via insecure HTTP before being redirected, leaving them vulnerable "
            "to man-in-the-middle attacks."
        ),
        "fix": "Strict-Transport-Security: max-age=31536000; includeSubDomains; preload",
        "fix_description": (
            "Add this header to your server configuration. "
            "'max-age=31536000' enforces HTTPS for 1 year. "
            "'includeSubDomains' extends protection to all subdomains. "
            "'preload' allows your site to be included in browser HSTS preload lists."
        ),
        "references": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Strict-Transport-Security",
    },
    "content-security-policy": {
        "title": "Implement a Content Security Policy (CSP)",
        "description": (
            "Without CSP, your site is vulnerable to Cross-Site Scripting (XSS) attacks. "
            "Attackers can inject malicious scripts that steal user data, hijack sessions, "
            "or deface your website."
        ),
        "fix": "Content-Security-Policy: default-src 'self'",
        "fix_description": (
            "Start with a strict baseline policy: 'default-src self' blocks all external "
            "resources by default. Then progressively whitelist trusted sources as needed. "
            "Warning: an overly permissive CSP (e.g. using 'unsafe-inline') significantly "
            "reduces its effectiveness."
        ),
        "references": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy",
    },
    "x-frame-options": {
        "title": "Add X-Frame-Options to Prevent Clickjacking",
        "description": (
            "Your page can be embedded in iframes on other websites. "
            "Attackers can overlay invisible iframes to trick users into clicking "
            "on elements they cannot see — a technique known as clickjacking."
        ),
        "fix": "X-Frame-Options: DENY",
        "fix_description": (
            "Use 'DENY' to block all iframe embedding, or 'SAMEORIGIN' to allow "
            "embedding only from your own domain. 'DENY' is recommended unless "
            "you intentionally embed your pages in iframes."
        ),
        "references": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Frame-Options",
    },
    "x-content-type-options": {
        "title": "Enable X-Content-Type-Options",
        "description": (
            "Without this header, browsers may 'sniff' and misinterpret file types, "
            "potentially executing a file as a script even if it was served as plain text. "
            "This can be exploited to run malicious code."
        ),
        "fix": "X-Content-Type-Options: nosniff",
        "fix_description": (
            "This header only has one valid value: 'nosniff'. "
            "It instructs the browser to strictly follow the declared Content-Type "
            "and never guess the file type."
        ),
        "references": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/X-Content-Type-Options",
    },
    "referrer-policy": {
        "title": "Set a Referrer Policy",
        "description": (
            "Without a Referrer-Policy, full URLs (including sensitive query parameters "
            "like tokens or user IDs) may be leaked to third-party websites when users "
            "click external links."
        ),
        "fix": "Referrer-Policy: strict-origin-when-cross-origin",
        "fix_description": (
            "'strict-origin-when-cross-origin' is the recommended balance: "
            "it sends full referrer info for same-origin requests, "
            "but only the origin (no path/query) for cross-origin requests, "
            "and nothing at all when navigating from HTTPS to HTTP."
        ),
        "references": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Referrer-Policy",
    },
    "permissions-policy": {
        "title": "Add a Permissions Policy",
        "description": (
            "Without Permissions-Policy, embedded third-party scripts (ads, widgets, trackers) "
            "may access sensitive browser features like the camera, microphone, or "
            "geolocation without your users' knowledge."
        ),
        "fix": "Permissions-Policy: camera=(), microphone=(), geolocation=()",
        "fix_description": (
            "The example above disables camera, microphone, and geolocation access entirely. "
            "Customize based on your site's needs — only allow features your application "
            "actually uses. Empty parentheses '()' means 'deny all origins'."
        ),
        "references": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Permissions-Policy",
    },
    "cross-origin-opener-policy": {
        "title": "Enable Cross-Origin-Opener-Policy (COOP)",
        "description": (
            "Without COOP, other websites may be able to obtain a reference to your "
            "browsing context and exploit side-channel attacks (like Spectre) to access "
            "sensitive information from your page's memory."
        ),
        "fix": "Cross-Origin-Opener-Policy: same-origin",
        "fix_description": (
            "'same-origin' is the strictest value — it fully isolates your page from "
            "cross-origin windows. Use 'same-origin-allow-popups' if your site opens "
            "cross-origin popups that need to interact with your page (e.g. OAuth flows)."
        ),
        "references": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cross-Origin-Opener-Policy",
    },
    "cross-origin-resource-policy": {
        "title": "Set a Cross-Origin-Resource-Policy (CORP)",
        "description": (
            "Without CORP, your resources (images, scripts, fonts) can be loaded "
            "by any external website. Combined with side-channel attacks, this can "
            "leak sensitive information about your users or your infrastructure."
        ),
        "fix": "Cross-Origin-Resource-Policy: same-origin",
        "fix_description": (
            "'same-origin' allows only your own pages to load these resources. "
            "Use 'same-site' if resources need to be shared across subdomains, "
            "or 'cross-origin' only if resources are intentionally public (like a CDN)."
        ),
        "references": "https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Cross-Origin-Resource-Policy",
    },
}


def generate_recommendations(analysis: dict) -> list:
    """
    Menghasilkan daftar rekomendasi untuk setiap header
    yang 'present: false' dalam hasil analisis.

    Args:
        analysis: dict hasil dari analyze_headers()

    Returns:
        List of dict, masing-masing berisi detail rekomendasi,
        diurutkan dari severity tertinggi ke terendah.
    """
    severity_order = {"high": 0, "medium": 1, "low": 2}

    recommendations = []
    for header_key, header_data in analysis.items():
        if not header_data["present"]:
            rec = RECOMMENDATIONS.get(header_key)
            if rec:
                recommendations.append({
                    "header": header_key,
                    "severity": header_data["severity"],
                    **rec,
                })

    recommendations.sort(key=lambda x: severity_order.get(x["severity"], 99))

    return recommendations