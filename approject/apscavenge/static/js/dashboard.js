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
*   Dashboard stats charts render
*/
// Doughtnut chart setup
let doughnutChartData = {
    labels: [
        'Secure',
        'Vulnerable'
    ],
    datasets: [{
        label: `Users`,
        data: null,
        backgroundColor: [
            'rgb(80, 202, 80)',
            'rgb(226, 96, 96)'
        ],
        hoverOffset: 4
    }]
};
// Doughtnut chart config
let doughnutChartConfig = {
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

function renderDoughnutChart() {
    const doughnutChartElements = document.querySelectorAll('.doughnut-chart');
    doughnutChartElements.forEach((element, index) => {
        let currentArea = element.getAttribute('area');

        let newData = JSON.parse(JSON.stringify(doughnutChartData));
        let newConfig = JSON.parse(JSON.stringify(doughnutChartConfig));

        newData.datasets[0].data = areasStatsData[currentArea].ratio;

        let vulnerableRatio = areasStatsData[currentArea].ratio[1] / areasStatsData[currentArea].ratio.reduce((sum, curValue) => sum + curValue, 0) * 100;

        newConfig.data = newData;
        newConfig.options.plugins.title.text = `Vulnerability Ratio: ${vulnerableRatio.toFixed(2)}%`;

        new Chart(element.getContext('2d'), newConfig);
    });
}

// Line chart setup
let lineChartData = {
    labels: ['January', 'February', 'March', 'April', 'May', 'June', 'July'],
    datasets: [{
        label: `Total Captures`,
        data: null,
        fill: false,
        borderColor: '#ef9a38',
        tension: 0.1
    },
    {
        label: `Secure Captures`,
        data: null,
        fill: false,
        borderColor: 'rgb(80, 202, 80)',
        tension: 0.1
    },
    {
        label: `Vulnerable Captures`,
        data: null,
        fill: false,
        borderColor: 'rgb(226, 96, 96)',
        tension: 0.1
    },]
};
// Line chart config
let lineChartConfig = {
    type: 'line',
    data: lineChartData,
    options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'top',
            },
            title: {
                display: true,
                text: null
            }
        }
    }
};

//new Chart(document.getElementById('test-line-chart').getContext('2d'), lineChartConfig);

function renderLineChart() {
    const lineChartElements = document.querySelectorAll('.line-chart');
    lineChartElements.forEach((element) => {
        let currentArea = element.getAttribute('area');

        let newData = JSON.parse(JSON.stringify(lineChartData));
        let newConfig = JSON.parse(JSON.stringify(lineChartConfig));

        newData.labels = areasStatsData[currentArea].weekly[0];
        newData.datasets[0].data = areasStatsData[currentArea].weekly[1];
        newData.datasets[1].data = areasStatsData[currentArea].weekly[2];
        newData.datasets[2].data = areasStatsData[currentArea].weekly[3];

        newConfig.options.plugins.title.text = `Capture Types Distribution`;

        newConfig.data = newData;

        new Chart(element.getContext('2d'), newConfig);
    });
}

renderDoughnutChart();
renderLineChart();

/*
*   Dashboard stats submission form handler
*/
function submitStatsForm() {
    let csrf_token = $('[name="csrfmiddlewaretoken"]').val();   // Include CSRF token in AJAX request headers
    let formData = $('#dashboard-stats-form').serialize();  // Serialize form data
    formData += '&ajaxStatsUpdate=' + encodeURIComponent('True');

    $.ajax({
        type: 'POST',
        url: dashboardStatsURL,
        data: formData,
        headers: {
            'X-CSRFToken': csrf_token
        },
        success: function (response) {
            $('#stats-area-container').html(response);
            renderDoughnutChart();
            renderLineChart();
        }
    });
}

/*
*   Event handler for <select> element
*/
$(document).on('change', '#dashboard-stats-form select', function () {
    submitStatsForm();
});