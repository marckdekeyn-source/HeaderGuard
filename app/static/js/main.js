const form = document.getElementById("scan-form");
const urlInput = document.getElementById("url-input");
const loadingIndicator = document.getElementById("loading-indicator");
const resultContainer = document.getElementById("result-container");

form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const url = urlInput.value.trim();
    resultContainer.innerHTML = "";

    loadingIndicator.classList.remove("hidden");

    try {
        const formData = new FormData();
        formData.append("url", url);

        const response = await fetch("/scan", {
            method: "POST",
            body: formData,
        });

        const data = await response.json();

        if (!response.ok) {
            showError(data.detail || "Something went wrong.");
            return;
        }

        renderResult(data);

    } catch (error) {
        showError("Network error. Please check your connection and try again.");
        console.error("Error during scan:", error);

    } finally {
        loadingIndicator.classList.add("hidden");
    }
});


function showError(message) {
    resultContainer.innerHTML = `
        <div class="bg-red-950 border border-red-800 text-red-300 rounded-lg px-4 py-3 text-sm">
            [!] ${message}
        </div>
    `;
}


// ============================================================
// Peta warna berdasarkan grade_color dari backend
// Semua class Tailwind harus ditulis secara literal —
// tidak boleh pakai string interpolation untuk class Tailwind
// karena CDN tidak bisa mendeteksi class dinamis.
// ============================================================
const COLOR_MAP = {
    emerald: {
        bg:          "bg-emerald-500",
        bgLight:     "bg-emerald-950",
        text:        "text-emerald-400",
        border:      "border-emerald-500",
        borderLight: "border-emerald-800",
        bar:         "bg-emerald-500",
    },
    green: {
        bg:          "bg-green-500",
        bgLight:     "bg-green-950",
        text:        "text-green-400",
        border:      "border-green-500",
        borderLight: "border-green-800",
        bar:         "bg-green-500",
    },
    blue: {
        bg:          "bg-blue-500",
        bgLight:     "bg-blue-950",
        text:        "text-blue-400",
        border:      "border-blue-500",
        borderLight: "border-blue-800",
        bar:         "bg-blue-500",
    },
    yellow: {
        bg:          "bg-yellow-500",
        bgLight:     "bg-yellow-950",
        text:        "text-yellow-400",
        border:      "border-yellow-500",
        borderLight: "border-yellow-800",
        bar:         "bg-yellow-500",
    },
    orange: {
        bg:          "bg-orange-500",
        bgLight:     "bg-orange-950",
        text:        "text-orange-400",
        border:      "border-orange-500",
        borderLight: "border-orange-800",
        bar:         "bg-orange-500",
    },
    red: {
        bg:          "bg-red-500",
        bgLight:     "bg-red-950",
        text:        "text-red-400",
        border:      "border-red-500",
        borderLight: "border-red-800",
        bar:         "bg-red-500",
    },
};

const GRADE_LABELS = {
    "A+": "Perfect — all security headers are implemented.",
    "A":  "Excellent security posture.",
    "B":  "Good, but some headers need attention.",
    "C":  "Fair — several important headers are missing.",
    "D":  "Poor — critical security headers are missing.",
    "F":  "Critical — most security headers are absent.",
};


function renderResult(data) {
    resultContainer.innerHTML = `
        ${renderScoreCard(data)}
        ${renderHeadersTable(data.analysis)}
        ${renderRecommendations(data.recommendations)}
    `;
}


function renderScoreCard(data) {
    const colors   = COLOR_MAP[data.grade_color] || COLOR_MAP.red;
    const label    = GRADE_LABELS[data.grade] || "";

    // A+ punya dua karakter, pakai font lebih kecil agar muat di kotak
    const gradeTextSize = data.grade === "A+"
        ? "text-2xl font-black text-white"
        : "text-4xl font-black text-white";

    // Tampilkan final_url jika berbeda dari received_url
    const redirectInfo = data.final_url && data.final_url !== data.received_url
        ? `<p class="text-slate-500 text-xs mt-1">
               &#8594; Redirected to:
               <span class="text-slate-400">${escapeHtml(data.final_url)}</span>
           </p>`
        : "";

    return `
        <div class="bg-slate-900 border-2 ${colors.border} rounded-xl overflow-hidden mb-6">

            <div class="${colors.bgLight} border-b ${colors.borderLight} px-6 py-3 flex items-center justify-between">
                <span class="${colors.text} text-sm font-medium">
                    &#9679; HeaderGuard Security Report
                </span>
                <span class="${colors.text} text-xs font-semibold">
                    Grade: ${escapeHtml(data.grade)}
                </span>
            </div>

            <div class="p-6">
                <div class="flex items-center justify-between gap-6">

                    <div class="flex-1 min-w-0">
                        <p class="text-slate-400 text-xs mb-1">Scan result for</p>
                        <p class="text-slate-100 font-semibold break-all">
                            ${escapeHtml(data.received_url)}
                        </p>
                        ${redirectInfo}
                        <p class="${colors.text} text-xs mt-2">${label}</p>
                    </div>

                    <div class="flex items-center gap-4 shrink-0">
                        <div class="text-right">
                            <p class="text-slate-400 text-xs mb-1">Score</p>
                            <p class="text-4xl font-black ${colors.text}">
                                ${data.score}<span class="text-slate-600 text-xl">/100</span>
                            </p>
                        </div>
                        <div class="w-20 h-20 rounded-2xl ${colors.bg} flex items-center justify-center shadow-lg">
                            <span class="${gradeTextSize}">${escapeHtml(data.grade)}</span>
                        </div>
                    </div>

                </div>

                <div class="mt-4 pt-4 border-t border-slate-800 flex items-center gap-3">
                    <div class="flex-1 bg-slate-800 rounded-full h-2 overflow-hidden">
                        <div class="${colors.bar} h-2 rounded-full"
                             style="width: ${data.score}%">
                        </div>
                    </div>
                    <span class="text-slate-500 text-xs shrink-0">${data.score}%</span>
                </div>
            </div>

        </div>
    `;
}


function renderHeadersTable(analysis) {
    const rows = Object.entries(analysis).map(([key, header]) => {
        const statusBadge = header.present
            ? `<span class="inline-flex items-center gap-1 bg-emerald-950 text-emerald-400 border border-emerald-800 text-xs px-2 py-0.5 rounded-full">&#10003; Present</span>`
            : `<span class="inline-flex items-center gap-1 bg-red-950 text-red-400 border border-red-800 text-xs px-2 py-0.5 rounded-full">&#10007; Missing</span>`;

        const severityColors = {
            high:   "bg-red-950 text-red-400 border-red-800",
            medium: "bg-yellow-950 text-yellow-400 border-yellow-800",
            low:    "bg-slate-800 text-slate-400 border-slate-700",
        };
        const severityClass = severityColors[header.severity] || severityColors.low;
        const severityBadge = `<span class="inline-flex border text-xs px-2 py-0.5 rounded-full ${severityClass}">${header.severity}</span>`;

        const valueDisplay = header.value
            ? `<p class="text-slate-500 text-xs mt-1 truncate max-w-xs"
                  title="${escapeHtml(header.value)}">
                   ${escapeHtml(header.value)}
               </p>`
            : "";

        return `
            <tr class="border-t border-slate-800 hover:bg-slate-800 transition-colors">
                <td class="py-3 pr-4 pl-2">
                    <p class="text-slate-200 text-sm font-mono">${escapeHtml(header.name)}</p>
                    ${valueDisplay}
                </td>
                <td class="py-3 pr-4">${severityBadge}</td>
                <td class="py-3 pr-2">${statusBadge}</td>
            </tr>
        `;
    }).join("");

    return `
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-6 mb-6">
            <h2 class="text-slate-100 font-semibold mb-4">Security Headers</h2>
            <table class="w-full">
                <thead>
                    <tr class="text-left text-slate-500 text-xs uppercase tracking-wider">
                        <th class="pb-3 pr-4 pl-2">Header</th>
                        <th class="pb-3 pr-4">Severity</th>
                        <th class="pb-3">Status</th>
                    </tr>
                </thead>
                <tbody>
                    ${rows}
                </tbody>
            </table>
        </div>
    `;
}


function renderRecommendations(recommendations) {
    if (recommendations.length === 0) {
        return `
            <div class="bg-emerald-950 border border-emerald-800 rounded-xl p-6">
                <p class="text-emerald-400 font-semibold">
                    All security headers are present!
                </p>
                <p class="text-emerald-600 text-sm mt-1">
                    This site has implemented all recommended security headers.
                </p>
            </div>
        `;
    }

    const severityColors = {
        high:   "border-red-800 bg-red-950",
        medium: "border-yellow-800 bg-yellow-950",
        low:    "border-slate-700 bg-slate-800",
    };

    const severityTextColors = {
        high:   "text-red-400",
        medium: "text-yellow-400",
        low:    "text-slate-400",
    };

    const items = recommendations.map(rec => {
        const cardClass        = severityColors[rec.severity]     || severityColors.low;
        const severityTextClass = severityTextColors[rec.severity] || severityTextColors.low;

        return `
            <div class="border ${cardClass} rounded-lg p-4">
                <div class="flex items-start justify-between gap-4">
                    <div class="flex-1">
                        <p class="text-slate-100 font-medium text-sm">
                            ${escapeHtml(rec.title)}
                        </p>
                        <p class="text-slate-400 text-xs mt-1">
                            ${escapeHtml(rec.description)}
                        </p>
                    </div>
                    <span class="text-xs ${severityTextClass} shrink-0 capitalize font-medium">
                        ${rec.severity}
                    </span>
                </div>
                <div class="mt-3 bg-slate-950 rounded-md px-3 py-2">
                    <p class="text-emerald-400 font-mono text-xs">
                        ${escapeHtml(rec.fix)}
                    </p>
                </div>
                <p class="text-slate-500 text-xs mt-2">
                    ${escapeHtml(rec.fix_description)}
                </p>
                <a href="${escapeHtml(rec.references)}"
                   target="_blank"
                   rel="noopener noreferrer"
                   class="inline-block text-xs text-slate-500 hover:text-emerald-400 mt-2 transition-colors">
                    MDN Reference &rarr;
                </a>
            </div>
        `;
    }).join("");

    return `
        <div class="bg-slate-900 border border-slate-800 rounded-xl p-6">
            <h2 class="text-slate-100 font-semibold mb-4">
                Recommendations
                <span class="ml-2 text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded-full">
                    ${recommendations.length}
                </span>
            </h2>
            <div class="flex flex-col gap-3">
                ${items}
            </div>
        </div>
    `;
}


function escapeHtml(str) {
    if (str === null || str === undefined) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}