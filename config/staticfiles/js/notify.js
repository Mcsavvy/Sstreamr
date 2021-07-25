notify = {
    message: function(text, options) {
        if (typeof options !== 'object'){
            options = new Object()
        }
        VanillaToasts.create({
            text: text || '',
            title: options.title || 'Sstreamr',
            icon: options.icon || '/static/img/favicon.ico',
            type: options.type || 'info',
            timeout: options.timeout || 2000,
            callback: options.callback || function(){},
            positionClass: options.position || 'topLeft'
        })
    },
    toast: function(text, options) {
        kwargs = {
            ...{
                type: 'info',
                title: 'Sstreamr Says...',
                buttonText: 'OKAY',
                confirmText: 'COOL',
                cancelText: 'NOT COOL',
                closeStyle: 'circle'
            },
            ...options
        }
        kwargs.message = text
        console.log(`toast: *(${text}), **${JSON.stringify(kwargs)}`)
        return cuteAlert(kwargs)
    },
    snackbar: function(text, options) {
        kwargs = {
            ...{
                type: 'info',
                interaction: true,
                actionText: 'UNDO',
                action: function(){
                    this.hide()
                },
                init: true,
                duration: 2000,
                modal: false,

            },
            ...options
        }
        console.log(`snackbar: *(${text}), **${JSON.stringify(kwargs)}`)
        return mdtoast(text, kwargs)
    },
    miniToast: function(text, options){
        kwargs = {
            ...{
                type: 'info',
                timer: 2000,
            },
            ...options
        }
        kwargs.message = text
        console.log(`miniToast: *(${text}), **${JSON.stringify(kwargs)}`)
        return cuteToast(kwargs)
    },
    miniToastGather: function(){}
}
