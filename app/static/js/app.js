// ================================
// HACKER THEME WAF FRONTEND JS
// ================================

// Global chart reference
let chart;
let chartMode = "history";  // "last" or "history"


// ================================
// LOAD HISTORY CHART (Malicious vs Safe)
// ================================
async function loadHistoryChart() {
    try {
        const res = await fetch('/api/stats');
        const data = await res.json();

        const ctx = document.getElementById('attackChart');
        if (!ctx) return;

        if (chart) chart.destroy();

        chart = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Malicious', 'Safe'],
                datasets: [{
                    data: [data.malicious, data.safe],
                    backgroundColor: ['#ff004c','#00ff9d'],
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                plugins: {
                    legend: {
                        labels: { color: '#00ff9d' }
                    }
                }
            }
        });
    } catch (err) {
        console.error("History Chart Error:", err);
    }
}


// ================================
// LOAD LAST RESULT CHART (FULL GREEN/RED)
// ================================
function loadLastResultChart() {
    const resultText = document.getElementById("resultText").innerText || "";
    const isMalicious = resultText.toLowerCase().includes("malicious");

    const ctx = document.getElementById('attackChart');
    if (!ctx) return;

    if (chart) chart.destroy();

    chart = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: ['Result'],
            datasets: [{
                data: [1],
                backgroundColor: [isMalicious ? '#ff004c' : '#00ff9d'],
                borderWidth: 1
            }]
        },
        options: {
            circumference: 360,
            rotation: -90,
            cutout: "70%",
            plugins: { legend: { display: false } }
        }
    });
}


// ================================
// DECIDE WHICH CHART TO LOAD
// ================================
function loadChart() {
    if (chartMode === "last") {
        loadLastResultChart();
    } else {
        loadHistoryChart();
    }
}


// ================================
// LOAD LOGS
// ================================
async function loadLogs() {
    try {
        const res = await fetch('/api/logs');
        const logs = await res.json();

        let logDiv = document.getElementById('logContainer');
        if (!logDiv) return;

        logDiv.innerHTML = "";

        logs.forEach(log => {
            let row = document.createElement('div');
            row.className = "log-row";
            row.style.whiteSpace = "pre-wrap";
            row.style.marginBottom = "10px";
            row.style.padding = "8px";
            row.style.border = "1px solid #00ff9d";

            row.innerText =
                `[${log.ts}]\n` +
                `IP: ${log.ip}\n` +
                `Result: ${log.result} (${log.reason})\n` +
                `Payload: ${log.input}`;

            logDiv.appendChild(row);
        });

    } catch (err) {
        console.error("Load Logs Error:", err);
    }
}


// ================================
// ANALYZE FORM SUBMIT
// ================================
const form = document.getElementById('analyzeForm');

if (form) {
    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        let txt = document.getElementById('inputText').value;
        if (!txt.trim()) return;

        const res = await fetch('/api/analyze', {
            method: 'POST',
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ input: txt })
        });

        const data = await res.json();
        document.getElementById('resultText').innerText =
            `${data.result} (${data.reason})`;

        loadLogs();
        loadChart();
    });
}


// ================================
// TOGGLE BUTTON EVENTS
// ================================
document.getElementById("btnLast")?.addEventListener("click", () => {
    chartMode = "last";
    loadChart();
});

document.getElementById("btnHistory")?.addEventListener("click", () => {
    chartMode = "history";
    loadChart();
});


// ================================
// AUTO REFRESH EVERY 3 SECONDS
// ================================
setInterval(() => {
    loadLogs();
    loadChart();
}, 3000);


// ================================
// INITIAL LOAD
// ================================
loadLogs();
loadChart();

