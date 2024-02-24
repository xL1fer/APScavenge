document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.querySelector(".sidebar");
    const buttonSidebarToggle = document.getElementById("button-sidebar-toggle");
    const aSidebarToggle = document.getElementById("a-sidebar-toggle");
    const sidebarToggleContainer = document.getElementById("sidebar-toggle-container");

    // Toggle sidebar visibility based on window width
    function toggleSidebarVisibility() {
        if (sidebar == null) return;
        
        if (window.innerWidth <= 1050) {
            sidebar.classList.add("sidebar-hidden");
            aSidebarToggle.classList.remove("sidebar-hidden");
            sidebarToggleContainer.classList.remove("sidebar-hidden");
        }
        else {
            sidebar.classList.remove("sidebar-hidden");
            aSidebarToggle.classList.add("sidebar-hidden");
            sidebarToggleContainer.classList.add("sidebar-hidden");
        }
    }

    // Set initial visibility
    toggleSidebarVisibility();

    // Toggle event listeners
    if (buttonSidebarToggle != null && aSidebarToggle != null)
    {
        buttonSidebarToggle.addEventListener("click", function () {
            sidebar.classList.toggle("sidebar-hidden");
        });

        aSidebarToggle.addEventListener("click", function () {
            sidebar.classList.toggle("sidebar-hidden");
        });
    }

    // Resize event listener to adjust sidebar visibility on window resize
    window.addEventListener("resize", function () {
        toggleSidebarVisibility();
    });
});

window.addEventListener('scroll', function() {
    var items = document.querySelectorAll('.navbar.second');
    var scrollPosition = window.scrollY;

    items.forEach(function(item) {
        if (scrollPosition > 90) {
            item.classList.remove("py-4");
            item.classList.add("py-2");
        }
        else if (scrollPosition < 50) {
            item.classList.add("py-4");
            item.classList.remove("py-2");
        }
    });
});