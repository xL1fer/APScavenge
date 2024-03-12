/*
*   Dashboard sidebar visibility handler
*/
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

/*
*   Dashboard table page change helper function
*/
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





/*
*   Dashboard table submission form handler
*/
function submitTableForm() {
    let csrf_token = $('[name="csrfmiddlewaretoken"]').val();   // Include CSRF token in AJAX request headers
    let formData = $('#dashboard-table-form').serialize();  // Serialize form data
    formData += '&ajaxTableUpdate=' + encodeURIComponent('True');
    formData += '&requestModel=' + encodeURIComponent(requestModel);

    $.ajax({
        type: 'POST',
        url: dashboardURL,
        data: formData,
        headers: {
            'X-CSRFToken': csrf_token
        },
        success: function (response) {
            $('#dashboard-table-form').html(response);
        }
    });
}

/*
*   Event handler for form submission
*/
$(document).on('submit', '#dashboard-table-form', function (e) {
    e.preventDefault();
    submitTableForm();
});

/*
*   Event handler for <a> elements
*/
$(document).on('click', '#dashboard-table-form .prevent-select a', function (e) {
    e.preventDefault();
    submitTableForm();
});

/*
*   Event handler for <select> element
*/
$(document).on('change', '#dashboard-table-form select', function () {
    submitTableForm();
});

/*
*   Event handler for table clickable row
*/
$(document).on('click', '.clickable-row', function (e) {
    let toggleId = $(this).attr('data-toggle-id');
    if (toggleId.includes('passwordhash'))
        return;
    
    let detailsRow = document.getElementById(toggleId + '_details');
    if (detailsRow) {
        if (detailsRow.style.display === 'none') {
            detailsRow.style.display = '';
            $(this).css('background-color', 'rgba(239, 154, 56, 0.3)');

            let csrf_token = $('[name="csrfmiddlewaretoken"]').val();   // Include CSRF token in AJAX request headers
            let formData = $('#dashboard-table-form').serialize();  // Serialize form data
            formData += '&ajaxTableUpdate=' + encodeURIComponent('True');
            formData += '&ajaxSubTableUpdate=' + encodeURIComponent('True');

            let relationField = $(this).attr('relation-data-model');
            let previousModel = toggleId.split('_')[0];
            formData += '&previousModel=' + encodeURIComponent(previousModel);
            formData += '&requestModel=' + encodeURIComponent(relationField);
            formData += '&requestValue=' + encodeURIComponent($(this).find('td').eq(0).text());

            $.ajax({
                type: 'POST',
                url: dashboardURL,
                data: formData,
                headers: {
                    'X-CSRFToken': csrf_token
                },
                success: function (response) {
                    $('#' + toggleId + '_details' + ' span').html(response);
                }
            });
        } else {
            detailsRow.style.display = 'none';
            $(this).css('background-color', '');
            $('#' + toggleId + '_details' + ' span').html('');
        }
    }
});


/*
*   Dashboard stats doughnut charts render
*/
// Setup
let data = {
    labels: [
        'Secure',
        'Vulnerable'
    ],
    datasets: [{
        label: null,
        data: null,
        backgroundColor: [
            'rgb(80, 202, 80)',
            'rgb(226, 96, 96)'
        ],
        hoverOffset: 4
    }]
};
// Config
let config = {
    type: 'doughnut',
    data: null,
    options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '70%', // Adjust the cutout percentage to control the size of the doughnut
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: null
            }
        }
    },
};

const chartElements = document.querySelectorAll('.doughnut');
chartElements.forEach((element, index) => {
    let currentArea = element.getAttribute('id');

    data.datasets[0].label = `Users`;
    data.datasets[0].data = areasStatsData[currentArea];

    config.data = data;
    config.options.plugins.title.text = `"${currentArea}" Area Vulnerability Ratio`;

    new Chart(element.getContext('2d'), config);
});