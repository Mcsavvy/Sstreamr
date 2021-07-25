Scraper = require("./youtube/Scraper");
let ajx = {
    post: {
        ajax: 1,
        type: "POST"
    },
    get: {
        ajax: 1,
        type: "GET"
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
        $.ajax({
            url: path,
            type: "GET",
            data: body,
            headers: {
                "X-CSRFToken": getCookie("csrftoken")
            },
            success: callback
        })
    },
    post: function(path, body, callback) {
        if (isNone(body)) {
            body = new Object
        }
        body = {
            ...body,
            ...ajx.get
        }
        $.ajax({
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
    $(".url--item").css("font-size", ".6rem");
    $(".url--item").css("padding", ".5rem")
}

function wSm() {
    console.log("small")
    $('.banner-img').css("height", "5cm")
    $(".url--item").css("font-size", ".6rem");
    $(".url--item").css("padding", ".68rem")
}

function wMd() {
    console.log("medium")
    $('.banner-img').css("height", "5.5cm");
    $("main").css("min-height", "15cm");
    $(".url--item").css("font-size", ".7rem");
    $(".url--item").css("padding", ".6rem")
}

function wLg() {
    console.log("large")
    $('.banner-img').css("height", "7cm")
    $(".url--item").css("font-size", "1.4rem");
    $(".url--item").css("padding", "1.2rem")
}

function wXl() {
    console.log("extra-large")
    $('.banner-img').css("height", "7.5cm")
    $(".url--item").css("font-size", "2rem");
    $(".url--item").css("padding", "1.5rem")
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

function handleFab(fab) {
    if ($(fab).hasClass('fab')) {
        $(fab).toggleClass('fab fab-active');
        $('.fab-info').addClass("fab-info-active")
    } else if ($(fab).hasClass('fab-active')) {
        $(fab).toggleClass('fab fab-active');
        $('.fab-info').removeClass("fab-info-active")
    }
    $(fab).closest('div.floating-action-menu').toggleClass('active');

}

// function handleNavMenuItemClick(self) {
//     $('.cd-side__item.cd-side__item--has-children.js-cd-item--has-children').not(self).each(function() {
//         $(this).removeClass('cd-side__item--selected')
//     })
//     $(self).addClass('cd-side__item--selected')

// }

// function handleNavMenuSubItemClick(self) {
//     $(self).siblings('.cd-side__sub-item').each(function() {
//         $(this).children('a').attr('aria-current', '')
//     })
//     $(self).children('a').attr('aria-current', 'page')

// }

// function handleNavOpenFabClose(self) {
//     if ($(self).hasClass('cd-nav-trigger--nav-is-visible')) {
//         if ($('#fab-trigger').hasClass('fab-active')) {
//             $('#fab-trigger').trigger('click')
//             $('#fab-trigger').hide()
//         }
//     } else {
//         if (!$('#fab-trigger').hasClass('fab-active')) {
//             $('#fab-trigger').show()
//             $('#fab-trigger').trigger('click')
//         }
//     }
// }

// function mobileRestrict() {
//     xEvent('/auth/xevent/', 'get:user-agent').then(function(ua) {
//     	console.log(ua.isMobile)
//         if (!ua.isMobile) {
//         	xEvent('/auth/xevent/', 'do:mobile-restrict', `location=${document.location}`).then(function(response){
//         		if ('message'in response && 'toast' in response && Boolean(response.toast)) {
// 					console.log('TRUE')
// 					arguments = argParser(response.message)
// 					notify.toast(arguments.args[0], arguments.kwargs)
// 				}
// 				if ('url'in response) {
//                     setTimeout(function(){
//                         document.location = response.url
//                     }, 5000)
					
// 				}
//         	})
            
//         }
//     })
// }

// $('.clipboard-object').each(function() {
//     var attr = $(this).attr('data-clipboard-text');
//     if (isNone(attr)) {
//         $(this).attr('data-clipboard-text', $(this).text())
//     }
// })
// clipboard = new ClipboardJS('.clipboard-object')
// clipboard.on('success', function(e) {
//     msg = $(e.trigger).attr('data-clipboard-toast')
//     if (!isNone(msg)) {
//         message(msg, "success")
//     } else {
//         message("copied to clipboard", "success")
//     }
// });
// clipboard.on('error', function() {
//     message("could not copy to clipboard. try again", "error")
// })

$(function() {
    Theme.setMode();
//     mobileRestrict();
    $("#fab-trigger").trigger("click");
    $(window).on("resize", function() {
        /*location.reload(true); */
        viewPort()
    });
    try{
        pushNotifications();
    }
    catch (e){
        ''
    }
       
    viewPort();
    $('img').each(function() {
        this.onerror = function() {
            $(this).replaceWith($(this).attr("alt") || "BROKEN IMAGE")
        }
        ;
    });
    // $('.cd-side__item.cd-side__item--has-children.js-cd-item--has-children').click(function() {
    //     handleNavMenuItemClick(this)
    // })
    // $('.cd-side__sub-item').click(function() {
    //     handleNavMenuSubItemClick(this)
    // })
    // $('.cd-nav-trigger.js-cd-nav-trigger').click(function() {
    //     handleNavOpenFabClose(this)
    // })
})
