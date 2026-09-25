document.addEventListener("DOMContentLoaded", () => {
    const analysis = document.querySelector(".risk-analysis");
    const score = Number(analysis?.dataset.riskScore || 0);

    if (analysis) {
        analysis.classList.add(
            score >= 80 ? "risk-urgent" :
            score >= 60 ? "risk-review" :
            score >= 30 ? "risk-monitor" : "risk-normal"
        );
    }
});
