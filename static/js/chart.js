function animateValue(id, start, end, duration, prefix = '') {
    const obj = document.getElementById(id);
    let startTime = null;
    const step = (timestamp) => {
        if (!startTime) startTime = timestamp;
        const progress = Math.min((timestamp - startTime) / duration, 1);
        obj.textContent = prefix + Math.floor(progress * (end - start) + start);
        if (progress < 1) requestAnimationFrame(step);
    };
    requestAnimationFrame(step);
}

document.addEventListener('DOMContentLoaded', () => {
    if (typeof total !== 'undefined') {
        animateValue("totalSpent", 0, total, 1500, "₹");
        animateValue("totalCount", 0, count, 1500);
        animateValue("maxExpense", 0, maxExp, 1500, "₹");

        const ctx1 = document.getElementById('categoryChart').getContext('2d');
        new Chart(ctx1, {
            type: 'pie',
            data: {
                labels: Object.keys(categoryData),
                datasets: [{
                    data: Object.values(categoryData),
                    backgroundColor: ['#10B981', '#34D399', '#6EE7B7', '#A7F3D0', '#D1FAE5']
                }]
            },
            options: { responsive: true }
        });

        const ctx2 = document.getElementById('dailyChart').getContext('2d');
        new Chart(ctx2, {
            type: 'bar',
            data: {
                labels: Object.keys(dailyData),
                datasets: [{
                    label: 'Daily Spend (₹)',
                    data: Object.values(dailyData),
                    backgroundColor: '#10B981'
                }]
            },
            options: { responsive: true, scales: { y: { beginAtZero: true } } }
        });
    }
});
