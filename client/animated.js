document.addEventListener("DOMContentLoaded", function() {
    const areas = document.querySelectorAll('.area');
    const tooltip = document.querySelector('.tooltip');

    areas.forEach(area => {
        area.addEventListener('mouseover', (e) => {
            const label = area.getAttribute('data-label');
            tooltip.textContent = label;
            tooltip.style.opacity = '1';
            tooltip.style.left = `${e.pageX + 10}px`;
            tooltip.style.top = `${e.pageY + 10}px`;
        });

        area.addEventListener('mouseout', () => {
            tooltip.style.opacity = '0';
        });

        area.addEventListener('mousemove', (e) => {
            tooltip.style.left = `${e.pageX + 10}px`;
            tooltip.style.top = `${e.pageY + 10}px`;
        });
    });
});
