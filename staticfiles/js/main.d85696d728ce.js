let ajx = {
    post: {
        ajax: 1,
    },
    get: {
        ajax: 1,
    }
}

function isNone(obj) {
    if ((typeof obj == typeof undefined || Boolean(obj) == false)) {
        return true
    } else {
        return false
    }

}

function argParser(arguments) {
    arguments = arguments.split('??')
    arg = arguments[0]
    args = []
    kwargs = new Object()
    if (1 in arguments) {
        kwarg = arguments[1]
    } else {
        kwarg = ""
    }
    if (arg) {
        _ = arg.split('&&')
        for (x in _) {
            args.push(_[x])
        }
    }
    if (kwarg) {
        _ = kwarg.split('&&')
        for (x in _) {
            __ = _[x].split('=')
            if (1 in __) {
                try {
                    kwargs[__[0]] = eval(__[1])
                } catch (error) {
                    kwargs[__[0]] = __[1]
                }

            } else {
                continue
            }
        }
    }
    return {
        args: args,
        kwargs: kwargs
    }

}

var main = {
    // Create cookie
    createCookie: function(name, value, days) {
        var expires;
        if (days) {
            var date = new Date();
            date.setTime(date.getTime() + (days * 24 * 60 * 60 * 1000));
            expires = "; expires=" + date.toGMTString();
        } else {
            expires = "";
        }
        document.cookie = name + "=" + value + expires + "; path=/";
    },

    // Read cookie
    readCookie: function(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                // Does this cookie string begin with the name we want?
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    },

    // Erase cookie
    eraseCookie: function(name) {
        this.createCookie(name, "", -1);
    },
}

// JavaScript wrapper function to send HTTP requests using Django's "X-CSRFToken" request header
requests = {
    get: function(path, body, callback) {
        if (isNone(body)) {
            body = new Object
        }
        body = {
            ...body,
            ...ajx.get
        }
        return $.ajax({
            url: path,
            type: "GET",
            data: body,
            success: callback
        })
    },
    post: function(path, body, callback) {
        if (isNone(body)) {
            body = new Object
        }
        body = {
            ...body,
            ...ajx.post
        }
        return $.ajax({
            url: path,
            type: "POST",
            data: body,
            headers: {
                "X-CSRFToken": main.readCookie("csrftoken")
            },
            success: callback
        })
    }
}

function xEvent(url, name, attrs) {
    return $.ajax({
        url: url,
        type: "GET",
        headers: {
            "X-Events": `${name || 'event'}??${attrs || ''}`,
            "X-Ajax": 1
        },
    })
}

function wXs() {
    console.log("extra-small")
    $('.nav-icon span.info').hide()
}

function wSm() {
    console.log("small")
    $('.nav-icon span.info').hide()
}

function wMd() {
    console.log("medium")
    $('.nav-icon span.info').hide()
}

function wLg() {
    console.log("large")
    $('.nav-icon span.info').show()
}

function wXl() {
    console.log("extra-large")
//     $('.banner-img').css("height", "7.5cm")
//     $(".url--item").css("font-size", "2rem");
//     $(".url--item").css("padding", "1.5rem")
}

function viewPort() {
    var height = $(window).height();
    var width = $(window).width();
    if (height <= 575.98) {
        // Extra small devices (portrait phones, less than 576px)
        wXs()
    } else if (height >= 576 && height <= 767.98) {
        // Small devices (landscape phones, 576px and up)
        wSm()
    } else if (height >= 768 && height <= 991.98) {
        // Medium devices (tablets, 768px and up)
        wMd()
    } else if (height >= 992 && height <= 1199.98) {
        // Large devices (desktops, 992px and up)
        wLg()
    } else if (height >= 1200) {
        // Extra large devices (large desktops, 1200px and up)
        wXl()
    }
}

/*
create two css classes to handle filtering of search
1. input--menu{
	this is the menu object containing the input objects;
	this object contains a reference to an input called "iref"
	the value of iref should be a css selector of the referencing input;
}

2. input--menu-object{
	this are input objects that when selected would have a class called
	input--menu-selected{
		this class gives the element an :after checked-input
	};
	onclick{
		if this has an attr called "ivalue"{
			the value of ivalue would be supplied to the 
			parent(".input--menu") iref
		} else {
			the .text() is supplied to the 
			parent(".input--menu:first") iref
		}
        any siblings("input--menu-object") that was previously selected
        would be unselected
	}
}

*/

$(function(){$('#fab-trigger').click(function(e){
    if ($(this).hasClass('fab-active')) {
        $(this).removeClass('fab-active');
        $('.fab-info').removeClass("fab-info-active")
        globalThis.fabActive = false
    } else {
        $(this).addClass('fab-active');
        $('.fab-info').addClass("fab-info-active")
        globalThis.fabActive = true
    }
    $(this).closest('div.floating-action-menu').toggleClass('active');
    e.stopPropagation()
})})


function getNotifications(read){
	function setHandler(){
		$('#box').slideUp()
		globalThis.notificationOpen = false;
		$('#bell').click(function(e) {
			if (notificationOpen) {
				$('#box').slideUp()
				notificationOpen = false;
			} else {
				$('#box').slideDown()
				notificationOpen = true;
			}
			event.stopPropagation()
		});
		viewPort()
	}
	if (read == 'all'){
		$('#notifications').load('/?x-ajax=1&notification&read=all', setHandler)
	} else if (typeof read == "number") {
        $('#notifications').load(`/?x-ajax=1&notification&read=${read}`, setHandler)
    } else if (typeof read == typeof undefined) {
    	$('#notifications').load(`/?x-ajax=1&notification`, setHandler)
    }
}

$(function() {
    Theme.setMode();
    //     mobileRestrict();
    $("#fab-trigger").click();
    getNotifications()
    $(document).click(()=>{
        if (notificationOpen) {
        	$('#box').slideUp()
            notificationOpen = false;
        }
    });
    $('#feeds').click(()=>{
    	if (fabActive) {
        	$('#fab-trigger').click()
        }
    })
    $(window).on("resize", function() {
        /*location.reload(true); */
        viewPort()
    });
    try {
        pushNotifications()
    } catch (e) {
        ''
    }
    viewPort();
    $('img').on('error', function() {
    	$(this).unbind("error")
    	if ($(this).attr('alt')){
    		$(this).replaceWith($(this).attr('alt'))
    	} else {
    		$(this).replaceWith("BROKEN IMAGE")
    	}
    })
})