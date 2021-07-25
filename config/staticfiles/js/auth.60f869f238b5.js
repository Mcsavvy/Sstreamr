$("input#show-password").on('change', function() {
    if (Boolean($('input#show-password:checked')[0])) {
        $('input[name=password]').attr('type', 'text')
    } else {
        $('input[name=password]').attr('type', 'password')
    }
})

$("input[name=username]").on('input', function() {
    if (isNone($(this).val())) {
        $('span#username').html('guest')
    } else {
        $('span#username').html($(this).val())
    }
})

function validateUsername(username) {
    badChars = username.match('[^a-zA-Z0-9_]')
    goodChars = username.match('[a-zA-Z0-9]')
    if (username.length < 3) {
        return 'short'
    } else if (username.length > 25) {
        return 'long'
    }
    else if (badChars) {
        return 'badChars'

    } else if (!goodChars) {
        return 'goodChars'
    }
    return 'ok'
}

function validateEmail(mail) {
    if (/^[\w-\.]+@([\w-]+\.)+[\w-]{2,4}$/.test(mail)) {
        return (true)
    }
    return (false)
}

$("input[name=email]").on('change', function() {
    res = validateEmail($(this).val())
    if (!res) {
        notify.snackbar('please supply a valid email address', {
            type: 'info',
            init: false,
            interaction:false
        })
    }
    return true
})

$("input[name=username]").on('change', function() {
    res = validateUsername($(this).val())
    if (res == 'short') {
        notify.snackbar('username should be longer than two characters', {
            type: 'info',
            init: false,
            interaction:false
        })
    } else if (res == 'long') {
        notify.snackbar('username should be shorter than twenty characters', {
            type: 'info',
            init: false,
        })
    } else if (res == 'badChars') {
        notify.snackbar('username can only contain alphabets, numbers and underscores', {
            type: 'info',
            init: false,
            interaction:false
        })
    } else if (res == 'goodChars') {
        notify.snackbar('username cannot contain only underscores', {
            type: 'info',
            interaction: false,
            init: false,
        })

    } else {
        $(this).trigger('input')
    }
})

// $(".form-signup input[name='username']").on('change', function(e){
// 	if ($(this).val().length > 1){
// 		request(
// 			"GET",
// 			"/api/user/exists/" + $(this).val(),
// 			{},
// 			function(data) {
// 				if (data != null){
// 					toast(
// 						data.message,
// 						data.level,
// 						2000,
// 						$(
// 							".form-signup input[name='username']"
// 						).val(data.suggested),
// 						"topRight"
// 					)
// 				}
// 			}
// 		)
// 	}
// })
