let
    username_input = "input[name=username]"
    email_input = "input[name=email]"
    password_input = 'input[name=password]'
    password_again_input = 'input[name=password2]'
    create_account_form = '#join-form'
    login_account_form = '#login-form'
    any_password_input = 'input[data-type=password]'

validators = {
    username: function(value){
        errors = []
        if (value.length < 3){
            errors.push('username too short, should be at least 3 characters')
        } else if (value.length > 25) {
            errors.push('username too long, should be 25 characters or less')
        } if (value.match(/[^a-z0-9_]/i)){
            errors.push('username contains unwanted characters, use only a-z 0-9 and underscores(_)')
        } else if (value.match(/^_+$/i)){
            errors.push('username should not contain only underscores')
        } else if (value.match(/^[0-9]+$/i)){
            errors.push('username should not contain only numbers')
        } else if (value.match(/^[0-9_]+$/i)) {
            errors.push('username should not contain only numbers and underscores')
        }
        return errors
    }, password: function(value){
        errors = []
        if (value.length < 8){
            errors.push(['password should be at least eight(8) characters'])
        } return errors
    }, email: function(value){
        errors = []
        if (! value.match(/^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/i)){
            errors.push(['please supply a valid email'])
        } return errors
    }

}

$(function(){
    $(any_password_input).on('change', function(){
        $(this).siblings('small.row').html('')
        errs = validators.password($(this).val())
        for (err in errs) {
            $(this).siblings('small.row').append(
                `<span class="text-muted col-auto" style="font-size: 0.65rem;">
                ${errs[err]}
                </span>`
            )
        }

    })


    $(email_input).on('change', function() {
        $(this).siblings('small.row').html('')
        errs = validators.email($(this).val())
        for (err in errs) {
            $(this).siblings('small.row').append(
                `<span class="text-muted col-auto" style="font-size: 0.65rem;">
                    ${errs[err]}
                </span>`
            )
        }
    }) 

    $(username_input).on('change', function() {
        $(this).siblings('small.row').html('')
        errs = validators.username($(this).val())
        for (err in errs) {
            $(this).siblings('small.row').append(
                `<span class="text-muted col-auto" style="font-size: 0.65rem;">
                ${errs[err]}
                </span>`
            )
        }
    })

    $(create_account_form).on('submit', function(event){
        let username = $(username_input).val()
            username_errors = validators.username(username)
            email = $(email_input).val()
            email_errors = validators.email(email)
            password = $(password_input).val()
            password_errors = validators.password(password)
        all_errors = []
        if (username_errors.length > 0){all_errors.push('username')}
        if (email_errors.length > 0){all_errors.push('email')}
        if (password_errors.length > 0){all_errors.push('password')}
        if (all_errors.length > 0){
            event.preventDefault()
            notify.toast(
                `errors were found in <br>${all_errors.join(' & ')}`,
                {
                    type: 'warning',
                    title: 'Please resolve the following...'
                }
            )
        } else if ($(password_input).val() != $(password_again_input).val()){
            event.preventDefault()
            notify.toast(
                'the passwords you entered do not match',
                {
                    title: 'We noticed that...',
                    type: 'error'
                }
            )
        }
    })

    $(login_account_form).on('submit', function(event){
        let
            password = $(password_input).val()
            password_errors = validators.password(password)
        if (password_errors.length > 0){
            event.preventDefault()
            notify.toast(
                `${password_errors.join(' & ')}`,
                {
                    title: 'Hey, fix up the password',
                    type: 'warning'
                }
            )
        }
    })
})