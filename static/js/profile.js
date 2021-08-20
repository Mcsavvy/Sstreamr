let
    notifications_div = '',
    notification_item = '.notifications-item',
    xevents = {
        feeds: {
            url: '/xevent/feeds/',
            counter: '#new-feeds-count'
        },
        notifications: {
            url: '/xevent/notifications/',
        }
    }

let countNewFeeds = function(){
    xEvent(xevents.feeds.url, 'get:count')
    .then((value) => {
        all = (value.all_youtube_videos + value.all_instagram_posts) -
            (value.viewed_youtube_videos + value.viewed_instagram_posts)
        if (all > 0){
            $(xevents.feeds.counter).html(all)
        }
    })
}

let notifications = {
    getUnread: function() {
        return $('.notifications-item').not('.R')
    },
    getSent: function() {
        return $('.notifications-item.S')
    },
    readAllUnread: function() {
        ids = []
        this.getUnread().each(function() {
            ids.push($(this).data('id'))
            $(this).removeClass('S D').addClass('R')
        })
        if (ids.length > 0) {
            xEvent('/xevent/notifications/', `read??ids=[${ids}]`)
        }
    },
    readOne: function(self) {
        id = $(this).data('id')
        if (!isNone(id)) {
            xEvent('/xevent/notifications/', `read??ids=[${id}]`)
            $(this).removeClass('S D').addClass('R').off('click', this.readOne)
        }
    },
    deliverSent: function() {
        ids = []
        this.getSent().each(function() {
            ids.push($(this).data('id'))
            $(this).removeClass('S').addClass('D')
        })
        if (ids.length > 0) {
            xEvent('/xevent/notifications/', `deliver??ids=[${ids}]`)
        }
    },
    setHandlersForUnread: function() {
        this.getUnread().click(this.readOne)
    }

}

$(function() {
    setInterval(countNewFeeds, 100000)
    countNewFeeds()
    let deliver_unseen_notifications = new Promise(function(resolve, reject) {
        resolve(notifications.deliverSent())
    })
    deliver_unseen_notifications.then(()=>notifications.setHandlersForUnread())
})
