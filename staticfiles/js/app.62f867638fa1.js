feeds = {
    youtube: function(slide, displayCount) {
        $('#youtube-feeds').load(`/?x-ajax&youtube&s=${slide || 1}&c=${displayCount || 20}`, function(){
            $('.youtube-slide').on('fotorama:loadvideo', function(e, self, extra) {
                $('.youtube-slide').not(this).each(function(){
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
            if (slide && displayCount){
                document.location = '#feeds'
            }
        })
    },
    instagram: function(slide, displayCount){
        $('#instagram-feeds').load(`/?x-ajax&instagram&s=${slide || 1}&c=${displayCount || 20}`, function(){
            $('.instagram-slide').on('fotorama:loadvideo', function(e, self, extra) {
                $('.instagram-slide').not(this).each(function(){
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
            if (slide && displayCount){
                document.location = '#feeds'
            }
            $('.fotorama').fotorama()
        })

    }
}

$(function() {
    feeds.instagram()
    feeds.youtube()
})

$(function(){$('[data-toggle="tooltip"]').tooltip('show')})
