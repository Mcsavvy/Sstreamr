function link_account(type){
    if (type == 'ig'){
        notify.toast(
            `
            view trends straight from instagram...
            You just need to supply your username below
            <input type=text class='social-input' placeholder='your username...'>
            `,
            {
                'type': 'question',
                'title': 'Instagram??'
            }
        )
    }
}