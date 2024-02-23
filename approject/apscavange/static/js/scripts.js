document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.querySelector(".sidebar");
    const sidebarToggle = document.getElementById("sidebar-toggle");
    const sidebarToggleContainer = document.getElementById("sidebar-toggle-container");

    // Toggle sidebar visibility based on window width
    function toggleSidebarVisibility() {
        if (window.innerWidth <= 1050) {
            sidebar.classList.add("sidebar-hidden");
            sidebarToggleContainer.classList.remove("sidebar-hidden");
        }
        else {
            sidebar.classList.remove("sidebar-hidden");
            sidebarToggleContainer.classList.add("sidebar-hidden");
        }
    }

    // Set initial visibility
    toggleSidebarVisibility();

    // Button event listener to the
    sidebarToggle.addEventListener("click", function () {
        sidebar.classList.toggle("sidebar-hidden");
    });

    // Eesize event listener to adjust sidebar visibility on window resize
    window.addEventListener("resize", function () {
        toggleSidebarVisibility();
    });
});