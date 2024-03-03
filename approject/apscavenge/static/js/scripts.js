document.addEventListener("DOMContentLoaded", function () {
    const sidebar = document.querySelector(".sidebar");
    const buttonSidebarToggle = document.getElementById("button-sidebar-toggle");
    const aSidebarToggle = document.getElementById("a-sidebar-toggle");
    const sidebarToggleContainer = document.getElementById("sidebar-toggle-container");
    const ulSidebar = document.getElementById("ul-sidebar");

    // Toggle sidebar visibility based on window width
    function toggleSidebarVisibility() {
        if (sidebar == null) return;
        
        if (window.innerWidth <= 1050) {
            sidebar.classList.add("sidebar-hidden");
            aSidebarToggle.classList.remove("sidebar-hidden");
            sidebarToggleContainer.classList.remove("sidebar-hidden");
            ulSidebar.classList.add("no-hover");
        }
        else {
            sidebar.classList.remove("sidebar-hidden");
            aSidebarToggle.classList.add("sidebar-hidden");
            sidebarToggleContainer.classList.add("sidebar-hidden");
            ulSidebar.classList.remove("no-hover");
        }
    }

    // Set initial visibility
    toggleSidebarVisibility();

    // Toggle event listeners
    if (buttonSidebarToggle != null && aSidebarToggle != null)
    {
        buttonSidebarToggle.addEventListener("click", function () {
            sidebar.classList.toggle("sidebar-hidden");
            ulSidebar.classList.toggle("no-hover");
        });

        aSidebarToggle.addEventListener("click", function () {
            sidebar.classList.toggle("sidebar-hidden");
            ulSidebar.classList.toggle("no-hover");
        });
    }

    // Resize event listener to adjust sidebar visibility on window resize
    window.addEventListener("resize", function () {
        toggleSidebarVisibility();
    });
});

window.addEventListener('scroll', function() {
    let items = document.querySelectorAll('.navbar.second');
    let scrollPosition = window.scrollY;

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

function changeTablePage(offset) {
    let currentPageField = document.getElementById('form-current-page');
    let maxPageField = document.getElementById('form-max-page');
    let currentPage = parseInt(currentPageField.value) || 1;
    let maxPage = parseInt(maxPageField.value) || 1;
    currentPage = Math.min(currentPage, maxPage);  // Ensure page is not more than max page
    currentPage += offset;
    currentPage = Math.max(1, currentPage);  // Ensure page is not less than 1
    currentPageField.value = currentPage;

    //document.getElementById('dashboard-table-form').submit();
}