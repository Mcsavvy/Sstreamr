let 
    feeds_div = '#feeds',
    youtubes_div = '#youtube-feeds',
    instagrams_div = '#instagram-feeds',
    youtube_content_get_url = '/?x-ajax&youtube',
    instagram_content_get_url = '/?x-ajax&instagram',
    youtube_item = '.youtube-slide',
    instagram_item = '.instagram-slide',
    xevents = {
        feeds: {
            url: '/xevent/feeds/',
        },
        notifications: {
            url: '/xevent/notifications/',
            counter: '#new-notifications-count'
        }
    }

    

let feeds = {
    loadYoutube: function(slide, displayCount) {
        $(youtubes_div).load(youtube_content_get_url, function() {
            $(youtube_item).on('fotorama:loadvideo', function(e, self, extra) {
                $(youtube_item).not(this).each(function() {
                    $(this).data('fotorama').stopVideo()
                })
                console.log('## ' + e.type);
                console.log('active frame', self.activeFrame);
                console.log('additional data', extra);
            }).on('fotorama:error', function(e, self, extra) {
                console.log('## ' + e.type);
                console.log('active frame', self.activeFrame);
                console.log('additional data', extra);
            }).fotorama()
            if (slide && displayCount) {
                document.location = '#feeds'
            }
        })
    },
    loadInstagram: function(slide, displayCount) {
        $(instagrams_div).load(instagram_content_get_url, function() {
            $(instagram_item).on('fotorama:loadvideo', function(e, self, extra) {
                $(instagram_item).not(this).each(function() {
                    $(this).data('fotorama').stopVideo()
                })
                console.log('## ' + e.type);
                console.log('active frame', self.activeFrame);
                console.log('additional data', extra);
            }).on('fotorama:error', function(e, self, extra) {
                console.log('## ' + e.type);
                console.log('active frame', self.activeFrame);
                console.log('additional data', extra);
            }).fotorama()
            if (slide && displayCount) {
                document.location = '#feeds'
            }
            $('.ig-redirect-link,.ig-tag-link,.ig-profile-link').click(function(event){
                $(this).attr('target', '_blank')
                event.stopPropagation()
            })
            $('.fotorama').fotorama()
        })

    },
}

let countUnseenNotifications = function(){
    xEvent(xevents.notifications.url, 'get:count')
    .then((value) => {
        if (value > 0){
            $(xevents.notifications.counter).html(value.sent)   
        }
    })
}

$(() => {
    setInterval(countUnseenNotifications, 100000)
    countUnseenNotifications()
    feeds.loadInstagram();
    feeds.loadYoutube();
    $(feeds_div).click(() => {
        if (globalThis.fabActive){
            $('#fab-trigger').click()
        }
    })
})