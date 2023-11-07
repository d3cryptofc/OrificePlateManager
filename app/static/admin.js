let username = $('input[name="login"]');
let remember_username = $('#remember-username');

username.val(localStorage.remember_username || '');
remember_username.prop('checked', Boolean(localStorage.remember_username))


$('form').on('submit', event => {
    event.preventDefault();

    if(remember_username.prop('checked')){
        localStorage.remember_username = username.val();
    }
    else {
        localStorage.removeItem('remember_username');
    }

    let form = $('form');
    let error_message = $('#error-message');
    let button = $('button');
    let text_login = $('#text-login');
    let text_entering = $('#text-entering');

    const switch_mode = () => {
        button.prop('disabled', !button.prop('disabled'))
        text_login.toggleClass('d-none');
        text_entering.toggleClass('d-none');
    }

    switch_mode()

    $.post({
        url: '/rest/auth',
        contentType: 'application/json',
        data: JSON.stringify(Object.assign(
            ...form.serializeArray().map(item => {
                return {[item.name]: item.value}
            }))
        ),
        xhrFields: {
            withCredentials: true
         }
    }).then(response => {
        location.href = '/';
    }).catch(response => {
        error_message.text(response.responseJSON.message);
        error_message.toggleClass('d-none', false);
        
    }).always(
        response => switch_mode()
    )
})