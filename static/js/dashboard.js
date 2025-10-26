document.addEventListener('DOMContentLoaded', function () {
    // Helper: try to parse JSON or split CSV-like strings, return arrays/objects when possible
    function parseMaybeJSON(value) {
        if (value === undefined || value === null) return undefined;
        if (typeof value === 'object') return value;
        if (typeof value === 'string') {
            // Trim surrounding whitespace
            const s = value.trim();
            // Try JSON
            try {
                return JSON.parse(s);
            } catch (e) {
                // If it's a simple CSV-like string, split into items
                if (s.indexOf(',') !== -1) {
                    return s.split(',').map(function (it) { return it.trim(); });
                }
                // Single string value -> return as single-item array
                return [s];
            }
        }
        return value;
    }

    // Try multiple window variable name candidates and return first valid parsed value or empty array
    function getWindowData(candidates) {
        for (var i = 0; i < candidates.length; i++) {
            var name = candidates[i];
            var raw = window[name];
            var parsed = parseMaybeJSON(raw);
            if (parsed !== undefined && parsed !== null) return parsed;
        }
        return [];
    }

    var weeklyLabels = getWindowData(['weekly_labels', 'WEEKLY_LABELS']);
    var weeklyData = getWindowData(['weekly_data', 'WEEKLY_DATA']);
    var monthlyLabels = getWindowData(['monthly_labels', 'MONTHLY_LABELS']);
    var monthlyData = getWindowData(['monthly_data', 'MONTHLY_DATA']);

    // Create Weekly Chart if canvas exists
    var weeklyCanvas = document.getElementById('weeklyChart');
    if (weeklyCanvas && weeklyCanvas.getContext) {
        new Chart(weeklyCanvas.getContext('2d'), {
            type: 'line',
            data: {
                labels: weeklyLabels,
                datasets: [{
                    label: 'Weekly Spending',
                    data: weeklyData,
                    backgroundColor: 'rgba(16,185,129,.1)',
                    borderColor: '#10b981',
                    borderWidth: 3,
                    pointBackgroundColor: '#ec4899',
                    tension: 0.5
                }]
            },
            options: { responsive: true }
        });
    }

    // Create Monthly Doughnut Chart if canvas exists
    var monthlyCanvas = document.getElementById('monthlyChart');
    if (monthlyCanvas && monthlyCanvas.getContext) {
        new Chart(monthlyCanvas.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: monthlyLabels,
                datasets: [{
                    data: monthlyData,
                    backgroundColor: ['#10b981', '#818cf8', '#ec4899', '#f59e42', '#4ade80']
                }]
            },
            options: { responsive: true, cutout: "70%" }
        });
    }
});