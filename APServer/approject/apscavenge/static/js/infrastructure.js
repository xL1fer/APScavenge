
/*
*   Infrastructure grid form submission
*/
function submitGridForm(agentAction) {
    let csrf_token = $('[name="csrfmiddlewaretoken"]').val();   // Include CSRF token in AJAX request headers
    let formData = $('#infrastructure-grid-form').serialize();  // Serialize form data
    formData += '&ajaxGridUpdate=' + encodeURIComponent('True');

    formData += '&agentAction=' + encodeURIComponent(agentAction);

    $.ajax({
        type: 'POST',
        url: infrastructureURL,
        data: formData,
        headers: {
            'X-CSRFToken': csrf_token
        },
        success: function (response) {
            $('#infrastructure-grid-form').html(response);
        }
    });
}

/*
*   Event handler for grid form submission
*/
$(document).on('click', '#infrastructure-grid-form button', function (e) {
    $(this).prop('disabled', true);
    $(this).addClass('action-disabled');
    e.preventDefault();
    submitGridForm($(this).attr('id'));
});





/*
*   Adjust agent alias name form width
*/
function adjustWidth(input) {
    input.style.width = (input.value.length * 1.3) + 'ch';
}

/*
*   Backend form submission
*/
function submitToBackend(key, value) {
    let csrf_token = $('[name="csrfmiddlewaretoken"]').val();   // Include CSRF token in AJAX request headers
    let formData = `&${key}=` + encodeURIComponent(value);

    $.ajax({
        type: 'POST',
        url: infrastructureAgentURL,
        data: formData,
        headers: {
            'X-CSRFToken': csrf_token
        },
        error: function(jqXHR, textStatus, errorThrown) {
            if (jqXHR.status == 400)
                window.location.href = infrastructureURL;
        }
    });
}

/*
*   Event handler for agent details form submission
*/
$(document).on('click', '.details-grid .row:first-child .col:first-child button', function (e) {
    e.preventDefault();
    
    let buttonId = $(this).attr('id');

    if (buttonId !== undefined)
        submitToBackend('ajaxAgentOption', $(this).attr('id'))
});

/*
*   Event handler for agent alias name form submission
*/
$(document).on('submit', '#alias-name-form', function (e) {
    e.preventDefault();
    submitToBackend('ajaxAliasNameUpdate', document.getElementById('input-alias-name').value);
    $('#input-alias-name').blur();
});