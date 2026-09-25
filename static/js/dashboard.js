document.addEventListener("DOMContentLoaded", () => {
    const dataElement = document.getElementById("dashboard-data");
    if (!dataElement || typeof Chart === "undefined") {
        return;
    }

    const chartData = JSON.parse(dataElement.textContent);
    const createChart = (id, type, records, label) => {
        const canvas = document.getElementById(id);
        if (!canvas) {
            return;
        }

        new Chart(canvas, {
            type,
            data: {
                labels: records.map((record) => record.label),
                datasets: [{
                    label,
                    data: records.map((record) => record.total)
                }]
            },
            options: {
                responsive: true,
                scales: type === "bar" ? { y: { beginAtZero: true } } : undefined
            }
        });
    };

    createChart("categoryChart", "doughnut", chartData.categories, "Reports");
    createChart("riskChart", "bar", chartData.risks, "Reports");
    createChart("locationChart", "bar", chartData.locations, "Incidents");
    createChart("statusChart", "pie", chartData.statuses, "Reports");
});