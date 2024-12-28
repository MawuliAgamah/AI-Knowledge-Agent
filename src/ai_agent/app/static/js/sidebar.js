document.addEventListener('DOMContentLoaded', function () {
    const sidebar = document.getElementById('sidebar');
    const mainContent = document.querySelector('.main-content');
    const sidebarToggle = document.getElementById('sidebarToggle');

    if (!sidebar || !mainContent || !sidebarToggle) {
        console.error('One or more elements not found');
        return;
    }

    sidebarToggle.addEventListener('click', function () {
        sidebar.classList.toggle('open');
        mainContent.classList.toggle('sidebar-open');
    });
});